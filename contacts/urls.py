from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contact_list, name='list'),
    path('add/', views.contact_add, name='add'),
    path('<int:pk>/edit/', views.contact_edit, name='edit'),
    path('<int:pk>/delete/', views.contact_delete, name='delete'),
]
