#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from allocation.models import Task, Assignment, Resource

# Test the end-to-end assignment flow
client = Client()

# Get the admin user
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    print("Admin user not found. Creating...")
    user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')

# Log in as admin
client.force_login(user)

# Get current state
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

print(f"Current state:")
print(f"  Total tasks: {Task.objects.count()}")
print(f"  Total assignments: {Assignment.objects.count()}")
print(f"  Unassigned tasks: {unassigned_tasks.count()}")

if unassigned_tasks.count() == 0:
    print("\nNo unassigned tasks! Creating a test scenario...")
    # Unassign a task to test
    if Assignment.objects.exists():
        test_assignment = Assignment.objects.first()
        task_id = test_assignment.task.id
        test_assignment.delete()
        print(f"Unassigned task {task_id} for testing")
        unassigned_tasks = Task.objects.exclude(id__in=Assignment.objects.values_list('task_id', flat=True))

# Test AI suggestions for the first unassigned task
if unassigned_tasks:
    test_task = unassigned_tasks.first()
    print(f"\n=== Testing AI suggestions for Task {test_task.id}: {test_task.name} ===")
    
    response = client.get(f'/allocation/api/ai-suggestions/{test_task.id}/')
    print(f"AI suggestions response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success') and data.get('suggestions'):
            suggestions = data['suggestions']
            print(f"Got {len(suggestions)} suggestions")
            
            # Try to assign the first suggestion
            if suggestions:
                best_suggestion = suggestions[0]
                print(f"\nBest suggestion:")
                print(f"  Resource: {best_suggestion['resource']['name']} ({best_suggestion['resource']['role']})")
                print(f"  Match score: {best_suggestion['match_score']}")
                print(f"  Reasoning: {best_suggestion['reasoning'][:100]}...")
                
                # Test the assignment
                assignment_data = {
                    'task_id': test_task.id,
                    'resource_id': best_suggestion['resource']['id'],
                    'project_name': test_task.project.name if test_task.project else 'No Project'
                }
                
                print(f"\n=== Testing assignment ===")
                print(f"Assignment data: {assignment_data}")
                
                assignment_response = client.post('/allocation/api/assign-task/', 
                                                data=json.dumps(assignment_data),
                                                content_type='application/json')
                
                print(f"Assignment response status: {assignment_response.status_code}")
                
                if assignment_response.status_code == 200:
                    assignment_result = assignment_response.json()
                    print(f"Assignment success: {assignment_result.get('success', False)}")
                    print(f"Message: {assignment_result.get('message', 'No message')}")
                    
                    if assignment_result.get('debug_info'):
                        print(f"Debug info: {assignment_result['debug_info']}")
                    
                    if assignment_result.get('success'):
                        print("✅ Assignment successful!")
                        
                        # Verify the assignment was created
                        new_assignment = Assignment.objects.filter(task_id=test_task.id).first()
                        if new_assignment:
                            print(f"✅ Assignment verified in database: Task {new_assignment.task.id} -> Resource {new_assignment.resource.name}")
                        else:
                            print("❌ Assignment not found in database")
                        
                        # Clean up - unassign the task
                        if new_assignment:
                            assignment_id = new_assignment.id
                            new_assignment.delete()
                            print(f"🧹 Cleaned up assignment {assignment_id}")
                    else:
                        print("❌ Assignment failed")
                        if assignment_result.get('error'):
                            print(f"Error: {assignment_result['error']}")
                else:
                    print(f"❌ Assignment request failed: {assignment_response.content.decode()}")
        else:
            print("❌ No suggestions returned")
    else:
        print(f"❌ AI suggestions request failed: {response.content.decode()}")
        
else:
    print("❌ No unassigned tasks available for testing")
