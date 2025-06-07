from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import models
from datetime import timedelta
import json

from .services import PredictiveAnalyticsService, UtilizationTrackingService, CostTrackingService
from .models import ResourceDemandForecast, HistoricalUtilization, SkillDemandAnalysis
from .export_services import ReportExportService
from resources.models import Resource
from projects.models import Project

@login_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    # Get recent forecasts
    recent_forecasts = ResourceDemandForecast.objects.all()[:5]
    
    # Get skill demand analysis
    skill_analyses = SkillDemandAnalysis.objects.filter(
        analysis_date=timezone.now().date()
    )[:10]
    
    # Get utilization trends
    utilization_service = UtilizationTrackingService()
    utilization_trends = utilization_service.get_utilization_trends(days=30)
      # Get cost tracking data
    cost_service = CostTrackingService()
    cost_report = cost_service.get_cost_variance_report()
    
    # Calculate summary metrics
    total_resources = Resource.objects.count()
    total_projects = Project.objects.count()
    
    context = {
        'recent_forecasts': recent_forecasts,
        'skill_analyses': skill_analyses,
        'utilization_trends': utilization_trends,
        'cost_report': cost_report[:10],  # Top 10 projects
        'total_resources': total_resources,
        'total_projects': total_projects,
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
    
    # GET request - display the forecasting page
    recent_forecasts = ResourceDemandForecast.objects.order_by('-forecast_date')[:10]
    context = {'recent_forecasts': recent_forecasts}
    return render(request, 'analytics/forecasting.html', context)

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
    
    # GET request - display the skill analysis page
    recent_analyses = SkillDemandAnalysis.objects.order_by('-analysis_date')[:20]
    context = {'skill_analyses': recent_analyses}
    return render(request, 'analytics/skill_analysis.html', context)

@login_required
def utilization_report(request):
    """Display utilization report"""
    resources = Resource.objects.all()
    days = int(request.GET.get('days', 30))
    
    utilization_service = UtilizationTrackingService()
    
    # Record today's utilization if not already done
    utilization_service.record_daily_utilization()
    
    # Get trends for each resource
    resource_data = []
    for resource in resources:
        trends = utilization_service.get_utilization_trends(resource, days)
        avg_utilization = trends.aggregate(avg=models.Avg('utilization_percentage'))['avg'] or 0
        
        resource_data.append({
            'resource': resource,
            'avg_utilization': round(avg_utilization, 1),
            'trends': trends[:10]  # Last 10 days
        })
    
    context = {
        'resource_data': resource_data,
        'days': days
    }
    
    return render(request, 'analytics/utilization_report.html', context)

@login_required
def cost_tracking_report(request):
    """Display cost tracking and budget analysis"""
    cost_service = CostTrackingService()
    
    # Update costs for all projects
    cost_service.update_project_costs()
    
    # Get cost variance report
    cost_report = cost_service.get_cost_variance_report()
    
    # Calculate summary statistics
    total_estimated = sum(item['estimated_cost'] for item in cost_report)
    total_actual = sum(item['actual_cost'] for item in cost_report)
    total_variance = total_estimated - total_actual
    
    projects_over_budget = len([item for item in cost_report if item['variance'] < 0])
    
    context = {
        'cost_report': cost_report,
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'total_variance': total_variance,
        'projects_over_budget': projects_over_budget,
        'total_projects': len(cost_report)
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
