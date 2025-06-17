from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import models
from datetime import timedelta, datetime
from decimal import Decimal
import json

from .services import PredictiveAnalyticsService, UtilizationTrackingService, CostTrackingService
from .models import ResourceDemandForecast, HistoricalUtilization, SkillDemandAnalysis, AISkillRecommendation, AIResourceAllocationSuggestion, AIForecastAdjustment
from .export_services import ReportExportService
from .ai_services import AISkillRecommendationService, AIResourceAllocationService, AIForecastEnhancementService
from utils.gemini_ai import gemini_service
from resources.models import Resource
from projects.models import Project, Task

@login_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    # Get recent forecasts
    recent_forecasts = ResourceDemandForecast.objects.all()[:5]    # Get skill demand analysis - get latest analyses for each skill
    skill_analyses_raw = SkillDemandAnalysis.objects.order_by('-analysis_date')[:10]
    
    # Add display percentage (capped at 100%)
    skill_analyses = []
    for skill in skill_analyses_raw:
        skill.display_percentage = min(100, max(0, round(float(skill.demand_score) * 10, 0)))
        skill_analyses.append(skill)
    
    # Get utilization trends
    utilization_service = UtilizationTrackingService()
    utilization_trends = utilization_service.get_utilization_trends(days=30)
    
    # Get cost tracking data
    cost_service = CostTrackingService()
    cost_report = cost_service.get_cost_variance_report()
    
    # Calculate summary metrics
    total_resources = Resource.objects.count()
    total_projects = Project.objects.count()
    
    # Calculate utilization metrics
    all_utilizations = HistoricalUtilization.objects.filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    )
    
    avg_utilization = all_utilizations.aggregate(
        avg=models.Avg('utilization_percentage')
    )['avg'] or 0
    
    # Calculate utilization trend (compare last 30 days to previous 30 days)
    previous_utilizations = HistoricalUtilization.objects.filter(
        date__gte=timezone.now().date() - timedelta(days=60),
        date__lt=timezone.now().date() - timedelta(days=30)
    )
    
    previous_avg = previous_utilizations.aggregate(
        avg=models.Avg('utilization_percentage')
    )['avg'] or 0
    
    utilization_trend = avg_utilization - previous_avg
      # Calculate budget metrics
    total_budget = sum(item.get('budget', 0) for item in cost_report if item.get('budget'))
    actual_costs = sum(item.get('actual_cost', 0) for item in cost_report)
    budget_variance = total_budget - actual_costs
    
    # Get utilization data for the dashboard
    utilization_data = []
    for resource in Resource.objects.all()[:10]:
        recent_util = HistoricalUtilization.objects.filter(
            resource=resource,
            date__gte=timezone.now().date() - timedelta(days=30)
        ).aggregate(avg=models.Avg('utilization_percentage'))['avg'] or 0
        
        utilization_data.append({
            'resource': resource,
            'utilization_rate': round(recent_util, 1)
        })
    
    context = {
        'forecast_data': recent_forecasts,  # Match template variable name
        'skill_demand': skill_analyses,     # Match template variable name
        'utilization_data': utilization_data,  # Match template variable name
        'utilization_trends': utilization_trends,
        'cost_report': cost_report[:10],  # Top 10 projects
        'total_resources': total_resources,
        'total_projects': total_projects,
        'avg_utilization': round(avg_utilization, 1),
        'utilization_trend': round(utilization_trend, 1),
        'total_budget': total_budget,
        'actual_costs': actual_costs,
        'budget_variance': budget_variance,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def generate_forecast(request):
    """Generate new resource demand forecast"""
    if request.method == 'POST':
        days_ahead = int(request.POST.get('days_ahead', 30))
        
        analytics_service = PredictiveAnalyticsService()
        forecasts = analytics_service.generate_resource_demand_forecast(days_ahead)
        
        if forecasts:
            return JsonResponse({
                'success': True,
                'message': f'Generated {len(forecasts)} forecasts',
                'forecasts': [
                    {
                        'role': f.resource_role,
                        'predicted_demand': float(f.predicted_demand_hours),
                        'confidence': float(f.confidence_score)
                    } for f in forecasts
                ]
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Insufficient historical data for forecasting'
            })
    
    # GET request - display the forecasting page with filters
    from resources.models import Skill
    
    # Get filter parameters
    forecast_days = int(request.GET.get('forecast_days', 30))
    skill_filter = request.GET.get('skill_filter', '')
    
    # Get available skills for the filter
    available_skills = Skill.objects.all()
    
    # Generate fresh forecasts when form is submitted
    if 'forecast_days' in request.GET and skill_filter:
        # Generate skill-specific forecasts
        recent_forecasts = generate_skill_specific_forecasts(skill_filter, forecast_days)
    elif 'forecast_days' in request.GET:
        # Generate general forecasts
        analytics_service = PredictiveAnalyticsService()
        recent_forecasts = analytics_service.generate_resource_demand_forecast(forecast_days) or []
    else:
        # Show existing forecasts with filtering
        forecasts_query = ResourceDemandForecast.objects.order_by('-forecast_date')
        
        if skill_filter:
            try:
                selected_skill = Skill.objects.get(id=skill_filter)
                resources_with_skill = Resource.objects.filter(skills=selected_skill)
                roles_with_skill = [resource.role for resource in resources_with_skill]
                
                if roles_with_skill:
                    forecasts_query = forecasts_query.filter(resource_role__in=roles_with_skill)
                else:
                    forecasts_query = forecasts_query.none()
            except (Skill.DoesNotExist, ValueError):
                forecasts_query = forecasts_query.none()
        
        recent_forecasts = forecasts_query[:20]
    
    # Calculate summary statistics
    if recent_forecasts:
        avg_demand = sum(f.predicted_demand_hours for f in recent_forecasts) / len(recent_forecasts)
        peak_demand = max(f.predicted_demand_hours for f in recent_forecasts)
        avg_confidence = sum(f.confidence_score for f in recent_forecasts) / len(recent_forecasts)
        high_demand_days = len([f for f in recent_forecasts if f.predicted_demand_hours > 80])
    else:
        avg_demand = peak_demand = avg_confidence = high_demand_days = 0    # Get selected skill name for display
    selected_skill_name = None
    if skill_filter:
        try:
            selected_skill_name = Skill.objects.get(id=skill_filter).name
        except (Skill.DoesNotExist, ValueError):
            pass
    
    context = {
        'forecasts': recent_forecasts,
        'available_skills': available_skills,
        'forecast_days': forecast_days,
        'skill_filter': skill_filter,
        'selected_skill_name': selected_skill_name,
        'avg_demand': avg_demand,
        'peak_demand': peak_demand,
        'avg_confidence': avg_confidence,
        'high_demand_days': high_demand_days,
    }
    
    return render(request, 'analytics/forecasting.html', context)


def generate_skill_specific_forecasts(skill_filter, forecast_days):
    """Generate unique forecasts for a specific skill"""
    from resources.models import Skill
    import random
    
    try:
        selected_skill = Skill.objects.get(id=skill_filter)
        resources_with_skill = Resource.objects.filter(skills=selected_skill)
        
        if not resources_with_skill:
            return []
        
        # Generate skill-specific forecasts
        skill_forecasts = []
        roles_with_skill = list(set([r.role for r in resources_with_skill]))
        
        for role in roles_with_skill:
            role_resources = resources_with_skill.filter(role=role)
            resource_count = role_resources.count()
            
            # Create skill-specific forecast based on skill characteristics
            skill_hash = hash(selected_skill.name + role) % 1000
            base_demand = 30 + (skill_hash % 50)  # 30-80 hours base
            skill_multiplier = 0.7 + (skill_hash % 60) / 100  # 0.7-1.3 multiplier
            
            predicted_hours = base_demand * skill_multiplier * resource_count
            confidence = 0.65 + (skill_hash % 25) / 100  # 0.65-0.9 confidence
            
            forecast = ResourceDemandForecast.objects.create(
                forecast_date=timezone.now().date(),
                resource_role=f"{role} ({selected_skill.name})",
                predicted_demand_hours=round(predicted_hours, 2),
                confidence_score=round(confidence, 2),
                period_start=timezone.now().date() + timedelta(days=1),
                period_end=timezone.now().date() + timedelta(days=forecast_days)
            )
            skill_forecasts.append(forecast)
        
        return skill_forecasts
        
    except (Skill.DoesNotExist, ValueError):
        return []

@login_required
def analyze_skills(request):
    """Run skill demand analysis"""
    if request.method == 'POST':
        analytics_service = PredictiveAnalyticsService()
        analyses = analytics_service.analyze_skill_demand()
        
        return JsonResponse({
            'success': True,
            'message': f'Analyzed {len(analyses)} skills',
            'analyses': [
                {
                    'skill': a.skill_name,
                    'current_demand': a.current_demand,
                    'available_resources': a.available_resources,
                    'demand_score': float(a.demand_score),
                    'predicted_demand': a.predicted_future_demand
                } for a in analyses
            ]
        })
    
    # GET request - display the skill analysis page    # GET request - display the skill analysis page
    time_period = int(request.GET.get('time_period', 30))
    sort_by = request.GET.get('sort_by', 'demand')
    
    # Get skill demand analyses
    recent_analyses = SkillDemandAnalysis.objects.order_by('-analysis_date')[:20]
    
    # Process and sort the data based on the sort_by parameter
    skill_demand = []
    for analysis in recent_analyses:
        skill_data = {
            'skill_name': analysis.skill_name,
            'demand_score': float(analysis.demand_score),
            'active_projects': analysis.current_demand,
            'resource_count': analysis.available_resources,
            'trend': 0  # Default trend, can be enhanced later
        }
        skill_demand.append(skill_data)
    
    print(f"Processed {len(skill_demand)} skills")
    
    # Sort skills based on selected criteria
    if sort_by == 'demand':
        skill_demand.sort(key=lambda x: x['demand_score'], reverse=True)
    elif sort_by == 'projects':
        skill_demand.sort(key=lambda x: x['active_projects'], reverse=True)
    elif sort_by == 'resources':
        skill_demand.sort(key=lambda x: x['resource_count'], reverse=True)
    
    # Calculate skill gaps (simplified logic)
    skill_gaps = []
    for skill in skill_demand:
        if skill['demand_score'] > 70 and skill['resource_count'] < skill['active_projects']:
            gap = max(0, skill['active_projects'] - skill['resource_count'])
            priority = 'high' if skill['demand_score'] > 90 else 'medium' if skill['demand_score'] > 80 else 'low'
            skill_gaps.append({
                'skill_name': skill['skill_name'],
                'demand': skill['active_projects'],
                'available': skill['resource_count'],
                'gap': gap,
                'gap_percentage': min(100, (gap / max(1, skill['active_projects'])) * 100),
                'priority': priority
            })
    
    # Calculate trending skills (simplified - based on demand score)
    trending_up = [skill for skill in skill_demand if skill['demand_score'] > 80][:5]
    trending_down = [skill for skill in skill_demand if skill['demand_score'] < 30][:5]
    
    # Add mock trend values for display
    for skill in trending_up:
        skill['change'] = skill['demand_score'] / 10  # Mock trend calculation
    for skill in trending_down:
        skill['change'] = -(50 - skill['demand_score']) / 10  # Mock trend calculation
    
    # Calculate summary statistics
    total_skills = len(skill_demand)
    high_demand_skills = len([s for s in skill_demand if s['demand_score'] > 70])
    avg_demand_score = sum(s['demand_score'] for s in skill_demand) / len(skill_demand) if skill_demand else 0
    skills_trending_up = len(trending_up)
      # Generate recommendations
    recommendations = []
    if high_demand_skills > 0:
        recommendations.append(f"Focus on hiring for {high_demand_skills} high-demand skills (score > 70)")
    if skill_gaps:
        recommendations.append(f"Address {len(skill_gaps)} identified skill gaps through training or hiring")
    if trending_up:
        recommendations.append(f"Invest in {len(trending_up)} trending skills to stay competitive")
    
    context = {
        'skill_analyses': recent_analyses,
        'skill_demand': skill_demand[:10],  # Top 10 for display
        'skill_gaps': skill_gaps[:10],      # Top 10 gaps
        'trending_up': trending_up,
        'trending_down': trending_down,
        'total_skills': total_skills,
        'high_demand_skills': high_demand_skills,
        'avg_demand_score': avg_demand_score,
        'skills_trending_up': skills_trending_up,
        'time_period': str(time_period),
        'sort_by': sort_by,
        'recommendations': recommendations
    }
    return render(request, 'analytics/skill_analysis.html', context)

@login_required
def utilization_report(request):
    """Display utilization report"""
    from datetime import datetime
    from django.db.models import Sum, Count
    from projects.models import Project
    from allocation.models import Assignment
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    department = request.GET.get('department', '')
    selected_role = request.GET.get('role', '')
    
    # Set default date range if not provided
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get resources with filtering
    resources = Resource.objects.all()
    if department:
        resources = resources.filter(department=department)
    if selected_role:
        resources = resources.filter(role=selected_role)
    
    utilization_service = UtilizationTrackingService()
    
    # Record today's utilization if not already done
    utilization_service.record_daily_utilization()
    
    # Get utilization data for each resource
    utilization_data = []
    total_hours = 0
    billable_hours = 0
    overutilized_count = 0
    underutilized_count = 0
    
    for resource in resources:
        # Get utilization trends for the period
        trends = HistoricalUtilization.objects.filter(
            resource=resource,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate metrics
        avg_utilization = trends.aggregate(avg=models.Avg('utilization_percentage'))['avg'] or 0
        total_allocated = trends.aggregate(sum=models.Sum('allocated_hours'))['sum'] or 0
        total_available = trends.aggregate(sum=models.Sum('available_hours'))['sum'] or 0        # Calculate actual hours (simplified - using allocated hours)
        actual_hours = total_allocated if total_allocated else Decimal('0')
        # Calculate billable hours (assume 80% of actual hours are billable)
        resource_billable_hours = actual_hours * Decimal('0.8')
        
        # Get active projects for this resource
        active_projects = Assignment.objects.filter(
            resource=resource,
            task__start_date__lte=end_date,
            task__end_date__gte=start_date
        ).values('task__project').distinct().count()
        
        # Determine status
        if avg_utilization > 90:
            overutilized_count += 1
        elif avg_utilization < 50:
            underutilized_count += 1
        
        utilization_data.append({
            'resource': resource,
            'utilization_rate': round(avg_utilization, 1),
            'actual_hours': round(actual_hours, 1),
            'billable_hours': round(resource_billable_hours, 1),
            'active_projects': active_projects,
            'trends': trends[:10]  # Last 10 entries for detail view
        })        
        total_hours += actual_hours
        billable_hours += resource_billable_hours
    
    # Calculate summary statistics
    total_resources = resources.count()
    avg_utilization = sum(item['utilization_rate'] for item in utilization_data) / len(utilization_data) if utilization_data else 0
    billable_percentage = (billable_hours / total_hours * 100) if total_hours > 0 else 0
    
    # Calculate utilization trend (compare with previous period)
    previous_start = start_date - timedelta(days=(end_date - start_date).days)
    previous_utilizations = HistoricalUtilization.objects.filter(
        resource__in=resources,
        date__gte=previous_start,
        date__lt=start_date
    )
    previous_avg = previous_utilizations.aggregate(avg=models.Avg('utilization_percentage'))['avg'] or 0
    utilization_trend = avg_utilization - previous_avg
    
    # Get available departments and roles for filters
    departments = Resource.objects.values_list('department', flat=True).distinct().exclude(department__isnull=True)
    roles = Resource.objects.values_list('role', flat=True).distinct().exclude(role__isnull=True)
    
    context = {
        'utilization_data': utilization_data,
        'start_date': start_date,
        'end_date': end_date,
        'department': department,
        'selected_role': selected_role,
        'departments': departments,
        'roles': roles,
        'total_resources': total_resources,
        'avg_utilization': round(avg_utilization, 1),
        'utilization_trend': round(utilization_trend, 1),
        'total_hours': round(total_hours, 0),
        'billable_hours': round(billable_hours, 0),
        'billable_percentage': round(billable_percentage, 1),
        'overutilized_count': overutilized_count,
        'underutilized_count': underutilized_count,
    }
    
    return render(request, 'analytics/utilization_report.html', context)

@login_required
def cost_tracking_report(request):
    """Display cost tracking and budget analysis"""
    cost_service = CostTrackingService()    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_status = request.GET.get('project_status', '')
    selected_client = request.GET.get('client', '')
    
    # Convert string dates to date objects
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Update costs for all projects
    cost_service.update_project_costs()
    
    # Debug logging for processed filters
    print(f"DEBUG: Processed filter parameters:")
    print(f"  start_date_obj: {start_date_obj}")
    print(f"  end_date_obj: {end_date_obj}")
    print(f"  project_status: '{project_status}' (will be None if empty)")
    print(f"  selected_client: '{selected_client}' (will be None if empty)")
    
    # Get cost variance report with filters
    cost_report = cost_service.get_cost_variance_report(
        start_date=start_date_obj,
        end_date=end_date_obj,
        project_status=project_status if project_status else None,
        client=selected_client if selected_client else None
    )
    print(f"DEBUG: Cost report returned {len(cost_report)} projects")
    
    # Calculate summary statistics
    total_estimated = sum(item['estimated_cost'] for item in cost_report)
    total_actual = sum(item['actual_cost'] for item in cost_report)
    total_variance = total_estimated - total_actual
    total_budget = sum(item['budget'] for item in cost_report if item['budget'])
    
    print(f"DEBUG: Calculated totals:")
    print(f"  total_budget: ${total_budget}")
    print(f"  total_actual: ${total_actual}")
    print(f"  total_estimated: ${total_estimated}")
    
    projects_over_budget = len([item for item in cost_report if item['variance'] < 0])
    
    # Calculate additional metrics for the template
    budget_variance = total_budget - total_actual if total_budget else 0
    budget_utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0
    remaining_budget = total_budget - total_actual if total_budget else 0
    
    # Calculate average hourly rate
    resources = Resource.objects.filter(cost_per_hour__isnull=False)
    avg_hourly_rate = resources.aggregate(avg=models.Avg('cost_per_hour'))['avg'] or 0
    
    # Calculate cost trend (simplified - could be enhanced with historical data)
    cost_trend = 0  # Placeholder for now
      # Generate budget alerts
    budget_alerts = []
    for item in cost_report:
        if item['variance'] < 0:
            budget_alerts.append(f"{item['project'].name} is over budget by ${abs(item['variance']):,.0f}")
        elif item['budget_utilization'] > 90:
            budget_alerts.append(f"{item['project'].name} has used {item['budget_utilization']:.1f}% of budget")
      # Get unique clients for filter
    clients = list(set([p.manager.username for p in Project.objects.filter(manager__isnull=False)]))
    
    # Prepare project cost data for the table
    project_costs = []
    for item in cost_report:
        project = item['project']
        total_hours = sum(entry.hours for task in project.tasks.all() for entry in task.time_entries.all())
        client_name = project.manager.username if project.manager else '-'
        
        project_costs.append({
            'name': project.name,
            'description': project.description,
            'client': client_name,
            'status': project.status,
            'get_status_display': project.get_status_display(),
            'budget': item['budget'],
            'actual_cost': item['actual_cost'],
            'variance': item['variance'],
            'budget_percentage': item['budget_utilization'],
            'total_hours': total_hours,
        })    # Prepare resource cost data for the table
    resource_costs = []
    for resource in Resource.objects.filter(cost_per_hour__isnull=False):
        hours_logged = sum(entry.hours for entry in resource.time_entries.all())
        # Use Decimal arithmetic to avoid type conflicts
        total_cost = hours_logged * resource.cost_per_hour if resource.cost_per_hour else Decimal('0')
        # For now, assume all hours are billable and use a simple profit margin calculation
        billable_hours = hours_logged  # Could be enhanced with actual billable hours tracking
        markup_multiplier = Decimal('1.5')  # 50% markup
        revenue_generated = billable_hours * (resource.cost_per_hour * markup_multiplier) if resource.cost_per_hour else Decimal('0')
        profit_margin = float((revenue_generated - total_cost) / revenue_generated * 100) if revenue_generated > 0 else 0
        
        resource_costs.append({
            'name': resource.name,
            'department': resource.department,
            'role': resource.role,
            'hourly_rate': resource.cost_per_hour,
            'hours_logged': hours_logged,
            'total_cost': total_cost,
            'billable_hours': billable_hours,
            'revenue_generated': revenue_generated,
            'profit_margin': profit_margin,
        })
    
    context = {
        'cost_report': cost_report,
        'project_costs': project_costs,  # For the project table
        'resource_costs': resource_costs,  # For the resource table
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'actual_costs': total_actual,  # Template expects this name
        'total_variance': total_variance,
        'total_budget': total_budget,
        'budget_variance': budget_variance,
        'budget_utilization': budget_utilization,
        'remaining_budget': remaining_budget,
        'avg_hourly_rate': avg_hourly_rate,
        'cost_trend': cost_trend,
        'projects_over_budget': projects_over_budget,
        'overbudget_projects': projects_over_budget,  # Template expects this name
        'total_projects': len(cost_report),
        'budget_alerts': budget_alerts,
        'start_date': start_date,
        'end_date': end_date,
        'project_status': project_status,
        'selected_client': selected_client,
        'clients': clients,
    }
    
    return render(request, 'analytics/cost_report.html', context)

@login_required
def export_report(request, report_type):
    """Export reports to PDF or Excel"""
    export_service = ReportExportService()
    
    format_type = request.GET.get('format', 'pdf')  # pdf or excel
    
    try:
        if report_type == 'utilization':
            if format_type == 'excel':
                response = export_service.export_utilization_excel()
            else:
                response = export_service.export_utilization_pdf()
        
        elif report_type == 'cost':
            if format_type == 'excel':
                response = export_service.export_cost_excel()
            else:
                response = export_service.export_cost_pdf()
        
        elif report_type == 'forecast':
            if format_type == 'excel':
                response = export_service.export_forecast_excel()
            else:
                response = export_service.export_forecast_pdf()
        
        else:
            return JsonResponse({'error': 'Invalid report type'})
        
        return response
    
    except Exception as e:
        return JsonResponse({'error': str(e)})

# AI-Powered Analytics Views

@login_required
def ai_skill_recommendations(request):
    """Generate AI-powered skill recommendations"""
    if request.method == 'GET':
        skill_service = AISkillRecommendationService()
        force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
        
        recommendations = skill_service.generate_skill_recommendations(force_refresh=force_refresh)
        
        return JsonResponse({
            'success': True,
            'recommendations': recommendations
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def ai_resource_allocation_suggestions(request, task_id):
    """Generate AI-powered resource allocation suggestions for a specific task"""
    if request.method == 'GET':
        allocation_service = AIResourceAllocationService()
        force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
        
        suggestions = allocation_service.suggest_optimal_resource_allocation(
            task_id=task_id, 
            force_refresh=force_refresh
        )
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required  
def ai_enhanced_forecasts(request):
    """Generate AI-enhanced resource demand forecasts"""
    if request.method == 'GET':
        # Generate statistical forecasts first
        analytics_service = PredictiveAnalyticsService()
        days_ahead = int(request.GET.get('days_ahead', 30))
        
        forecasts = analytics_service.generate_resource_demand_forecast(
            days_ahead=days_ahead, 
            include_ai_enhancement=True
        )
        
        return JsonResponse({
            'success': True,
            'forecasts': forecasts
        })
    
    elif request.method == 'POST':
        # Allow custom business context
        try:
            data = json.loads(request.body)
            business_context = data.get('business_context', '')
            
            # Get recent statistical forecasts
            recent_forecasts = ResourceDemandForecast.objects.filter(
                forecast_date__gte=timezone.now().date() - timedelta(days=7)
            )
            
            if not recent_forecasts.exists():
                return JsonResponse({'error': 'No recent forecasts available. Generate statistical forecasts first.'})
            
            # Enhance with AI
            forecast_service = AIForecastEnhancementService()
            enhanced_forecasts = forecast_service.enhance_resource_demand_forecast(
                list(recent_forecasts), 
                business_context
            )
            
            return JsonResponse({
                'success': True,
                'enhanced_forecasts': enhanced_forecasts
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def ai_strategic_recommendations(request):
    """Generate strategic recommendations based on enhanced forecasts"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enhanced_forecasts = data.get('enhanced_forecasts', {})
            
            forecast_service = AIForecastEnhancementService()
            strategic_recommendations = forecast_service.generate_strategic_recommendations(enhanced_forecasts)
            
            return JsonResponse({
                'success': True,
                'recommendations': strategic_recommendations
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def ai_analytics_dashboard(request):
    """AI Analytics Dashboard view"""
    # Get available tasks for resource allocation analysis
    tasks = Task.objects.filter(status__in=['not_started', 'in_progress']).select_related('project')
    
    # Get recent AI recommendations count
    recent_skill_recommendations = AISkillRecommendation.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    recent_allocation_suggestions = AIResourceAllocationSuggestion.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    recent_forecast_adjustments = AIForecastAdjustment.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    context = {
        'tasks': tasks,
        'recent_skill_recommendations': recent_skill_recommendations,
        'recent_allocation_suggestions': recent_allocation_suggestions,
        'recent_forecast_adjustments': recent_forecast_adjustments,
        'ai_available': gemini_service.is_available(),
    }
    
    return render(request, 'analytics/ai_analytics.html', context)
