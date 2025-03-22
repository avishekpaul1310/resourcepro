from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from resources.models import Resource
from projects.models import Project, Task
from .models import Assignment

@login_required
def allocation_board(request):
    """
    Main allocation board view where users can assign resources to tasks.
    """
    # Get all resources
    resources = Resource.objects.all()
    
    # Calculate current utilization for all resources
    for resource in resources:
        resource.utilization = resource.current_utilization()
        resource.capped_utilization = min(resource.utilization, 100)
    
    # Get unassigned tasks
    unassigned_tasks = Task.objects.filter(
        Q(assignments=None) & 
        Q(status__in=['not_started', 'in_progress', 'blocked'])
    ).distinct()
    
    # Get all projects for filtering
    projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold'])
    
    # Apply filters if provided
    project_filter = request.GET.get('project')
    if project_filter:
        unassigned_tasks = unassigned_tasks.filter(project_id=project_filter)
    
    # For each resource, get their assignments
    for resource in resources:
        resource.task_assignments = Assignment.objects.filter(
            resource=resource,
            task__status__in=['not_started', 'in_progress', 'blocked']
        ).select_related('task', 'task__project')
    
    context = {
        'resources': resources,
        'unassigned_tasks': unassigned_tasks,
        'projects': projects,
        'selected_project': project_filter,
    }
    
    return render(request, 'allocation/allocation_board.html', context)