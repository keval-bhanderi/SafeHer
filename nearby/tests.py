from django.test import TestCase, Client  # noqa: F401
from django.urls import reverse
from accounts.models import User
from nearby.models import NearbyResource
from nearby.views import haversine


class NearbyResourceModelTest(TestCase):
    """Test NearbyResource model"""

    def setUp(self):
        self.resource = NearbyResource.objects.create(
            name='Surat Police Station',
            type='police',
            phone='0261-2222222',
            city='Surat',
            state='Gujarat',
            latitude=21.1702,
            longitude=72.8311,
            is_active=True
        )

    def test_resource_created(self):
        self.assertEqual(self.resource.name, 'Surat Police Station')
        self.assertEqual(self.resource.type, 'police')

    def test_resource_str(self):
        self.assertIn('Surat Police Station', str(self.resource))

    def test_inactive_resource(self):
        self.resource.is_active = False
        self.resource.save()
        self.assertFalse(self.resource.is_active)


class HaversineTest(TestCase):
    """Test distance calculation"""

    def test_same_location_is_zero(self):
        dist = haversine(23.0225, 72.5714, 23.0225, 72.5714)
        self.assertAlmostEqual(dist, 0.0, places=2)

    def test_known_distance(self):
        # Surat to Mumbai is approx 270km
        dist = haversine(21.1702, 72.8311, 19.0760, 72.8777)
        self.assertGreater(dist, 200)
        self.assertLess(dist, 350)

    def test_distance_is_positive(self):
        dist = haversine(23.0225, 72.5714, 21.1702, 72.8311)
        self.assertGreater(dist, 0)


class NearbyViewTest(TestCase):
    """Test nearby resources view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            city='Surat'
        )
        self.client.login(username='testuser', password='testpass123')
        NearbyResource.objects.create(
            name='Surat Police', type='police',
            city='Surat', state='Gujarat',
            latitude=21.1702, longitude=72.8311, is_active=True
        )
        NearbyResource.objects.create(
            name='Surat NGO', type='ngo',
            city='Surat', state='Gujarat',
            latitude=21.1802, longitude=72.8411, is_active=True
        )

    def test_nearby_list_loads(self):
        response = self.client.get(reverse('nearby:list'))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_type(self):
        response = self.client.get(reverse('nearby:list') + '?type=police')
        self.assertEqual(response.status_code, 200)

    def test_filter_by_city(self):
        response = self.client.get(reverse('nearby:list') + '?city=Surat')
        self.assertEqual(response.status_code, 200)

    def test_nearby_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('nearby:list'))
        self.assertEqual(response.status_code, 302)

    def test_inactive_resources_not_shown(self):
        NearbyResource.objects.create(
            name='Inactive Station', type='police',
            city='Surat', state='Gujarat', is_active=False
        )
        response = self.client.get(reverse('nearby:list') + '?city=Surat')
        self.assertNotContains(response, 'Inactive Station')
