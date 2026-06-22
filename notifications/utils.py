from django.core.mail import send_mail
from django.conf import settings
import urllib.request
import urllib.parse
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)

def send_sos_email(contact, alert):
    """Send SOS email to emergency contact."""
    user = alert.user
    maps_link = ""
    if alert.latitude and alert.longitude:
        maps_link = f"https://www.google.com/maps?q={alert.latitude},{alert.longitude}"

    subject = f"🚨 URGENT: SOS Alert from {user.first_name} {user.last_name}"
    message = f"""
EMERGENCY ALERT - IMMEDIATE ATTENTION REQUIRED

{user.first_name} {user.last_name} has triggered an SOS alert!

Details:
- Name: {user.first_name} {user.last_name}
- Phone: {user.phone}
- Time: {alert.triggered_at.strftime('%d %B %Y, %I:%M %p')}
- Location: {alert.address or 'See map link below'}
{f'- Map: {maps_link}' if maps_link else ''}
{f'- Message: {alert.message}' if alert.message else ''}

Please contact them immediately or call emergency services (100/112) if you cannot reach them.

This alert was sent automatically by SafeHer Safety App.
"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [contact.email], fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Email failed to {contact.email}: {e}")
        return False

def send_sos_sms(contact, alert):
    """Send SOS SMS via Fast2SMS (India)."""
    user = alert.user
    maps_link = ""
    if alert.latitude and alert.longitude:
        maps_link = f"maps.google.com/?q={alert.latitude},{alert.longitude}"

    message = (
        f"URGENT SOS! {user.first_name} {user.last_name} needs help! "
        f"Phone: {user.phone}. "
        f"{f'Location: {maps_link}' if maps_link else ''} "
        f"Please respond immediately! -SafeHer"
    )
    try:
        api_key = settings.FAST2SMS_API_KEY
        if api_key == 'your-fast2sms-api-key':
            logger.info(f"[SMS MOCK] To: {contact.phone} | Message: {message}")
            return True
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": contact.phone.replace('+91', '').replace(' ', '').replace('-', ''),
        }
        headers = {'authorization': api_key, 'Content-Type': 'application/json'}
        req = urllib.request.Request(url, json.dumps(payload).encode(), headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            return result.get('return', False)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        logger.error(f"SMS failed to {contact.phone}: HTTP {e.code} - {error_body}")
        return False
    except Exception as e:
        logger.error(f"SMS failed to {contact.phone}: {e}")
        return False

def send_sos_notifications(alert, contacts):
    """Send all SOS notifications to all emergency contacts."""
    from .models import NotificationLog
    for contact in contacts:
        # Send email
        if contact.email:
            success = send_sos_email(contact, alert)
            NotificationLog.objects.create(
                alert=alert, contact=contact,
                method='email', status='sent' if success else 'failed'
            )
        # Send SMS
        if contact.phone:
            success = send_sos_sms(contact, alert)
            NotificationLog.objects.create(
                alert=alert, contact=contact,
                method='sms', status='sent' if success else 'failed'
            )