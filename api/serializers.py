"""
API Serializers for ResourcePro
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from resources.models import Resource, Skill, ResourceSkill, TimeEntry, ResourceAvailability
from projects.models import Project, Task
from allocation.models import Assignment
from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'department']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model"""
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description']


class ResourceSkillSerializer(serializers.ModelSerializer):
    """Serializer for ResourceSkill model"""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ResourceSkill
        fields = ['id', 'skill', 'skill_id', 'proficiency']


class ResourceAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for ResourceAvailability model"""
    
    class Meta:
        model = ResourceAvailability
        fields = [
            'id', 'resource', 'availability_type', 'start_date', 'end_date', 
            'hours_per_day', 'description', 'created_at'
        ]
        read_only_fields = ['created_at']


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry model"""
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True)
    project_name = serializers.CharField(source='task.project.name', read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'resource', 'resource_name', 'task', 'task_name', 'project_name',
            'date', 'hours', 'description', 'is_billable', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'resource_name', 'task_name', 'project_name']


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for Resource model"""
    skills = SkillSerializer(many=True, read_only=True)
    resource_skills = ResourceSkillSerializer(many=True, read_only=True)
    current_utilization = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Resource
        fields = [
            'id', 'user', 'name', 'role', 'department', 'skills', 'resource_skills',
            'capacity', 'cost_per_hour', 'color', 'timezone', 'location',
            'current_utilization'
        ]
    
    def get_current_utilization(self, obj):
        """Get current utilization percentage"""
        try:
            return obj.current_utilization()
        except:
            return 0.0


class ResourceDetailSerializer(ResourceSerializer):
    """Detailed serializer for Resource model with additional data"""
    availability = ResourceAvailabilitySerializer(many=True, read_only=True)
    time_entries = TimeEntrySerializer(many=True, read_only=True)
    
    class Meta(ResourceSerializer.Meta):
        fields = ResourceSerializer.Meta.fields + ['availability', 'time_entries']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    skills_required = SkillSerializer(many=True, read_only=True)
    assigned_resources = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'project_name', 'name', 'description', 'start_date', 'end_date',
            'estimated_hours', 'actual_hours', 'skills_required', 'status',
            'completion_percentage', 'priority', 'assigned_resources',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'project_name']
    
    def get_assigned_resources(self, obj):
        """Get assigned resources for this task"""
        assignments = obj.assignments.all()
        return [
            {
                'resource_id': assignment.resource.id,
                'resource_name': assignment.resource.name,
                'allocated_hours': assignment.allocated_hours,
                'assignment_id': assignment.id
            }
            for assignment in assignments
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    manager = UserSerializer(read_only=True)
    tasks_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    total_estimated_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'manager',
            'status', 'priority', 'color', 'budget', 'tasks_count',
            'completion_percentage', 'total_estimated_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_tasks_count(self, obj):
        """Get total number of tasks in project"""
        return obj.tasks.count()
    
    def get_completion_percentage(self, obj):
        """Get project completion percentage"""
        try:
            return obj.get_completion_percentage()
        except:
            return 0
    
    def get_total_estimated_hours(self, obj):
        """Get total estimated hours for all tasks"""
        return sum(task.estimated_hours for task in obj.tasks.all())


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed serializer for Project model with tasks"""
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['tasks']


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    resource = ResourceSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    resource_id = serializers.IntegerField(write_only=True)
    task_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'resource', 'task', 'resource_id', 'task_id',
            'allocated_hours', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate assignment data"""
        # Check if assignment already exists
        if Assignment.objects.filter(
            resource_id=data['resource_id'], 
            task_id=data['task_id']
        ).exists():
            raise serializers.ValidationError(
                "This resource is already assigned to this task."
            )
        return data


# AI-specific serializers
class AIResourceSuggestionSerializer(serializers.Serializer):
    """Serializer for AI resource suggestions"""
    resource = ResourceSerializer(read_only=True)
    match_score = serializers.FloatField()
    reasoning = serializers.CharField()
    skill_match = serializers.DictField()
    availability_status = serializers.CharField()
    utilization_impact = serializers.FloatField()


class AITaskRecommendationSerializer(serializers.Serializer):
    """Serializer for AI task recommendations"""
    task = TaskSerializer(read_only=True)
    suggestions = AIResourceSuggestionSerializer(many=True)
    priority_score = serializers.FloatField()
    complexity_analysis = serializers.DictField()


# Bulk operation serializers
class BulkAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk assignment operations"""
    task_ids = serializers.ListField(child=serializers.IntegerField())
    auto_assign = serializers.BooleanField(default=True)
    force_reassign = serializers.BooleanField(default=False)


class ResourceUtilizationSerializer(serializers.Serializer):
    """Serializer for resource utilization data"""
    resource = ResourceSerializer(read_only=True)
    utilization_percentage = serializers.FloatField()
    allocated_hours = serializers.FloatField()
    available_hours = serializers.FloatField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()


# API Response serializers
class APIResponseSerializer(serializers.Serializer):
    """Standard API response serializer"""
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)
    errors = serializers.ListField(required=False)


class PaginatedResponseSerializer(serializers.Serializer):
    """Paginated response serializer"""
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()
