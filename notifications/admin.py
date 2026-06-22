from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'contact', 'method', 'status', 'sent_at']
    list_filter = ['method', 'status']
