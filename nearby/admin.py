from django.contrib import admin
from .models import NearbyResource

@admin.register(NearbyResource)
class NearbyResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'city', 'phone', 'is_active']
    list_filter = ['type', 'city', 'is_active']
