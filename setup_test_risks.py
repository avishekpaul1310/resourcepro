#!/usr/bin/env python
"""
Create test risks and scenarios for AI intervention testing
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.models import DynamicRisk, RiskCategory, InterventionScenario
from projects.models import Project
from resources.models import Resource
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

print("=== Creating Test Risks for AI Intervention Testing ===")

# Get or create risk categories
resource_category, _ = RiskCategory.objects.get_or_create(
    name="Resource Management",
    defaults={"description": "Resource allocation and utilization risks"}
)

timeline_category, _ = RiskCategory.objects.get_or_create(
    name="Timeline & Deadlines", 
    defaults={"description": "Project timeline and deadline risks"}
)

quality_category, _ = RiskCategory.objects.get_or_create(
    name="Quality & Standards",
    defaults={"description": "Quality assurance and standards risks"}
)

# Get test project and resources
test_project = Project.objects.filter(name="test project").first()
api_project = Project.objects.filter(name="API Integration").first()
mike_wilson = Resource.objects.filter(name__icontains="Mike").first()
bob_johnson = Resource.objects.filter(name__icontains="Bob").first()

# Create realistic test risks
risks_to_create = [
    {
        'title': 'Critical Deadline for test project',
        'description': 'test project has multiple unfinished tasks and only 8 days until its deadline, increasing the likelihood of missed deadlines and impacting quality, team morale, and client satisfaction.',
        'category': timeline_category,
        'severity': 'high',
        'probability': 0.8,
        'impact_score': 8.5,
        'related_project': test_project,
        'ai_analysis': {
            'affected_items': ['test project', 'Bob Johnson', 'Alice Brown'],
            'suggested_interventions': [
                'reassignment', 'overtime', 'scope_reduction'
            ],
            'risk_factors': ['tight_deadline', 'incomplete_tasks', 'resource_constraints']
        }
    },
    {
        'title': 'Potential Resource Overallocation',
        'description': 'Several team members are involved in multiple projects, increasing the risk of overallocation as project demands increase, potentially impacting timelines, quality, and team morale.',
        'category': resource_category,
        'severity': 'medium',
        'probability': 0.7,
        'impact_score': 6.5,
        'related_resource': mike_wilson,
        'ai_analysis': {
            'affected_items': ['Bob Johnson', 'Jane Smith', 'John Doe', 'Mike Wilson', 'All projects'],
            'suggested_interventions': [
                'reassignment', 'resource_addition', 'training'
            ],
            'utilization_analysis': 'Multiple resources showing increasing utilization'
        }
    },
    {
        'title': 'Communication Breakdown Risk',
        'description': 'Multiple projects and potentially limited time for collaboration increase the risk of communication issues, potentially impacting timelines, quality, and team morale.',
        'category': quality_category,
        'severity': 'medium',
        'probability': 0.6,
        'impact_score': 5.5,
        'ai_analysis': {
            'affected_items': ['All projects', 'All resources'],
            'suggested_interventions': [
                'communication_plan', 'process_improvement', 'training'
            ],
            'risk_triggers': ['multiple_projects', 'limited_collaboration_time']
        }
    },
    {
        'title': 'API Integration Skill Gap',
        'description': 'Advanced API integration requirements may exceed current team capabilities, risking project delays and quality issues.',
        'category': resource_category,
        'severity': 'medium',
        'probability': 0.5,
        'impact_score': 7.0,
        'related_project': api_project,
        'ai_analysis': {
            'affected_items': ['API Integration', 'Development Team'],
            'suggested_interventions': [
                'training', 'external_resource', 'resource_addition'
            ],
            'skill_requirements': ['Advanced API Development', 'Integration Patterns']
        }
    }
]

# Create the risks
created_risks = []
for risk_data in risks_to_create:
    # Check if risk already exists
    existing_risk = DynamicRisk.objects.filter(
        title=risk_data['title']
    ).first()
    
    if not existing_risk:
        risk = DynamicRisk.objects.create(
            title=risk_data['title'],
            description=risk_data['description'],
            category=risk_data['category'],
            severity=risk_data['severity'],
            probability=risk_data['probability'],
            impact_score=risk_data['impact_score'],
            related_project=risk_data.get('related_project'),
            related_resource=risk_data.get('related_resource'),
            ai_analysis=risk_data['ai_analysis'],
            suggested_interventions=risk_data['ai_analysis']['suggested_interventions']
        )
        created_risks.append(risk)
        print(f"✅ Created risk: {risk.title}")
    else:
        print(f"⚪ Risk already exists: {risk_data['title']}")

print(f"\n=== Test Risk Summary ===")
print(f"Total risks in database: {DynamicRisk.objects.count()}")
print(f"Newly created risks: {len(created_risks)}")

# Show risk breakdown by severity
for severity in ['critical', 'high', 'medium', 'low']:
    count = DynamicRisk.objects.filter(severity=severity).count()
    if count > 0:
        print(f"{severity.title()} risks: {count}")

print(f"\n=== Testing Ready Status ===")
print("✅ Critical deadline risk (HIGH) - Ready for overtime/reassignment testing")
print("✅ Resource overallocation risk (MEDIUM) - Ready for reassignment testing") 
print("✅ Communication risk (MEDIUM) - Ready for process improvement testing")
print("✅ Skill gap risk (MEDIUM) - Ready for training/external resource testing")

print(f"\n=== Next Steps ===")
print("1. Go to http://localhost:8000/dashboard/")
print("2. Look for the 'Key Risks' section")
print("3. Click 'Simulate Solutions' on any risk")
print("4. Test each intervention scenario")
print("5. Verify AI provides realistic results")

print(f"\n=== Quick Test Commands ===")
print("# Check risks via Django admin:")
print("http://localhost:8000/admin/dashboard/dynamicrisk/")
print("\n# Check interventions via Django admin:")
print("http://localhost:8000/admin/dashboard/interventionscenario/")
