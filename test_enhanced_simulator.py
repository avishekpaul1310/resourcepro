#!/usr/bin/env python3
"""
Test script for the enhanced intervention simulator APIs
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from dashboard.models import Project, Resource, Task
from allocation.models import Assignment
from resources.models import Skill

def test_intervention_simulator_apis():
    print("🧪 Testing Enhanced Intervention Simulator APIs...")
    
    client = Client()
      # Create or get test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'password': 'testpass'}
    )
    if created:
        user.set_password('testpass')
        user.save()
    
    client.login(username='testuser', password='testpass')
    
    # Test 1: Project Resources API
    print("\n1. Testing Project Resources API...")
    response = client.get('/dashboard/api/project-resources/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Resources count: {len(data.get('resources', []))}")
        if data.get('resources'):
            resource = data['resources'][0]
            print(f"   Sample resource: {resource.get('name')} ({resource.get('role')})")
            print(f"   Has skills: {'skills' in resource}")
            print(f"   Has hourly_rate: {'hourly_rate' in resource}")
    
    # Test 2: Project Tasks API (if any projects exist)
    print("\n2. Testing Project Tasks API...")
    projects = Project.objects.all()
    if projects.exists():
        project = projects.first()
        response = client.get(f'/dashboard/api/project-tasks/?project_id={project.id}')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Tasks count: {len(data.get('tasks', []))}")
            print(f"   Project: {data.get('project_name')}")
    else:
        print("   No projects found to test with")
    
    # Test 3: Enhanced simulation context
    print("\n3. Testing Enhanced Simulation Context...")
    from dashboard.ai_services import intervention_simulator_service
    
    scenario_data = {
        'scenario_type': 'overtime',
        'title': 'Test Overtime Scenario',
        'description': 'Testing enhanced context gathering',
        'project_id': projects.first().id if projects.exists() else None
    }
    
    try:
        context = intervention_simulator_service._gather_intervention_context(scenario_data)
        print(f"   Context keys: {list(context.keys())}")
        print(f"   Has project_tasks: {'project_tasks' in context}")
        print(f"   Has project_resources: {'project_resources' in context}")
        if context.get('target_project'):
            print(f"   Target project: {context['target_project'].get('name')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API Testing Complete!")

if __name__ == "__main__":
    test_intervention_simulator_apis()
