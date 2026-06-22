from django.test import TestCase, Client  # noqa: F401
from django.urls import reverse
from accounts.models import User
from contacts.models import EmergencyContact


class EmergencyContactModelTest(TestCase):
    """Test EmergencyContact model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.contact = EmergencyContact.objects.create(
            user=self.user,
            name='Jane Doe',
            phone='9876543210',
            email='jane@example.com',
            relationship='Sister',
            is_primary=True
        )

    def test_contact_created(self):
        self.assertEqual(self.contact.name, 'Jane Doe')
        self.assertEqual(self.contact.phone, '9876543210')
        self.assertTrue(self.contact.is_primary)

    def test_contact_str(self):
        self.assertIn('Jane Doe', str(self.contact))

    def test_only_one_primary_contact(self):
        """Saving a second primary contact should demote the first one"""
        second = EmergencyContact.objects.create(
            user=self.user,
            name='John Doe',
            phone='9876543211',
            email='john@example.com',
            is_primary=True
        )
        # Refresh first contact from DB
        self.contact.refresh_from_db()
        self.assertFalse(self.contact.is_primary)
        self.assertTrue(second.is_primary)

    def test_multiple_contacts_allowed(self):
        for i in range(4):
            EmergencyContact.objects.create(
                user=self.user,
                name=f'Contact {i}',
                phone=f'987654321{i}',
            )
        self.assertEqual(
            EmergencyContact.objects.filter(user=self.user).count(), 5
        )


class ContactViewTest(TestCase):
    """Test contact CRUD views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_contact_list_loads(self):
        response = self.client.get(reverse('contacts:list'))
        self.assertEqual(response.status_code, 200)

    def test_contact_add_page_loads(self):
        response = self.client.get(reverse('contacts:add'))
        self.assertEqual(response.status_code, 200)

    def test_add_contact(self):
        response = self.client.post(reverse('contacts:add'), {
            'name': 'Jane Doe',
            'phone': '9876543210',
            'email': 'jane@example.com',
            'relationship': 'Sister',
            'is_primary': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EmergencyContact.objects.filter(user=self.user).count(), 1
        )

    def test_cannot_add_more_than_5_contacts(self):
        for i in range(5):
            EmergencyContact.objects.create(
                user=self.user,
                name=f'Contact {i}',
                phone=f'987654321{i}',
            )
        response = self.client.post(reverse('contacts:add'), {
            'name': 'Extra Contact',
            'phone': '9999999999',
        })
        # Should redirect with warning, not create 6th contact
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EmergencyContact.objects.filter(user=self.user).count(), 5
        )

    def test_edit_contact(self):
        contact = EmergencyContact.objects.create(
            user=self.user, name='Old Name', phone='9876543210'
        )
        response = self.client.post(
            reverse('contacts:edit', args=[contact.pk]),
            {'name': 'New Name', 'phone': '9876543210'}
        )
        self.assertEqual(response.status_code, 302)
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'New Name')

    def test_delete_contact(self):
        contact = EmergencyContact.objects.create(
            user=self.user, name='To Delete', phone='9876543210'
        )
        response = self.client.post(
            reverse('contacts:delete', args=[contact.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            EmergencyContact.objects.filter(pk=contact.pk).exists()
        )

    def test_contact_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('contacts:list'))
        self.assertEqual(response.status_code, 302)

    def test_cannot_edit_other_users_contact(self):
        other_user = User.objects.create_user(
            username='otheruser', password='pass123'
        )
        contact = EmergencyContact.objects.create(
            user=other_user, name='Other Contact', phone='9876543210'
        )
        response = self.client.post(
            reverse('contacts:edit', args=[contact.pk]),
            {'name': 'Hacked', 'phone': '9876543210'}
        )
        self.assertEqual(response.status_code, 404)
