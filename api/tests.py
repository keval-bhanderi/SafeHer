from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from alerts.models import SOSAlert
from contacts.models import EmergencyContact
from nearby.models import NearbyResource
from helpline.models import Helpline


class APIAuthTest(TestCase):
    """Test API authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            phone='9876543210',
            city='Surat'
        )

    def test_register_api(self):
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '9876543211',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'password': 'strongpass123!',
            'password2': 'strongpass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_register_password_mismatch(self):
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser2',
            'password': 'pass123',
            'password2': 'different',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_profile_api_unauthenticated(self):
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/v1/auth/profile/', {
            'city': 'Mumbai'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, 'Mumbai')


class APIContactTest(TestCase):
    """Test API contact endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_contacts_empty(self):
        response = self.client.get('/api/v1/contacts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_contact(self):
        response = self.client.post('/api/v1/contacts/', {
            'name': 'Jane Doe',
            'phone': '9876543210',
            'email': 'jane@example.com',
            'relationship': 'Sister',
            'is_primary': True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Jane Doe')

    def test_list_contacts_returns_own_only(self):
        other_user = User.objects.create_user(
            username='other', password='pass123'
        )
        EmergencyContact.objects.create(
            user=self.user, name='My Contact', phone='9876543210'
        )
        EmergencyContact.objects.create(
            user=other_user, name='Other Contact', phone='9876543211'
        )
        response = self.client.get('/api/v1/contacts/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'My Contact')

    def test_cannot_add_more_than_5_contacts_api(self):
        for i in range(5):
            EmergencyContact.objects.create(
                user=self.user,
                name=f'Contact {i}',
                phone=f'987654321{i}'
            )
        response = self.client.post('/api/v1/contacts/', {
            'name': 'Extra', 'phone': '9999999999'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_contact_api(self):
        contact = EmergencyContact.objects.create(
            user=self.user, name='To Delete', phone='9876543210'
        )
        response = self.client.delete(f'/api/v1/contacts/{contact.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            EmergencyContact.objects.filter(pk=contact.pk).exists()
        )


class APIAlertTest(TestCase):
    """Test SOS alert API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            phone='9876543210'
        )
        self.client.force_authenticate(user=self.user)

    def test_trigger_sos_api(self):
        response = self.client.post('/api/v1/alerts/trigger/', {
            'latitude': 23.0225,
            'longitude': 72.5714,
            'message': 'Need help!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('alert', response.data)

    def test_trigger_sos_creates_db_record(self):
        self.client.post('/api/v1/alerts/trigger/', {
            'latitude': 23.0225,
            'longitude': 72.5714
        }, format='json')
        self.assertEqual(
            SOSAlert.objects.filter(user=self.user).count(), 1
        )

    def test_alert_history_api(self):
        SOSAlert.objects.create(user=self.user, status='active')
        SOSAlert.objects.create(user=self.user, status='resolved')
        response = self.client.get('/api/v1/alerts/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_resolve_alert_api(self):
        alert = SOSAlert.objects.create(user=self.user, status='active')
        response = self.client.post(f'/api/v1/alerts/{alert.id}/resolve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')

    def test_resolve_nonexistent_alert(self):
        import uuid
        response = self.client.post(
            f'/api/v1/alerts/{uuid.uuid4()}/resolve/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_location_api(self):
        alert = SOSAlert.objects.create(user=self.user, status='active')
        response = self.client.post(
            f'/api/v1/alerts/{alert.id}/location/',
            {'latitude': 23.0300, 'longitude': 72.5800},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertAlmostEqual(float(alert.latitude), 23.03, places=1)

    def test_trigger_sos_unauthenticated(self):
        self.client.logout()
        response = self.client.post('/api/v1/alerts/trigger/', {
            'latitude': 23.0225, 'longitude': 72.5714
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APINearbyTest(TestCase):
    """Test nearby resources API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        NearbyResource.objects.create(
            name='Surat Police', type='police',
            city='Surat', state='Gujarat',
            latitude=21.1702, longitude=72.8311, is_active=True
        )
        NearbyResource.objects.create(
            name='Mumbai NGO', type='ngo',
            city='Mumbai', state='Maharashtra',
            latitude=19.0760, longitude=72.8777, is_active=True
        )

    def test_nearby_list_api(self):
        response = self.client.get('/api/v1/nearby/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_type(self):
        response = self.client.get('/api/v1/nearby/?type=police')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Surat Police')

    def test_filter_by_city(self):
        response = self.client.get('/api/v1/nearby/?city=Mumbai')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Mumbai NGO')

    def test_nearby_unauthenticated(self):
        self.client.logout()
        response = self.client.get('/api/v1/nearby/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIHelplineTest(TestCase):
    """Test helplines API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        Helpline.objects.create(
            name='Women Helpline', number='1091',
            category='women', is_active=True
        )
        Helpline.objects.create(
            name='Police', number='100',
            category='police', is_active=True
        )

    def test_helplines_list_api(self):
        response = self.client.get('/api/v1/helplines/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_helplines_by_category(self):
        response = self.client.get('/api/v1/helplines/?category=women')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['number'], '1091')

    def test_helplines_unauthenticated(self):
        self.client.logout()
        response = self.client.get('/api/v1/helplines/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
