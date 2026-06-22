from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from alerts.models import SOSAlert
from contacts.models import EmergencyContact


class DashboardViewTest(TestCase):
    """Test dashboard views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            first_name='Test', role='user'
        )
        self.admin = User.objects.create_user(
            username='adminuser', password='testpass123',
            first_name='Admin', role='admin'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_for_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_alert_count(self):
        self.client.login(username='testuser', password='testpass123')
        SOSAlert.objects.create(user=self.user)
        SOSAlert.objects.create(user=self.user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.context['total_alerts'], 2)

    def test_dashboard_shows_contact_count(self):
        self.client.login(username='testuser', password='testpass123')
        EmergencyContact.objects.create(
            user=self.user, name='Contact 1', phone='9876543210'
        )
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.context['contacts_count'], 1)

    def test_dashboard_shows_active_alert_banner(self):
        self.client.login(username='testuser', password='testpass123')
        SOSAlert.objects.create(user=self.user, status='active')
        response = self.client.get(reverse('dashboard:home'))
        self.assertIsNotNone(response.context['active_alert'])

    def test_admin_panel_accessible_for_admin(self):
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 200)

    def test_admin_panel_forbidden_for_regular_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 403)

    def test_admin_panel_accessible_for_ngo(self):
        User.objects.create_user(
            username='ngouser', password='testpass123', role='ngo'
        )
        self.client.login(username='ngouser', password='testpass123')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 200)

    def test_admin_panel_shows_all_alerts(self):
        self.client.login(username='adminuser', password='testpass123')
        SOSAlert.objects.create(user=self.user, status='active')
        SOSAlert.objects.create(user=self.user, status='resolved')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.context['total_alerts'], 2)
