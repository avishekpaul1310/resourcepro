#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from allocation.models import Task, Assignment, Resource
from analytics.ai_services import AIResourceAllocationService

# Test the improved utilization filtering
client = Client()
user = User.objects.get(username='admin')
client.force_login(user)

print("=== Testing Improved Utilization Protection ===")

# Get unassigned tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

if unassigned_tasks:
    test_task = unassigned_tasks.first()
    print(f"\nTest task: {test_task.id} - {test_task.name}")
    print(f"Estimated hours: {test_task.estimated_hours}")
    print(f"Duration: {test_task.start_date} to {test_task.end_date}")
    
    # Test the AI service directly to see utilization filtering
    ai_service = AIResourceAllocationService()
    
    print(f"\n=== Resource Utilization Analysis ===")
    all_resources = Resource.objects.all()[:10]  # Check first 10 resources
    
    for resource in all_resources:
        current_util = resource.current_utilization()
        projected_util = ai_service._calculate_projected_utilization(resource, test_task)
        
        # Check if resource would be considered available
        is_available = current_util < 85 and projected_util < 95
        status = "✅ AVAILABLE" if is_available else "❌ EXCLUDED"
        
        print(f"{resource.name} ({resource.role}):")
        print(f"  Current: {current_util}%")
        print(f"  Projected: {projected_util}%")
        print(f"  Status: {status}")
        print()
    
    print(f"\n=== AI Suggestions with Utilization Protection ===")
    
    # Get AI suggestions
    response = client.get(f'/allocation/api/ai-suggestions/{test_task.id}/')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('suggestions'):
            suggestions = data['suggestions']
            print(f"✅ AI returned {len(suggestions)} suggestion(s)")
            
            for i, suggestion in enumerate(suggestions, 1):
                resource_info = suggestion['resource']
                print(f"Suggestion {i}:")
                print(f"  Resource: {resource_info['name']} ({resource_info['role']})")
                print(f"  Match Score: {suggestion['match_score']}")
                print(f"  Reasoning: {suggestion['reasoning'][:100]}...")
                
                # Verify this resource meets utilization criteria
                resource = Resource.objects.get(id=resource_info['id'])
                current_util = resource.current_utilization()
                projected_util = ai_service._calculate_projected_utilization(resource, test_task)
                print(f"  Utilization check: {current_util}% -> {projected_util}%")
                
                if current_util < 85 and projected_util < 95:
                    print(f"  ✅ Utilization criteria met")
                else:
                    print(f"  ⚠️  WARNING: Utilization criteria not met!")
                print()
        else:
            print("❌ No suggestions returned")
            if data.get('error'):
                print(f"Error: {data['error']}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.content.decode())

else:
    print("❌ No unassigned tasks available for testing")
