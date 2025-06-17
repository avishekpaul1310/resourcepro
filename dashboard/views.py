from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
from resources.models import Resource
from projects.models import Project, Task
from allocation.models import Assignment

@login_required
def dashboard(request):
    """
    Dashboard view with overall resource utilization and project status.
    """
    # Get all active resources
    resources = Resource.objects.all()
    
    # Calculate current utilization for all resources
    for resource in resources:
        resource.utilization = resource.current_utilization()
    
    # Get active projects
    projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold'])
    
    # For each project, calculate completion percentage
    for project in projects:
        project.completion = project.get_completion_percentage()
    
    # Get upcoming deadlines (tasks due in the next 14 days)
    today = timezone.now().date()
    upcoming_deadlines = Task.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=14),
        status__in=['not_started', 'in_progress', 'blocked']
    ).order_by('end_date').select_related('project')
    
    # Get overallocated resources
    overallocated_resources = [r for r in resources if r.utilization > 100]
    
    # Get unassigned tasks
    unassigned_tasks = Task.objects.filter(
        assignments=None,
        status__in=['not_started', 'in_progress', 'blocked']
    ).count()
    
    # Calculate some trending data for enhanced metrics
    last_week = today - timedelta(days=7)
    
    # Count projects created in the last week
    recent_projects = Project.objects.filter(
        created_at__gte=last_week
    ).count() if hasattr(Project, 'created_at') else 0
    
    # Count tasks completed in the last week
    completed_tasks_recent = Task.objects.filter(
        status='completed',
        updated_at__gte=last_week
    ).count() if hasattr(Task, 'updated_at') else 0
    
    # Calculate average utilization
    avg_utilization = sum(r.utilization for r in resources) / len(resources) if resources else 0
    
    # Prepare data for charts
    resource_names = [r.name for r in resources]
    resource_utilizations = [r.utilization for r in resources]
    
    project_names = [p.name for p in projects]
    project_completions = [p.completion for p in projects]
    
    # Create chart colors based on utilization
    resource_colors = []
    for r in resources:
        if r.utilization > 100:
            resource_colors.append("#e53e3e")
        elif r.utilization > 85:
            resource_colors.append("#ed8936")
        else:
            resource_colors.append("#48bb78")
    
    context = {
        'resources': resources,
        'projects': projects,
        'upcoming_deadlines': upcoming_deadlines,
        'overallocated_resources': overallocated_resources,
        'unassigned_tasks': unassigned_tasks,
        'total_resources': resources.count(),
        'total_projects': projects.count(),
        'recent_projects': recent_projects,
        'completed_tasks_recent': completed_tasks_recent,
        'avg_utilization': round(avg_utilization, 1),
        # Add these for the charts as JSON strings
        'resource_names_json': json.dumps(resource_names),
        'resource_utilizations_json': json.dumps(resource_utilizations),
        'resource_colors_json': json.dumps(resource_colors),
        'project_names_json': json.dumps(project_names),
        'project_completions_json': json.dumps(project_completions),
    }
    
    return render(request, 'dashboard/dashboard.html', context)