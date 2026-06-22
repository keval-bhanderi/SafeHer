import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from alerts.models import SOSAlert


class SOSAlertModelTest(TestCase):
    """Test SOSAlert model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            phone='9876543210'
        )

    def test_alert_created(self):
        alert = SOSAlert.objects.create(
            user=self.user,
            latitude=23.0225,
            longitude=72.5714,
            status='active'
        )
        self.assertEqual(alert.status, 'active')
        self.assertTrue(alert.is_active)

    def test_alert_default_status_is_active(self):
        alert = SOSAlert.objects.create(user=self.user)
        self.assertEqual(alert.status, 'active')

    def test_alert_str(self):
        alert = SOSAlert.objects.create(user=self.user)
        self.assertIn('testuser', str(alert))

    def test_alert_resolve(self):
        alert = SOSAlert.objects.create(user=self.user, status='active')
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')
        self.assertIsNotNone(alert.resolved_at)
        self.assertFalse(alert.is_active)

    def test_alert_uuid_primary_key(self):
        alert = SOSAlert.objects.create(user=self.user)
        self.assertIsNotNone(alert.id)
        self.assertEqual(len(str(alert.id)), 36)  # UUID format


class SOSAlertViewTest(TestCase):
    """Test SOS alert views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            phone='9876543210', email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_trigger_sos_get_redirects(self):
        response = self.client.get(reverse('alerts:trigger'))
        self.assertEqual(response.status_code, 302)

    def test_trigger_sos_post_creates_alert(self):
        response = self.client.post(
            reverse('alerts:trigger'),
            data=json.dumps({
                'latitude': 23.0225,
                'longitude': 72.5714,
                'address': 'Surat, Gujarat'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(SOSAlert.objects.filter(user=self.user).count(), 1)

    def test_trigger_sos_without_location(self):
        """SOS should still work even without GPS coordinates"""
        response = self.client.post(
            reverse('alerts:trigger'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_alert_history_loads(self):
        response = self.client.get(reverse('alerts:history'))
        self.assertEqual(response.status_code, 200)

    def test_alert_history_shows_user_alerts_only(self):
        other_user = User.objects.create_user(
            username='otheruser', password='pass123'
        )
        SOSAlert.objects.create(user=self.user)
        SOSAlert.objects.create(user=other_user)
        response = self.client.get(reverse('alerts:history'))
        self.assertEqual(response.status_code, 200)
        # Only current user's alerts should appear
        self.assertEqual(
            SOSAlert.objects.filter(user=self.user).count(), 1
        )

    def test_resolve_own_alert(self):
        alert = SOSAlert.objects.create(user=self.user, status='active')
        response = self.client.post(
            reverse('alerts:resolve', args=[alert.id])
        )
        self.assertEqual(response.status_code, 302)
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')

    def test_resolve_other_users_alert_returns_404(self):
        other_user = User.objects.create_user(
            username='otheruser', password='pass123'
        )
        alert = SOSAlert.objects.create(user=other_user, status='active')
        response = self.client.post(
            reverse('alerts:resolve', args=[alert.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_can_resolve_any_alert(self):
        User.objects.create_user(
            username='adminuser', password='pass123', role='admin'
        )  # noqa: F841
        self.client.login(username='adminuser', password='pass123')
        alert = SOSAlert.objects.create(user=self.user, status='active')
        response = self.client.post(
            reverse('alerts:resolve', args=[alert.id])
        )
        self.assertEqual(response.status_code, 302)
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')

    def test_alert_history_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('alerts:history'))
        self.assertEqual(response.status_code, 302)

    def test_trigger_sos_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse('alerts:trigger'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertNotEqual(response.status_code, 200)
