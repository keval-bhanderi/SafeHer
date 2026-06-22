from django.test import TestCase, Client  # noqa: F401
from django.urls import reverse
from accounts.models import User


class UserModelTest(TestCase):
    """Test custom User model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='9876543210',
            city='Surat',
            state='Gujarat',
            role='user'
        )

    def test_user_created_successfully(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'user')

    def test_user_str(self):
        self.assertIn('testuser', str(self.user))

    def test_default_role_is_user(self):
        new_user = User.objects.create_user(
            username='newuser', password='pass123'
        )
        self.assertEqual(new_user.role, 'user')

    def test_admin_role(self):
        admin = User.objects.create_user(
            username='admin2', password='pass123', role='admin'
        )
        self.assertEqual(admin.role, 'admin')

    def test_ngo_role(self):
        ngo = User.objects.create_user(
            username='ngouser', password='pass123', role='ngo'
        )
        self.assertEqual(ngo.role, 'ngo')


class AuthViewTest(TestCase):
    """Test authentication views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            email='test@example.com'
        )

    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SafeHer')

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_new_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '9876543211',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'password1': 'strongpass123!',
            'password2': 'strongpass123!',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_login_valid_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertNotEqual(response.status_code, 200)

    def test_profile_accessible_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
