from django.test import TestCase, Client  # noqa: F401
from django.urls import reverse
from accounts.models import User
from helpline.models import Helpline


class HelplineModelTest(TestCase):
    """Test Helpline model"""

    def setUp(self):
        self.helpline = Helpline.objects.create(
            name='Women Helpline',
            number='1091',
            category='women',
            description='National women helpline',
            available_24x7=True,
            is_active=True
        )

    def test_helpline_created(self):
        self.assertEqual(self.helpline.name, 'Women Helpline')
        self.assertEqual(self.helpline.number, '1091')
        self.assertTrue(self.helpline.available_24x7)

    def test_helpline_str(self):
        self.assertIn('Women Helpline', str(self.helpline))
        self.assertIn('1091', str(self.helpline))

    def test_inactive_helpline(self):
        self.helpline.is_active = False
        self.helpline.save()
        self.assertFalse(self.helpline.is_active)


class HelplineViewTest(TestCase):
    """Test helpline list view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        Helpline.objects.create(
            name='Women Helpline', number='1091',
            category='women', is_active=True
        )
        Helpline.objects.create(
            name='Police', number='100',
            category='police', is_active=True
        )
        Helpline.objects.create(
            name='Inactive Line', number='0000',
            category='other', is_active=False
        )

    def test_helpline_list_loads(self):
        response = self.client.get(reverse('helpline:list'))
        self.assertEqual(response.status_code, 200)

    def test_helpline_list_shows_active_only(self):
        response = self.client.get(reverse('helpline:list'))
        self.assertNotContains(response, 'Inactive Line')

    def test_filter_by_category(self):
        response = self.client.get(
            reverse('helpline:list') + '?category=women'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1091')
        self.assertNotContains(response, 'tel:100')

    def test_helpline_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('helpline:list'))
        self.assertEqual(response.status_code, 302)
