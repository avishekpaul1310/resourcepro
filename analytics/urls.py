from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('forecast/generate/', views.generate_forecast, name='generate_forecast'),
    path('skills/analyze/', views.analyze_skills, name='analyze_skills'),
    path('utilization/', views.utilization_report, name='utilization_report'),
    path('costs/', views.cost_tracking_report, name='cost_tracking_report'),
    path('export/<str:report_type>/', views.export_report, name='export_report'),
]
