#!/usr/bin/env python
"""
Test script for the Enhanced Risk Management & Dynamic Intervention System
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.models import Project, Task, Resource, InterventionScenario, RiskCategory, DynamicRisk
from dashboard.ai_services import EnhancedRiskAnalysisService
from projects.models import Project as ProjectModel

def test_enhanced_risk_system():
    """Test the enhanced risk analysis and intervention system"""
    print("🧪 Testing Enhanced Risk Management & Dynamic Intervention System")
    print("=" * 80)
    
    # Test risk analysis service
    service = EnhancedRiskAnalysisService()
    
    # Get test project data
    project = Project.objects.first()
    if not project:
        print("❌ No projects found for testing")
        return
    
    print(f"✅ Testing with project: {project.name}")
    
    # Create sample project context
    context = {
        'project_id': str(project.id),
        'project_name': project.name,
        'timeline': {
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'days_remaining': 30
        },        'resources': {
            'total': Resource.objects.count(),
            'allocated': Resource.objects.filter(assignments__task__project=project).distinct().count(),
            'high_utilization': 0  # Placeholder - utilization calculated differently
        },
        'tasks': {
            'total': Task.objects.filter(project=project).count(),
            'completed': Task.objects.filter(project=project, status='completed').count(),
            'overdue': Task.objects.filter(project=project, end_date__lt=datetime.now().date()).count()
        },
        'budget': {
            'allocated': float(project.budget) if hasattr(project, 'budget') and project.budget else 100000,
            'spent': 45000,
            'remaining': 55000
        }
    }
    
    print(f"\n📊 Project Context:")
    print(json.dumps(context, indent=2))
    
    print(f"\n🔍 Running Comprehensive Risk Analysis...")
    
    # Test risk analysis
    risks = service.analyze_comprehensive_risks(context)
    
    if not risks:
        print("⚠️ No risks identified (AI service may be unavailable)")
        test_manual_risk_scenarios()
        return
    
    print(f"\n✅ Found {len(risks)} risks:")
    
    for i, risk in enumerate(risks, 1):
        print(f"\n🚨 Risk #{i}: {risk.get('title', 'Unknown')}")
        print(f"   Category: {risk.get('category', 'Unknown')}")
        print(f"   Severity: {risk.get('severity', 'Unknown')}")
        print(f"   Probability: {risk.get('probability', 0):.2f}")
        print(f"   Impact Score: {risk.get('impact_score', 0):.1f}")
        
        # Test intervention generation
        interventions = risk.get('dynamic_interventions', [])
        if interventions:
            print(f"   🛠️ Suggested Interventions ({len(interventions)}):")
            for j, intervention in enumerate(interventions, 1):
                print(f"      {j}. {intervention.get('name', 'Unknown')}")
                print(f"         Success Rate: {intervention.get('success_probability', 0):.0%}")
                print(f"         Cost: ${intervention.get('estimated_cost', 0):.0f}")
                print(f"         Time: {intervention.get('time_to_implement', 'Unknown')}")
        else:
            print("   ⚠️ No interventions suggested")
    
    # Test intervention scenario creation
    print(f"\n💾 Testing Intervention Scenario Storage...")
    test_intervention_storage(risks)
    
    # Test risk categories
    print(f"\n📂 Testing Risk Categories...")
    test_risk_categories()
    
    print(f"\n🎉 Enhanced Risk System Test Complete!")

def test_manual_risk_scenarios():
    """Test the system with manually created risk scenarios"""
    print("\n🔧 Testing with Manual Risk Scenarios...")
    
    # Test different risk categories and their interventions
    risk_scenarios = [
        {
            'category': 'technical',
            'title': 'Legacy System Integration Issues',
            'severity': 'high',
            'probability': 0.8,
            'impact_score': 8.0
        },
        {
            'category': 'team',
            'title': 'Team Communication Breakdown',
            'severity': 'medium',
            'probability': 0.6,
            'impact_score': 6.0
        },
        {
            'category': 'external',
            'title': 'Client Approval Bottlenecks',
            'severity': 'high',
            'probability': 0.7,
            'impact_score': 7.0
        }
    ]
    
    service = EnhancedRiskAnalysisService()
    
    for i, risk in enumerate(risk_scenarios, 1):
        print(f"\n🧪 Testing Risk Scenario #{i}: {risk['title']}")
        
        # Generate interventions for this risk
        context = {'project_id': '1', 'resources': {'total': 5}}
        enhanced_risk = service._enhance_risk_analysis(risk, context)
        
        interventions = enhanced_risk.get('dynamic_interventions', [])
        print(f"   Generated {len(interventions)} interventions:")
        
        for j, intervention in enumerate(interventions, 1):
            print(f"      {j}. {intervention.get('name', 'Unknown')}")
            print(f"         Type: {intervention.get('type', 'Unknown')}")
            print(f"         Success Rate: {intervention.get('success_probability', 0):.0%}")

def test_intervention_storage(risks):
    """Test storing intervention scenarios in the database"""
    if not risks:
        print("   ⚠️ No risks to store")
        return
    
    project = Project.objects.first()
    if not project:
        print("   ❌ No project available for storage test")
        return
    
    # Create an intervention scenario based on first risk
    risk = risks[0]
    interventions = risk.get('dynamic_interventions', [])
    
    if not interventions:
        print("   ⚠️ No interventions to store")
        return
    
    intervention = interventions[0]
    
    scenario = InterventionScenario.objects.create(
        scenario_type=intervention.get('type', 'custom'),
        title=f"AI Intervention: {risk.get('title', 'Unknown Risk')}",
        description=intervention.get('description', 'AI-generated intervention'),
        related_project=project,
        simulation_data={
            'risk_data': risk,
            'intervention_data': intervention
        },
        success_probability=intervention.get('success_probability', 0.7),
        estimated_cost=intervention.get('estimated_cost', 1000),
        ai_generated=True
    )
    
    print(f"   ✅ Created intervention scenario: {scenario.title}")
    print(f"      ID: {scenario.id}")
    print(f"      Type: {scenario.scenario_type}")
    print(f"      Success Rate: {scenario.success_probability:.0%}")

def test_risk_categories():
    """Test risk category functionality"""
    categories = [
        ('resource', 'Resource & Allocation'),
        ('technical', 'Technical & Quality'),
        ('external', 'External Dependencies'),
        ('team', 'Team Dynamics'),
        ('business', 'Business & Strategic'),
        ('operational', 'Operational'),
        ('financial', 'Financial & Budget'),
        ('timeline', 'Timeline & Schedule'),
        ('scope', 'Scope & Requirements'),
        ('quality', 'Quality & Standards')    ]
    
    for code, name in categories:
        category, created = RiskCategory.objects.get_or_create(
            risk_type=code,
            defaults={'name': name, 'description': f'{name} related risks'}
        )
        
        if created:
            print(f"   ✅ Created risk category: {name}")
        else:
            print(f"   📂 Risk category exists: {name}")
    
    total_categories = RiskCategory.objects.count()
    print(f"   📊 Total risk categories: {total_categories}")

if __name__ == '__main__':
    test_enhanced_risk_system()
