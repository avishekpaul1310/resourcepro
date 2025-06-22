from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/simulate-intervention/', views.simulate_intervention, name='simulate_intervention'),
    path('api/nli-query/', views.process_nli_query, name='process_nli_query'),
    path('api/refresh-ai-analysis/', views.refresh_ai_analysis, name='refresh_ai_analysis'),
    path('api/resolve-insight/<int:insight_id>/', views.resolve_insight, name='resolve_insight'),
    path('api/project-resources/', views.get_project_resources, name='get_project_resources'),
    path('api/project-tasks/', views.get_project_tasks, name='get_project_tasks'),
]