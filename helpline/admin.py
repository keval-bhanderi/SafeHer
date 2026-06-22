from django.contrib import admin
from .models import Helpline

@admin.register(Helpline)
class HelplineAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'category', 'available_24x7', 'is_active']
    list_filter = ['category', 'available_24x7', 'is_active']
