from django.contrib import admin
from .models import EmergencyContact

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'phone', 'relationship', 'is_primary']
