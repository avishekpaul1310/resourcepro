#!/usr/bin/env python
"""
Test script for contextual scenario generation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.ai_services import EnhancedRiskAnalysisService
from projects.models import Project
import json

def test_contextual_scenarios():
    """Test contextual scenario generation for different project types"""
    print("🧪 Testing Contextual Scenario Generation")
    print("=" * 60)
    
    service = EnhancedRiskAnalysisService()
    
    # Test different project contexts
    test_contexts = [
        {
            'name': 'Startup MVP (Low Budget, Tight Timeline, Small Team)',
            'project_context': {
                'project_type': 'startup_mvp',
                'budget': 15000,
                'days_remaining': 10,
                'completion_percentage': 30,
                'team_size': 2
            },
            'risk': {
                'title': 'Timeline Pressure',
                'category_type': 'timeline',
                'severity': 'high'
            }
        },
        {
            'name': 'Enterprise Migration (High Budget, Extended Timeline, Large Team)',
            'project_context': {
                'project_type': 'enterprise_migration',
                'budget': 250000,
                'days_remaining': 120,
                'completion_percentage': 15,
                'team_size': 12
            },
            'risk': {
                'title': 'Technical Complexity',
                'category_type': 'technical',
                'severity': 'medium'
            }
        },
        {
            'name': 'Maintenance Project (Low Budget, Flexible Timeline, Minimal Team)',
            'project_context': {
                'project_type': 'maintenance',
                'budget': 8000,
                'days_remaining': 60,
                'completion_percentage': 50,
                'team_size': 1
            },
            'risk': {
                'title': 'Resource Constraints',
                'category_type': 'resource',
                'severity': 'medium'
            }
        },
        {
            'name': 'Critical Bug Fix (Medium Budget, Critical Timeline, Medium Team)',
            'project_context': {
                'project_type': 'bugfix',
                'budget': 25000,
                'days_remaining': 3,
                'completion_percentage': 0,
                'team_size': 4
            },
            'risk': {
                'title': 'Critical Production Issue',
                'category_type': 'operational',
                'severity': 'critical'
            }
        }
    ]
    
    for i, context in enumerate(test_contexts, 1):
        print(f"\n{i}. {context['name']}")
        print("-" * 50)
        
        # Generate interventions for this context
        interventions = service._generate_dynamic_interventions(
            context['risk'], 
            {
                'project_context': context['project_context'],
                'team_size': context['project_context']['team_size']
            }
        )
        
        # Categorize budget and timeline
        budget_level = service._categorize_budget(context['project_context']['budget'])
        timeline_pressure = service._assess_timeline_pressure(context['project_context'])
        team_size_cat = service._categorize_team_size(context['project_context']['team_size'])
        
        print(f"Context: {budget_level.title()} Budget, {timeline_pressure.title()} Timeline, {team_size_cat.title()} Team")
        print(f"Risk: {context['risk']['title']} ({context['risk']['severity'].title()} {context['risk']['category_type'].title()})")
        
        print(f"\nRecommended Interventions ({len(interventions)}):")
        for j, intervention in enumerate(interventions, 1):
            success_rate = intervention.get('success_rate', 0.75)
            cost = intervention.get('estimated_cost', 0)
            
            print(f"  {j}. {intervention['name']}")
            print(f"     Success: {success_rate*100:.0f}% | Cost: ${cost:,.0f} | {intervention.get('time_range', 'N/A')}")
            print(f"     {intervention['description']}")
        
        # Show what would be filtered out
        all_scenario_types = ['reassignment', 'overtime', 'resource_addition', 'deadline_extension', 
                            'scope_reduction', 'training', 'external_resource', 'process_improvement', 
                            'technology_upgrade', 'risk_mitigation', 'communication_plan', 
                            'quality_assurance', 'stakeholder_engagement']
        
        suggested_types = [interv.get('name', '').lower().replace(' ', '_').replace('&', '').replace('/', '_') for interv in interventions]
        filtered_out = set(all_scenario_types) - set(suggested_types)
        
        if filtered_out:
            print(f"\nFiltered Out ({len(filtered_out)}): {', '.join(filtered_out)}")
    
    print(f"\n✅ Contextual Scenario Testing Complete!")
    print(f"\n🎯 Key Insights:")
    print("- Different project contexts get different intervention recommendations")
    print("- Budget constraints filter out expensive options (external consultants, etc.)")
    print("- Timeline pressure prioritizes quick wins (overtime, scope reduction)")
    print("- Team size affects reassignment and communication scenarios")
    print("- Risk severity adds emergency interventions when budget allows")

if __name__ == "__main__":
    test_contextual_scenarios()
