#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from allocation.models import Task, Assignment, Resource

# Test the "assign all" functionality
client = Client()

# Get the admin user
user = User.objects.get(username='admin')
client.force_login(user)

# Get unassigned tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

print(f"Testing 'Assign All' functionality with {unassigned_tasks.count()} unassigned tasks")

if unassigned_tasks.count() >= 2:
    test_tasks = list(unassigned_tasks[:2])  # Test with first 2 tasks
    
    print(f"\nTest tasks:")
    for task in test_tasks:
        print(f"  - Task {task.id}: {task.name}")
    
    # Get AI suggestions for all test tasks
    all_suggestions = []
    for task in test_tasks:
        response = client.get(f'/allocation/api/ai-suggestions/{task.id}/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('suggestions'):
                suggestion = data['suggestions'][0]  # Get best suggestion
                all_suggestions.append({
                    'task': {
                        'id': task.id,
                        'name': task.name,
                        'project_name': task.project.name if task.project else 'No Project'
                    },
                    'suggestion': suggestion
                })
    
    print(f"\nGot suggestions for {len(all_suggestions)} tasks")
    
    # Test bulk assignment
    if len(all_suggestions) >= 2:
        assignments_to_make = []
        for item in all_suggestions:
            assignments_to_make.append({
                'task_id': item['task']['id'],
                'resource_id': item['suggestion']['resource']['id'],
                'project_name': item['task']['project_name']
            })
        
        print(f"\n=== Testing bulk assignment ===")
        print(f"Assignments to make: {len(assignments_to_make)}")
        
        success_count = 0
        for assignment_data in assignments_to_make:
            print(f"\nAssigning Task {assignment_data['task_id']} -> Resource {assignment_data['resource_id']}")
            
            response = client.post('/allocation/api/assign-task/', 
                                 data=json.dumps(assignment_data),
                                 content_type='application/json')
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    success_count += 1
                    print(f"  ✅ Success")
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"  ❌ Request failed: {response.status_code}")
        
        print(f"\n=== Results ===")
        print(f"Successfully assigned {success_count} of {len(assignments_to_make)} tasks")
        
        if success_count == len(assignments_to_make):
            print("🎉 All assignments successful!")
        elif success_count > 0:
            print("⚠️ Partial success")
        else:
            print("❌ All assignments failed")
        
        # Clean up - remove test assignments
        print(f"\n🧹 Cleaning up test assignments...")
        for assignment_data in assignments_to_make:
            assignment = Assignment.objects.filter(task_id=assignment_data['task_id']).first()
            if assignment:
                assignment.delete()
                print(f"  Removed assignment for task {assignment_data['task_id']}")
        
        print("✅ Cleanup complete")
    else:
        print("❌ Not enough suggestions for bulk assignment test")
else:
    print("❌ Need at least 2 unassigned tasks for bulk assignment test")
