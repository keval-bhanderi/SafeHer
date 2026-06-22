from django.test import TestCase
from unittest.mock import patch, MagicMock
from accounts.models import User
from alerts.models import SOSAlert
from contacts.models import EmergencyContact
from notifications.models import NotificationLog
from notifications.utils import send_sos_email, send_sos_sms, send_sos_notifications


class NotificationModelTest(TestCase):
    """Test NotificationLog model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            phone='9876543210'
        )
        self.alert = SOSAlert.objects.create(
            user=self.user,
            latitude=23.0225,
            longitude=72.5714
        )
        self.contact = EmergencyContact.objects.create(
            user=self.user,
            name='Jane',
            phone='9876543211',
            email='jane@example.com'
        )

    def test_notification_log_created(self):
        log = NotificationLog.objects.create(
            alert=self.alert,
            contact=self.contact,
            method='email',
            status='sent'
        )
        self.assertEqual(log.method, 'email')
        self.assertEqual(log.status, 'sent')

    def test_notification_log_str(self):
        log = NotificationLog.objects.create(
            alert=self.alert,
            contact=self.contact,
            method='sms',
            status='failed'
        )
        self.assertIn('sms', str(log).lower())


class EmailNotificationTest(TestCase):
    """Test email sending utility"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            first_name='Test', last_name='User',
            phone='9876543210', email='test@example.com'
        )
        self.alert = SOSAlert.objects.create(
            user=self.user,
            latitude=23.0225,
            longitude=72.5714
        )
        self.contact = EmergencyContact.objects.create(
            user=self.user,
            name='Jane',
            phone='9876543211',
            email='jane@example.com'
        )

    @patch('notifications.utils.send_mail')
    def test_email_sent_successfully(self, mock_send_mail):
        mock_send_mail.return_value = 1
        result = send_sos_email(self.contact, self.alert)
        self.assertTrue(result)
        mock_send_mail.assert_called_once()

    @patch('notifications.utils.send_mail')
    def test_email_contains_user_name(self, mock_send_mail):
        mock_send_mail.return_value = 1
        send_sos_email(self.contact, self.alert)
        call_args = mock_send_mail.call_args
        # Subject should contain user's name
        subject = call_args[0][0]
        self.assertIn('Test', subject)

    @patch('notifications.utils.send_mail')
    def test_email_contains_map_link(self, mock_send_mail):
        mock_send_mail.return_value = 1
        send_sos_email(self.contact, self.alert)
        call_args = mock_send_mail.call_args
        message = call_args[0][1]
        self.assertIn('google.com/maps', message)

    @patch('notifications.utils.send_mail')
    def test_email_failure_returns_false(self, mock_send_mail):
        mock_send_mail.side_effect = Exception('SMTP Error')
        result = send_sos_email(self.contact, self.alert)
        self.assertFalse(result)

    @patch('notifications.utils.send_mail')
    def test_email_without_location_still_sends(self, mock_send_mail):
        mock_send_mail.return_value = 1
        alert_no_location = SOSAlert.objects.create(user=self.user)
        result = send_sos_email(self.contact, alert_no_location)
        self.assertTrue(result)


class SMSNotificationTest(TestCase):
    """Test SMS sending utility"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            first_name='Test', phone='9876543210'
        )
        self.alert = SOSAlert.objects.create(
            user=self.user,
            latitude=23.0225, longitude=72.5714
        )
        self.contact = EmergencyContact.objects.create(
            user=self.user,
            name='Jane', phone='9876543211',
            email='jane@example.com'
        )

    def test_sms_mock_mode_returns_true(self):
        """SMS should succeed in mock mode (placeholder API key)"""
        result = send_sos_sms(self.contact, self.alert)
        self.assertTrue(result)

    @patch('notifications.utils.urllib.request.urlopen')
    def test_sms_api_called_with_real_key(self, mock_urlopen):
        from django.conf import settings
        original_key = settings.FAST2SMS_API_KEY
        settings.FAST2SMS_API_KEY = 'real-test-api-key'

        mock_response = MagicMock()
        mock_response.read.return_value = b'{"return": true}'
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = send_sos_sms(self.contact, self.alert)
        self.assertTrue(result)
        settings.FAST2SMS_API_KEY = original_key


class SendSOSNotificationsTest(TestCase):
    """Test the main notification dispatcher"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            first_name='Test', phone='9876543210'
        )
        self.alert = SOSAlert.objects.create(user=self.user)

    @patch('notifications.utils.send_mail')
    def test_logs_created_for_each_contact(self, mock_send_mail):
        mock_send_mail.return_value = 1
        for i in range(3):
            EmergencyContact.objects.create(
                user=self.user,
                name=f'Contact {i}',
                phone=f'987654321{i}',
                email=f'contact{i}@example.com'
            )
        contacts = EmergencyContact.objects.filter(user=self.user)
        send_sos_notifications(self.alert, contacts)
        # 3 contacts × (1 email + 1 SMS attempt) = 6 logs
        self.assertEqual(
            NotificationLog.objects.filter(alert=self.alert).count(), 6
        )

    @patch('notifications.utils.send_mail')
    def test_contact_without_email_skips_email(self, mock_send_mail):
        mock_send_mail.return_value = 1
        EmergencyContact.objects.create(
            user=self.user,
            name='No Email',
            phone='9876543299',
            email=''
        )
        contacts = EmergencyContact.objects.filter(user=self.user)
        send_sos_notifications(self.alert, contacts)
        mock_send_mail.assert_not_called()

    @patch('notifications.utils.send_mail')
    def test_no_contacts_no_notifications(self, mock_send_mail):
        send_sos_notifications(self.alert, [])
        mock_send_mail.assert_not_called()
        self.assertEqual(
            NotificationLog.objects.filter(alert=self.alert).count(), 0
        )
