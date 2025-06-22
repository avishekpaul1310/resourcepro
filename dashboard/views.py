from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta
from resources.models import Resource
from projects.models import Project, Task
from allocation.models import Assignment
from dashboard.models import DashboardAIAnalysis, AIInsight
from dashboard.ai_services import dashboard_ai_service, nli_service, enhanced_risk_service

@login_required
def dashboard(request):
    """
    Dashboard view with overall resource utilization, project status, and AI insights.
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
    
    # Get AI analysis for dashboard
    ai_analysis = dashboard_ai_service.generate_daily_briefing()
    
    # Add AI data to context
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
        'ai_analysis': ai_analysis,
        'has_ai_service': True,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def get_risk_recommendations(request):
    """
    API endpoint for getting AI recommendations for a specific risk
    """
    try:
        data = json.loads(request.body)
        risk_id = data.get('risk_id')
        
        if not risk_id:
            return JsonResponse({"error": "Risk ID is required"}, status=400)
        
        recommendations = enhanced_risk_service.generate_risk_recommendations(risk_id)
        return JsonResponse(recommendations)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def process_nli_query(request):
    """
    API endpoint for processing natural language interface queries
    """
    try:
        data = json.loads(request.body)
        query_text = data.get('query', '')
        
        if not query_text:
            return JsonResponse({"error": "Query text is required"}, status=400)
        
        response = nli_service.process_query(query_text, user=request.user)
        return JsonResponse(response)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def refresh_ai_analysis(request):
    """
    API endpoint to refresh AI analysis
    """
    try:
        ai_analysis = dashboard_ai_service.generate_daily_briefing(force_refresh=True)
        return JsonResponse(ai_analysis)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def resolve_insight(request, insight_id):
    """
    API endpoint to resolve an AI insight
    """
    try:
        insight = AIInsight.objects.get(id=insight_id, is_active=True)
        insight.resolve(user=request.user)
        return JsonResponse({"success": True})
    except AIInsight.DoesNotExist:
        return JsonResponse({"error": "Insight not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_project_resources(request):
    """
    API endpoint to get resources assigned to a specific project
    """
    project_id = request.GET.get('project_id')
    
    if not project_id:
        # If no project specified, return all available resources
        resources = Resource.objects.all()
    else:
        try:
            project = Project.objects.get(id=project_id)
            # Get resources assigned to tasks in this project
            assigned_resource_ids = Assignment.objects.filter(
                task__project=project
            ).values_list('resource_id', flat=True).distinct()
            
            # For recommendations, we want to show all resources, not just assigned ones
            resources = Resource.objects.all()
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)
    
    resources_data = []
    for resource in resources:
        resources_data.append({
            'id': resource.id,
            'name': resource.name,
            'role': resource.role,
            'current_utilization': resource.current_utilization(),
            'hourly_rate': float(resource.hourly_rate) if hasattr(resource, 'hourly_rate') and resource.hourly_rate else 50.0,
            'skills': [skill.name for skill in resource.skills.all()] if hasattr(resource, 'skills') else []
        })
    
    return JsonResponse({
        'success': True,
        'resources': resources_data
    })

@login_required
@require_http_methods(["GET"])
def get_project_tasks(request):
    """
    API endpoint to get tasks for a specific project
    """
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({"error": "Project ID is required"}, status=400)
    
    try:
        project = Project.objects.get(id=project_id)
        tasks = Task.objects.filter(project=project)
        
        task_data = []
        for task in tasks:
            task_data.append({
                'id': task.id,
                'name': task.name,
                'status': task.status,
                'priority': getattr(task, 'priority', 3),
                'estimated_hours': float(task.estimated_hours) if task.estimated_hours else 0,
                'completion_percentage': task.completion_percentage,
                'assigned_resources': [assignment.resource.name for assignment in task.assignments.all()]
            })
        
        return JsonResponse({
            "success": True,
            "tasks": task_data,
            "project_name": project.name
        })
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_ai_analysis(request):
    """
    API endpoint for getting current AI analysis
    """
    try:
        # Get the latest AI analysis
        latest_analysis = DashboardAIAnalysis.objects.filter(
            analysis_type='daily_briefing'
        ).order_by('-created_at').first()
        
        if latest_analysis:
            # Check if analysis is fresh (less than 1 hour old)
            is_fresh = (timezone.now() - latest_analysis.created_at).total_seconds() < 3600
            
            return JsonResponse({
                "id": latest_analysis.id,
                "summary": latest_analysis.summary,
                "risks": latest_analysis.risks,
                "recommendations": latest_analysis.recommendations,
                "confidence_score": latest_analysis.confidence_score,
                "created_at": latest_analysis.created_at.isoformat(),
                "is_fresh": is_fresh
            })
        else:
            # If no analysis exists, return basic structure
            return JsonResponse({
                "summary": "No AI analysis available yet.",
                "risks": [],
                "recommendations": [],
                "confidence_score": 0.0,
                "created_at": timezone.now().isoformat(),
                "is_fresh": False
            })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
