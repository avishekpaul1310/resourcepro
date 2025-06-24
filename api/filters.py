"""
Custom filters for ResourcePro API
"""
import django_filters
from django.db.models import Q
from resources.models import Resource, Skill, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment


class ResourceFilter(django_filters.FilterSet):
    """Custom filter for Resource model"""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    skills = django_filters.ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        field_name='skills__id',
        to_field_name='id'
    )
    min_capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    min_cost = django_filters.NumberFilter(field_name='cost_per_hour', lookup_expr='gte')
    max_cost = django_filters.NumberFilter(field_name='cost_per_hour', lookup_expr='lte')
    timezone = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Resource
        fields = ['name', 'role', 'department', 'skills', 'timezone', 'location']


class ProjectFilter(django_filters.FilterSet):
    """Custom filter for Project model"""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Project._meta.get_field('status').choices)
    priority = django_filters.NumberFilter()
    min_priority = django_filters.NumberFilter(field_name='priority', lookup_expr='gte')
    max_priority = django_filters.NumberFilter(field_name='priority', lookup_expr='lte')
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    manager = django_filters.CharFilter(field_name='manager__username', lookup_expr='icontains')
    min_budget = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    max_budget = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')
    
    class Meta:
        model = Project
        fields = ['name', 'status', 'priority', 'manager']


class TaskFilter(django_filters.FilterSet):
    """Custom filter for Task model"""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    project_name = django_filters.CharFilter(field_name='project__name', lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Task._meta.get_field('status').choices)
    priority = django_filters.NumberFilter()
    min_priority = django_filters.NumberFilter(field_name='priority', lookup_expr='gte')
    max_priority = django_filters.NumberFilter(field_name='priority', lookup_expr='lte')
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    skills_required = django_filters.ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        field_name='skills_required__id',
        to_field_name='id'
    )
    min_estimated_hours = django_filters.NumberFilter(field_name='estimated_hours', lookup_expr='gte')
    max_estimated_hours = django_filters.NumberFilter(field_name='estimated_hours', lookup_expr='lte')
    min_completion = django_filters.NumberFilter(field_name='completion_percentage', lookup_expr='gte')
    max_completion = django_filters.NumberFilter(field_name='completion_percentage', lookup_expr='lte')
    is_assigned = django_filters.BooleanFilter(method='filter_by_assignment')
    
    def filter_by_assignment(self, queryset, name, value):
        """Filter tasks by assignment status"""
        assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
        if value:
            return queryset.filter(id__in=assigned_task_ids)
        else:
            return queryset.exclude(id__in=assigned_task_ids)
    
    class Meta:
        model = Task
        fields = ['name', 'project', 'status', 'priority', 'skills_required']


class AssignmentFilter(django_filters.FilterSet):
    """Custom filter for Assignment model"""
    
    resource = django_filters.ModelChoiceFilter(queryset=Resource.objects.all())
    resource_name = django_filters.CharFilter(field_name='resource__name', lookup_expr='icontains')
    task = django_filters.ModelChoiceFilter(queryset=Task.objects.all())
    task_name = django_filters.CharFilter(field_name='task__name', lookup_expr='icontains')
    project = django_filters.ModelChoiceFilter(
        field_name='task__project',
        queryset=Project.objects.all()
    )
    project_name = django_filters.CharFilter(field_name='task__project__name', lookup_expr='icontains')
    min_allocated_hours = django_filters.NumberFilter(field_name='allocated_hours', lookup_expr='gte')
    max_allocated_hours = django_filters.NumberFilter(field_name='allocated_hours', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Assignment
        fields = ['resource', 'task', 'project']


class TimeEntryFilter(django_filters.FilterSet):
    """Custom filter for TimeEntry model"""
    
    resource = django_filters.ModelChoiceFilter(queryset=Resource.objects.all())
    resource_name = django_filters.CharFilter(field_name='resource__name', lookup_expr='icontains')
    task = django_filters.ModelChoiceFilter(queryset=Task.objects.all())
    task_name = django_filters.CharFilter(field_name='task__name', lookup_expr='icontains')
    project = django_filters.ModelChoiceFilter(
        field_name='task__project',
        queryset=Project.objects.all()
    )
    project_name = django_filters.CharFilter(field_name='task__project__name', lookup_expr='icontains')
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    min_hours = django_filters.NumberFilter(field_name='hours', lookup_expr='gte')
    max_hours = django_filters.NumberFilter(field_name='hours', lookup_expr='lte')
    is_billable = django_filters.BooleanFilter()
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = TimeEntry
        fields = ['resource', 'task', 'date', 'is_billable']
