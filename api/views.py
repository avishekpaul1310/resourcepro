from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
from datetime import timedelta
from resources.models import Resource
from projects.models import Task
from allocation.models import Assignment

@login_required
@require_POST
def assign_resource(request):
    """
    API endpoint to assign a resource to a task.
    """
    data = json.loads(request.body)
    task_id = data.get('task_id')
    resource_id = data.get('resource_id')
    allocated_hours = data.get('allocated_hours')
    
    # Get the task and resource
    task = get_object_or_404(Task, id=task_id)
    resource = get_object_or_404(Resource, id=resource_id)
    
    # If no hours specified, use the task's estimated hours
    if not allocated_hours:
        allocated_hours = task.estimated_hours
    
    # Create or update the assignment
    assignment, created = Assignment.objects.update_or_create(
        task=task,
        resource=resource,
        defaults={'allocated_hours': allocated_hours}
    )
    
    # Return the assignment data
    assignment_data = {
        'id': assignment.id,
        'task_id': task.id,
        'task_name': task.name,
        'resource_id': resource.id,
        'resource_name': resource.name,
        'allocated_hours': assignment.allocated_hours,
        'project_name': task.project.name,
        'utilization': resource.current_utilization()
    }
    
    return JsonResponse({'success': True, 'assignment': assignment_data})

@login_required
@require_POST
def remove_assignment(request):
    """
    API endpoint to remove a resource assignment.
    """
    data = json.loads(request.body)
    assignment_id = data.get('assignment_id')
    
    # Get the assignment
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Get the resource before deleting (for utilization update)
    resource = assignment.resource
    
    # Delete the assignment
    assignment.delete()
    
    # Return updated utilization
    return JsonResponse({
        'success': True, 
        'resource_id': resource.id,
        'utilization': resource.current_utilization()
    })

@login_required
def check_conflicts(request):
    """
    API endpoint to check for conflicts when assigning a resource to a task.
    """
    task_id = request.GET.get('task_id')
    resource_id = request.GET.get('resource_id')
    
    # Get the task and resource
    task = get_object_or_404(Task, id=task_id)
    resource = get_object_or_404(Resource, id=resource_id)
    
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
    
    # Calculate additional utilization from this task
    work_days = sum(1 for i in range((task.end_date - task.start_date).days + 1) 
                  if (task.start_date + timedelta(days=i)).weekday() < 5)
    
    daily_capacity = resource.capacity / 5  # Assuming 5-day work week
    available_hours = daily_capacity * work_days
    
    if available_hours > 0:
        task_utilization = (task.estimated_hours / available_hours) * 100
        new_utilization = current_utilization + task_utilization
        
        if new_utilization > 100:
            conflicts.append({
                'type': 'overallocation',
                'message': f"Resource will be overallocated ({new_utilization:.1f}%)",
                'current_utilization': current_utilization,
                'new_utilization': new_utilization
            })
    
    # Check for schedule conflicts with dependencies
    dependencies = task.dependencies.all()
    for dependency in dependencies:
        if dependency.status != 'completed' and dependency.end_date > task.start_date:
            conflicts.append({
                'type': 'dependency_conflict',
                'message': f"Dependent task '{dependency.name}' is not completed and ends after this task starts"
            })
    
    return JsonResponse({
        'success': True,
        'conflicts': conflicts,
        'task_name': task.name,
        'resource_name': resource.name
    })