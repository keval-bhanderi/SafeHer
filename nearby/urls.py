from django.urls import path
from . import views

app_name = 'nearby'

urlpatterns = [
    path('', views.nearby_list, name='list'),
]
