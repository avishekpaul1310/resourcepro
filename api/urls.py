from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from . import views
from .viewsets import (
    CustomAuthToken, SkillViewSet, ResourceViewSet, ProjectViewSet,
    TaskViewSet, AssignmentViewSet, TimeEntryViewSet, UserViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'time-entries', TimeEntryViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api_schema'), name='api_redoc'),
    
    # Authentication
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('auth/token/obtain/', obtain_auth_token, name='api_token_obtain'),
    
    # REST API endpoints
    path('v1/', include(router.urls)),
    
    # Legacy API endpoints (for backward compatibility)
    path('assign-resource/', views.assign_resource, name='api_assign_resource'),
    path('remove-assignment/', views.remove_assignment, name='api_remove_assignment'),
    path('check-conflicts/', views.check_conflicts, name='api_check_conflicts'),
]