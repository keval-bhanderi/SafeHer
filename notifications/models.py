from django.db import models

class NotificationLog(models.Model):
    METHOD_CHOICES = [('email', 'Email'), ('sms', 'SMS')]
    STATUS_CHOICES = [('sent', 'Sent'), ('failed', 'Failed'), ('pending', 'Pending')]

    alert = models.ForeignKey('alerts.SOSAlert', on_delete=models.CASCADE, related_name='notifications')
    contact = models.ForeignKey('contacts.EmergencyContact', on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.method.upper()} to {self.contact.name} - {self.status}"
