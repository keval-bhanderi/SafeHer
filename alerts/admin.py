from django.contrib import admin
from .models import SOSAlert

@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'triggered_at', 'latitude', 'longitude']
    list_filter = ['status']
    ordering = ['-triggered_at']
