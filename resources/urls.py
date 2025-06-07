from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    path('create/', views.resource_create, name='resource_create'),
    path('<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('skills/create/', views.create_skill, name='create_skill'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
    
    # Time tracking URLs
    path('time-entries/', views.time_entry_list, name='time_entry_list'),
    path('time-entries/create/', views.time_entry_create, name='time_entry_create'),
    path('time-entries/<int:pk>/edit/', views.time_entry_edit, name='time_entry_edit'),
    path('time-entries/bulk/', views.bulk_time_entry, name='bulk_time_entry'),
    
    # Availability URLs
    path('availability/', views.availability_calendar, name='availability_calendar'),
    path('availability/create/', views.availability_create, name='availability_create'),
    path('availability/<int:pk>/edit/', views.availability_edit, name='availability_edit'),
    
    # Reports
    path('<int:pk>/time-report/', views.resource_time_tracking_report, name='resource_time_report'),
]