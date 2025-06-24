"""
API ViewSets for ResourcePro
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from resources.models import Resource, Skill, ResourceSkill, TimeEntry, ResourceAvailability
from projects.models import Project, Task
from allocation.models import Assignment
from accounts.models import UserProfile
from analytics.ai_services import AIResourceAllocationService
from analytics.working_enhanced_ai import WorkingEnhancedAIService

from .serializers import (
    UserSerializer, UserProfileSerializer, SkillSerializer, ResourceSerializer,
    ResourceDetailSerializer, TaskSerializer, ProjectSerializer, ProjectDetailSerializer,
    AssignmentSerializer, TimeEntrySerializer, ResourceAvailabilitySerializer,
    AIResourceSuggestionSerializer, AITaskRecommendationSerializer,
    BulkAssignmentSerializer, ResourceUtilizationSerializer, APIResponseSerializer
)
from .permissions import (
    IsOwnerOrReadOnly, IsResourceOwnerOrManager, IsProjectManagerOrReadOnly,
    CanManageAssignments, CanViewTimeEntries
)
from .filters import (
    ResourceFilter, ProjectFilter, TaskFilter, AssignmentFilter, TimeEntryFilter
)


class CustomAuthToken(ObtainAuthToken):
    """Custom authentication token view with user details"""
    
    @extend_schema(
        tags=['Authentication'],
        summary="Obtain authentication token",
        description="Get API token for authentication. Returns token and user details."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })


@extend_schema_view(
    list=extend_schema(
        tags=['Resources'],
        summary="List all skills",
        description="Get a paginated list of all skills in the system."
    ),
    create=extend_schema(
        tags=['Resources'],
        summary="Create a new skill",
        description="Create a new skill that can be assigned to resources."
    ),
    retrieve=extend_schema(
        tags=['Resources'],
        summary="Get skill details",
        description="Get detailed information about a specific skill."
    ),
    update=extend_schema(
        tags=['Resources'],
        summary="Update skill",
        description="Update skill information."
    ),
    destroy=extend_schema(
        tags=['Resources'],
        summary="Delete skill",
        description="Delete a skill from the system."
    )
)
class SkillViewSet(viewsets.ModelViewSet):
    """ViewSet for managing skills"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        tags=['Resources'],
        summary="List all resources",
        description="Get a paginated list of all resources with their skills and utilization."
    ),
    create=extend_schema(
        tags=['Resources'],
        summary="Create a new resource",
        description="Create a new resource in the system."
    ),
    retrieve=extend_schema(
        tags=['Resources'],
        summary="Get resource details",
        description="Get detailed information about a specific resource including availability and time entries."
    )
)
class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing resources"""
    queryset = Resource.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsResourceOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ResourceFilter
    search_fields = ['name', 'role', 'department']
    ordering_fields = ['name', 'role', 'capacity']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResourceDetailSerializer
        return ResourceSerializer
    
    @extend_schema(
        tags=['Resources'],
        summary="Get resource utilization",
        description="Get current utilization data for a specific resource.",
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date for utilization calculation'),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date for utilization calculation'),
        ]
    )
    @action(detail=True, methods=['get'])
    def utilization(self, request, pk=None):
        """Get resource utilization data"""
        resource = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        utilization = resource.current_utilization(start_date, end_date)
        
        return Response({
            'resource_id': resource.id,
            'resource_name': resource.name,
            'utilization_percentage': utilization,
            'capacity': resource.capacity,
            'period_start': start_date,
            'period_end': end_date
        })
    
    @extend_schema(
        tags=['Resources'],
        summary="Get available resources",
        description="Get resources available for assignment during a specific period.",
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date for availability check'),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date for availability check'),
            OpenApiParameter('required_skills', OpenApiTypes.STR, description='Comma-separated list of required skill IDs'),
        ]
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available resources for a time period"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        required_skills = request.query_params.get('required_skills', '').split(',')
        
        queryset = self.get_queryset()
        
        # Filter by skills if provided
        if required_skills and required_skills[0]:
            skill_ids = [int(skill_id) for skill_id in required_skills if skill_id.isdigit()]
            queryset = queryset.filter(skills__in=skill_ids).distinct()
        
        # Add availability filtering logic here
        # For now, return all resources with utilization data
        available_resources = []
        for resource in queryset:
            utilization = resource.current_utilization(start_date, end_date)
            if utilization < 100:  # Resource has some availability
                available_resources.append({
                    **ResourceSerializer(resource).data,
                    'utilization_percentage': utilization,
                    'available_capacity': resource.capacity * (1 - utilization / 100)
                })
        
        return Response({
            'count': len(available_resources),
            'results': available_resources
        })


@extend_schema_view(
    list=extend_schema(
        tags=['Projects'],
        summary="List all projects",
        description="Get a paginated list of all projects with basic information."
    ),
    create=extend_schema(
        tags=['Projects'],
        summary="Create a new project",
        description="Create a new project in the system."
    ),
    retrieve=extend_schema(
        tags=['Projects'],
        summary="Get project details",
        description="Get detailed information about a specific project including all tasks."
    )
)
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects"""
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    @extend_schema(
        tags=['Projects'],
        summary="Get project statistics",
        description="Get comprehensive statistics for a specific project."
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get project statistics"""
        project = self.get_object()
        tasks = project.tasks.all()
        
        stats = {
            'project_id': project.id,
            'project_name': project.name,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'in_progress_tasks': tasks.filter(status='in_progress').count(),
            'not_started_tasks': tasks.filter(status='not_started').count(),
            'total_estimated_hours': sum(task.estimated_hours for task in tasks),
            'total_actual_hours': sum(task.get_actual_hours() for task in tasks),
            'completion_percentage': project.get_completion_percentage(),
            'assigned_resources': Assignment.objects.filter(task__project=project).values_list('resource__name', flat=True).distinct().count()
        }
        
        return Response(stats)


@extend_schema_view(
    list=extend_schema(
        tags=['Projects'],
        summary="List all tasks",
        description="Get a paginated list of all tasks with filtering options."
    ),
    create=extend_schema(
        tags=['Projects'],
        summary="Create a new task",
        description="Create a new task within a project."
    ),
    retrieve=extend_schema(
        tags=['Projects'],
        summary="Get task details",
        description="Get detailed information about a specific task."
    )
)
class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'priority']
    ordering = ['-created_at']
    
    @extend_schema(
        tags=['Projects'],
        summary="Get unassigned tasks",
        description="Get all tasks that don't have any resource assignments."
    )
    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Get unassigned tasks"""
        assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
        unassigned_tasks = self.get_queryset().exclude(id__in=assigned_task_ids)
        
        serializer = self.get_serializer(unassigned_tasks, many=True)
        return Response({
            'count': unassigned_tasks.count(),
            'results': serializer.data
        })
    
    @extend_schema(
        tags=['AI Services'],
        summary="Get AI resource suggestions for task",
        description="Get AI-powered resource allocation suggestions for a specific task."
    )
    @action(detail=True, methods=['get'])
    def ai_suggestions(self, request, pk=None):
        """Get AI resource suggestions for a task"""
        task = self.get_object()
        
        try:
            ai_service = AIResourceAllocationService()
            suggestions = ai_service.suggest_optimal_resource_allocation(
                task_id=task.id,
                force_refresh=True
            )
            
            return Response({
                'task_id': task.id,
                'task_name': task.name,
                'suggestions': suggestions.get('suggestions', [])
            })
        except Exception as e:
            return Response({
                'error': f'AI service error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    list=extend_schema(
        tags=['Allocation'],
        summary="List all assignments",
        description="Get a paginated list of all resource assignments."
    ),
    create=extend_schema(
        tags=['Allocation'],
        summary="Create assignment",
        description="Assign a resource to a task."
    ),
    destroy=extend_schema(
        tags=['Allocation'],
        summary="Remove assignment",
        description="Remove a resource assignment from a task."
    )
)
class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assignments"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAssignments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AssignmentFilter
    ordering_fields = ['created_at', 'allocated_hours']
    ordering = ['-created_at']
    
    @extend_schema(
        tags=['Allocation'],
        summary="Bulk assign tasks",
        description="Automatically assign multiple unassigned tasks using AI recommendations.",
        request=BulkAssignmentSerializer
    )
    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """Bulk assign tasks using AI"""
        serializer = BulkAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task_ids = serializer.validated_data['task_ids']
        auto_assign = serializer.validated_data['auto_assign']
        force_reassign = serializer.validated_data['force_reassign']
        
        assignments_made = []
        errors = []
        
        try:
            ai_service = AIResourceAllocationService()
            
            for task_id in task_ids:
                try:
                    task = Task.objects.get(id=task_id)
                    
                    # Skip if already assigned (unless force_reassign is True)
                    if Assignment.objects.filter(task=task).exists() and not force_reassign:
                        continue
                    
                    if auto_assign:
                        suggestions = ai_service.suggest_optimal_resource_allocation(
                            task_id=task_id,
                            force_refresh=False
                        )
                        
                        if suggestions and 'suggestions' in suggestions and suggestions['suggestions']:
                            best_suggestion = suggestions['suggestions'][0]
                            resource_id = best_suggestion['resource']['id']
                            resource = Resource.objects.get(id=resource_id)
                            
                            # Remove existing assignment if force_reassign
                            if force_reassign:
                                Assignment.objects.filter(task=task).delete()
                            
                            assignment = Assignment.objects.create(
                                task=task,
                                resource=resource,
                                allocated_hours=task.estimated_hours
                            )
                            
                            assignments_made.append({
                                'task_id': task.id,
                                'task_name': task.name,
                                'resource_id': resource.id,
                                'resource_name': resource.name,
                                'assignment_id': assignment.id,
                                'match_score': best_suggestion.get('match_score', 0)
                            })
                            
                except Task.DoesNotExist:
                    errors.append(f"Task {task_id} not found")
                except Exception as e:
                    errors.append(f"Failed to assign task {task_id}: {str(e)}")
            
            return Response({
                'success': True,
                'assignments_made': assignments_made,
                'total_assigned': len(assignments_made),
                'errors': errors
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Bulk assignment failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        tags=['Allocation'],
        summary="Check assignment conflicts",
        description="Check for potential conflicts when assigning a resource to a task.",
        parameters=[
            OpenApiParameter('task_id', OpenApiTypes.INT, description='Task ID'),
            OpenApiParameter('resource_id', OpenApiTypes.INT, description='Resource ID'),
        ]
    )
    @action(detail=False, methods=['get'])
    def check_conflicts(self, request):
        """Check for assignment conflicts"""
        task_id = request.query_params.get('task_id')
        resource_id = request.query_params.get('resource_id')
        
        if not task_id or not resource_id:
            return Response({
                'error': 'Both task_id and resource_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            task = Task.objects.get(id=task_id)
            resource = Resource.objects.get(id=resource_id)
            
            conflicts = []
            
            # Check for skill requirements
            required_skills = task.skills_required.all()
            if required_skills.exists():
                resource_skills = resource.skills.all()
                missing_skills = [skill for skill in required_skills if skill not in resource_skills]
                if missing_skills:
                    conflicts.append({
                        'type': 'skill_mismatch',
                        'message': f"Resource lacks required skills: {', '.join(skill.name for skill in missing_skills)}"
                    })
            
            # Check for overallocation
            current_utilization = resource.current_utilization(task.start_date, task.end_date)
            if current_utilization > 80:  # Warning threshold
                conflicts.append({
                    'type': 'high_utilization',
                    'message': f"Resource has high utilization ({current_utilization:.1f}%)"
                })
            
            return Response({
                'success': True,
                'conflicts': conflicts,
                'task_name': task.name,
                'resource_name': resource.name
            })
            
        except (Task.DoesNotExist, Resource.DoesNotExist) as e:
            return Response({
                'error': 'Task or Resource not found'
            }, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(
        tags=['Resources'],
        summary="List time entries",
        description="Get a paginated list of time entries with filtering options."
    ),
    create=extend_schema(
        tags=['Resources'],
        summary="Create time entry",
        description="Create a new time entry for a resource."
    )
)
class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing time entries"""
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated, CanViewTimeEntries]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TimeEntryFilter
    ordering_fields = ['date', 'hours']
    ordering = ['-date']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user information (read-only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    
    @extend_schema(
        tags=['Authentication'],
        summary="Get current user profile",
        description="Get the profile information of the currently authenticated user."
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        profile_data = serializer.data
        
        # Add profile information if available
        try:
            profile = request.user.profile
            profile_data['profile'] = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            profile_data['profile'] = None
        
        return Response(profile_data)
