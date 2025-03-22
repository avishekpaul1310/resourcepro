from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
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
    
    context = {
        'resources': resources,
        'projects': projects,
        'upcoming_deadlines': upcoming_deadlines,
        'overallocated_resources': overallocated_resources,
        'unassigned_tasks': unassigned_tasks,
        'total_resources': resources.count(),
        'total_projects': projects.count(),
    }
    
    return render(request, 'dashboard/dashboard.html', context)