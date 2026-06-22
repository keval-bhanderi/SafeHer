from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.ProfileAPIView.as_view(), name='profile'),
    # Contacts
    path('contacts/', views.ContactListCreateAPIView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', views.ContactDetailAPIView.as_view(), name='contact_detail'),
    # Alerts
    path('alerts/trigger/', views.TriggerSOSAPIView.as_view(), name='sos_trigger'),
    path('alerts/history/', views.AlertHistoryAPIView.as_view(), name='alert_history'),
    path('alerts/<uuid:pk>/resolve/', views.ResolveAlertAPIView.as_view(), name='alert_resolve'),
    path('alerts/<uuid:pk>/location/', views.UpdateLocationAPIView.as_view(), name='update_location'),
    # Resources
    path('nearby/', views.NearbyResourceAPIView.as_view(), name='nearby'),
    path('helplines/', views.HelplineAPIView.as_view(), name='helplines'),
]
