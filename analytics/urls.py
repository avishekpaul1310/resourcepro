from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main analytics pages
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('', views.analytics_dashboard, name='dashboard'),  # Alternative name for backwards compatibility
    path('forecast/', views.generate_forecast, name='forecasting'),
    path('forecast/generate/', views.generate_forecast, name='generate_forecast'),
    path('skills/', views.analyze_skills, name='skill_analysis'),
    path('skills/analyze/', views.analyze_skills, name='analyze_skills'),
    path('utilization/', views.utilization_report, name='utilization_report'),
    path('costs/', views.cost_tracking_report, name='cost_report'),
    path('costs/tracking/', views.cost_tracking_report, name='cost_tracking_report'),
    path('export/<str:report_type>/', views.export_report, name='export_report'),

    # AI analytics dashboard
    path('ai/', views.ai_analytics_dashboard, name='ai_analytics_dashboard'),

    # AI-powered endpoints
    path('ai/skill-recommendations/', views.ai_skill_recommendations, name='ai_skill_recommendations'),
    path('ai/resource-allocation/<int:task_id>/', views.ai_resource_allocation_suggestions, name='ai_resource_allocation'),
    path('ai/enhanced-forecasts/', views.ai_enhanced_forecasts, name='ai_enhanced_forecasts'),
    path('ai/strategic-recommendations/', views.ai_strategic_recommendations, name='ai_strategic_recommendations'),
]
