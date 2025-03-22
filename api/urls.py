from django.urls import path
from . import views

urlpatterns = [
    path('assign-resource/', views.assign_resource, name='api_assign_resource'),
    path('remove-assignment/', views.remove_assignment, name='api_remove_assignment'),
    path('check-conflicts/', views.check_conflicts, name='api_check_conflicts'),
]