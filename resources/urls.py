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
    path('time-tracking/', views.time_entry_list, name='time_tracking'),
    path('time-entries/', views.time_entry_list, name='time_entry_list'),    path('time-entries/create/', views.time_entry_create, name='time_entry_create'),
    path('time-entries/<int:pk>/edit/', views.time_entry_edit, name='time_entry_edit'),
    path('time-entries/<int:pk>/delete/', views.time_entry_delete, name='time_entry_delete'),
    path('time-entries/<int:pk>/toggle-billable/', views.toggle_time_entry_billable, name='toggle_time_entry_billable'),
    path('time-entries/bulk/', views.bulk_time_entry, name='bulk_time_entry'),
    path('time-entries/bulk-action/', views.bulk_time_action, name='bulk_time_action'),
    path('time-entries/export/', views.export_time_entries, name='export_time_entries'),
    
    # Availability URLs
    path('availability/', views.availability_calendar, name='availability_calendar'),
    path('availability/create/', views.availability_create, name='availability_create'),
    path('availability/<int:pk>/edit/', views.availability_edit, name='availability_edit'),
    
    # Reports
    path('<int:pk>/time-report/', views.resource_time_tracking_report, name='resource_time_report'),
]