from django.urls import path
from . import views

app_name = 'helpline'

urlpatterns = [
    path('', views.helpline_list, name='list'),
]
