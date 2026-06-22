from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('trigger/', views.sos_trigger, name='trigger'),
    path('<uuid:pk>/', views.alert_detail, name='detail'),
    path('<uuid:pk>/resolve/', views.alert_resolve, name='resolve'),
    path('<uuid:pk>/location/', views.update_location, name='update_location'),
    path('history/', views.alert_history, name='history'),
]
