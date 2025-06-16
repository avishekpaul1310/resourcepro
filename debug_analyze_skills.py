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
def analyze_skills_debug(request):
    """Debug version of analyze_skills view"""
    print("=== DEBUG: analyze_skills view called ===")
    
    # GET request - display the skill analysis page
    time_period = int(request.GET.get('time_period', 30))
    sort_by = request.GET.get('sort_by', 'demand')
    
    print(f"Time period: {time_period}, Sort by: {sort_by}")
    
    # Get skill demand analyses
    recent_analyses = SkillDemandAnalysis.objects.order_by('-analysis_date')[:20]
    print(f"Found {recent_analyses.count()} skill analyses")
    
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
    
    print(f"Top 3 skills after sorting: {[s['skill_name'] for s in skill_demand[:3]]}")
    
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
    
    print(f"Found {len(skill_gaps)} skill gaps")
    
    # Calculate trending skills (simplified - based on demand score)
    trending_up = [skill for skill in skill_demand if skill['demand_score'] > 80][:5]
    trending_down = [skill for skill in skill_demand if skill['demand_score'] < 30][:5]
    
    print(f"Trending up: {len(trending_up)}, Trending down: {len(trending_down)}")
    
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
    
    print(f"Summary: total={total_skills}, high_demand={high_demand_skills}, avg_score={avg_demand_score:.1f}")
    
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
    
    print(f"Context keys: {list(context.keys())}")
    print("=== DEBUG: End analyze_skills view ===")
    
    return render(request, 'analytics/skill_analysis.html', context)
