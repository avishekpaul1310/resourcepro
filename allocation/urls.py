from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.allocation_board, name='allocation_board'),    # Enhanced AI-powered allocation APIs
    path('api/enhanced-ai-suggestions/', api_views.enhanced_ai_task_suggestions, name='enhanced_ai_task_suggestions'),
    path('api/ai-auto-assign/', api_views.ai_auto_assign_tasks, name='ai_auto_assign_tasks'),
    path('api/assign-task/', api_views.assign_task, name='assign_task'),
    path('api/unassign-task/', api_views.unassign_task, name='unassign_task'),
    path('api/check-conflicts/', api_views.check_assignment_conflicts, name='check_assignment_conflicts'),
]