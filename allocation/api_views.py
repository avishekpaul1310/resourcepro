"""
AI-powered allocation API views
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction

from projects.models import Task
from resources.models import Resource
from .models import Assignment
from analytics.ai_services import AIResourceAllocationService

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def ai_task_suggestions(request, task_id):
    """
    Get AI-powered resource suggestions for a specific task
    """
    try:
        task = get_object_or_404(Task, id=task_id)
        
        # Get AI suggestions
        ai_service = AIResourceAllocationService()
        suggestions = ai_service.suggest_optimal_resource_allocation(
            task_id=task_id, 
            force_refresh=False  # Use cache if available
        )
        
        if not suggestions or 'error' in suggestions:
            return JsonResponse({
                'success': False,
                'error': suggestions.get('error', 'Failed to get AI suggestions') if suggestions else 'No suggestions available'
            })
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'name': task.name,
                'estimated_hours': task.estimated_hours
            },
            'suggestions': suggestions.get('suggestions', [])
        })
        
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
    except Exception as e:
        logger.error(f"Error getting AI task suggestions: {e}")
        return JsonResponse({'success': False, 'error': 'Internal server error'})

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_auto_assign_tasks(request):
    """
    Auto-assign multiple unassigned tasks using AI recommendations
    """
    try:
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return JsonResponse({'success': False, 'error': 'No tasks specified'})
        
        ai_service = AIResourceAllocationService()
        assignments_made = []
        errors = []
        
        with transaction.atomic():
            for task_id in task_ids:
                try:
                    task = Task.objects.get(id=task_id)
                    
                    # Skip if already assigned
                    if Assignment.objects.filter(task=task).exists():
                        continue
                    
                    # Get AI suggestions
                    suggestions = ai_service.suggest_optimal_resource_allocation(
                        task_id=task_id, 
                        force_refresh=False
                    )
                    
                    if suggestions and 'suggestions' in suggestions and suggestions['suggestions']:
                        # Use the best suggestion (first one)
                        best_suggestion = suggestions['suggestions'][0]
                        resource_id = best_suggestion['resource']['id']
                        
                        resource = Resource.objects.get(id=resource_id)
                          # Create assignment
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
                            'match_score': best_suggestion.get('match_score', 0),
                            'reasoning': best_suggestion.get('reasoning', 'AI recommendation')
                        })
                        
                except Task.DoesNotExist:
                    errors.append(f"Task {task_id} not found")
                except Resource.DoesNotExist:
                    errors.append(f"Resource not found for task {task_id}")
                except Exception as e:
                    errors.append(f"Failed to assign task {task_id}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'assignments_made': assignments_made,
            'total_assigned': len(assignments_made),
            'errors': errors
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error in AI auto-assign: {e}")
        return JsonResponse({'success': False, 'error': 'Internal server error'})

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def assign_task(request):
    """
    Manually assign a task to a resource with conflict checking
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        resource_id = data.get('resource_id')
        
        if not task_id or not resource_id:
            return JsonResponse({'success': False, 'error': 'Task ID and Resource ID required'})
        
        task = get_object_or_404(Task, id=task_id)
        resource = get_object_or_404(Resource, id=resource_id)
        
        # Check for existing assignment
        if Assignment.objects.filter(task=task).exists():
            return JsonResponse({'success': False, 'error': 'Task is already assigned'})
        
        # Check for conflicts
        conflicts = check_resource_conflicts(task, resource)
          # Create assignment
        assignment = Assignment.objects.create(
            task=task,
            resource=resource,
            allocated_hours=task.estimated_hours
        )
        
        # Get updated utilization
        new_utilization = resource.current_utilization()
        
        return JsonResponse({
            'success': True,
            'assignment': {
                'id': assignment.id,
                'task_id': task.id,
                'task_name': task.name,
                'resource_id': resource.id,
                'resource_name': resource.name,
                'allocated_hours': assignment.allocated_hours
            },
            'new_utilization': new_utilization,
            'conflicts': conflicts
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': f'Internal server error: {str(e)}'})

@login_required
@require_http_methods(["GET"])
def check_assignment_conflicts(request):
    """
    Check for potential conflicts when assigning a task to a resource
    """
    try:
        task_id = request.GET.get('task_id')
        resource_id = request.GET.get('resource_id')
        
        if not task_id or not resource_id:
            return JsonResponse({'success': False, 'error': 'Task ID and Resource ID required'})
        
        task = get_object_or_404(Task, id=task_id)
        resource = get_object_or_404(Resource, id=resource_id)
        
        conflicts = check_resource_conflicts(task, resource)
        
        return JsonResponse({
            'success': True,
            'conflicts': conflicts,
            'has_conflicts': len(conflicts) > 0
        })
        
    except Exception as e:
        logger.error(f"Error checking conflicts: {e}")
        return JsonResponse({'success': False, 'error': 'Internal server error'})

def check_resource_conflicts(task, resource):
    """
    Helper function to check for various assignment conflicts
    """
    conflicts = []
    
    # Check utilization
    current_utilization = resource.current_utilization()
    if current_utilization > 85:
        conflicts.append({
            'type': 'high_utilization',
            'severity': 'warning' if current_utilization <= 100 else 'error',
            'message': f"Resource is {current_utilization:.1f}% utilized"
        })
    
    # Check skill match
    task_skills = set(task.skills_required.values_list('name', flat=True))
    resource_skills = set(resource.skills.values_list('name', flat=True))
    
    missing_skills = task_skills - resource_skills
    if missing_skills:
        conflicts.append({
            'type': 'skill_mismatch',
            'severity': 'warning',
            'message': f"Missing skills: {', '.join(missing_skills)}"
        })
    
    # Check date conflicts (if resource has overlapping assignments)
    overlapping_assignments = Assignment.objects.filter(
        resource=resource,
        task__start_date__lte=task.end_date,
        task__end_date__gte=task.start_date
    ).exclude(task=task)
    
    if overlapping_assignments.exists():
        conflicts.append({
            'type': 'schedule_conflict',
            'severity': 'warning',
            'message': f"Has {overlapping_assignments.count()} overlapping assignments"
        })
    
    return conflicts

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def unassign_task(request):
    """
    Remove an assignment and return task to unassigned list
    """
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        
        # More detailed error messages for debugging
        if not assignment_id:
            logger.warning(f"Unassign task called without assignment_id. Request data: {data}")
            return JsonResponse({
                'success': False, 
                'error': 'Assignment ID required',
                'debug_info': f'Received data: {data}'
            })
        
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Store info before deletion
        task_info = {
            'id': assignment.task.id,
            'name': assignment.task.name,
            'estimated_hours': assignment.task.estimated_hours,
            'project_name': assignment.task.project.name,
            'start_date': assignment.task.start_date.strftime('%b %d'),
            'end_date': assignment.task.end_date.strftime('%b %d')
        }
        
        resource_id = assignment.resource.id
        
        # Delete the assignment
        assignment.delete()
        
        # Get updated utilization
        resource = Resource.objects.get(id=resource_id)
        new_utilization = resource.current_utilization()
        
        return JsonResponse({
            'success': True,
            'task': task_info,
            'resource_id': resource_id,
            'new_utilization': new_utilization
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error unassigning task: {e}")
        return JsonResponse({'success': False, 'error': f'Internal server error: {str(e)}'})
