from django.urls import path
from . import views

app_name = 'demo_data'

urlpatterns = [
    path('', views.demo_management_view, name='management'),
    path('showcase/', views.recruiter_showcase, name='recruiter_showcase'),
    path('completion/', views.demo_completion_summary, name='completion_summary'),
    path('load/', views.load_demo_data, name='load'),
    path('clear/', views.clear_demo_data, name='clear'),
    path('status/', views.demo_status, name='status'),
    path('api/status/', views.api_demo_status, name='api_demo_status'),
    path('api/load-scenario/', views.api_load_scenario, name='api_load_scenario'),
    path('api/clear-data/', views.api_clear_data, name='api_clear_data'),
]
