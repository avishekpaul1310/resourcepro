#!/usr/bin/env python
import os
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from allocation.models import Task, Assignment, Resource

# Test the AI suggestions API directly
client = Client()

# Create a test user if not exists
try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create_user('testuser', 'test@test.com', 'testpass')

# Log in the client
client.login(username='testuser', password='testpass')

# Get an unassigned task
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)[:3]

print(f"Testing AI suggestions API with {len(unassigned_tasks)} unassigned tasks:")

for task in unassigned_tasks:
    print(f"\nTesting task {task.id}: {task.name}")
    
    # Test AI suggestions endpoint
    response = client.get(f'/allocation/api/ai-suggestions/{task.id}/')
    print(f"AI suggestions response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Suggestions success: {data.get('success', False)}")
        if data.get('suggestions'):
            print(f"Number of suggestions: {len(data['suggestions'])}")
            if data['suggestions']:
                best_suggestion = data['suggestions'][0]
                print(f"Best suggestion - Resource: {best_suggestion.get('resource_name')}, Score: {best_suggestion.get('score')}")
    else:
        print(f"Error response: {response.content.decode()}")

# Test assignment API
print("\n=== Testing Assignment API ===")
if unassigned_tasks:
    task = unassigned_tasks[0]
    resources = Resource.objects.all()[:3]
    
    for resource in resources:
        print(f"\nTesting assignment: Task {task.id} -> Resource {resource.id} ({resource.name})")
        
        assignment_data = {
            'task_id': task.id,
            'resource_id': resource.id,
            'project_name': task.project.name if task.project else 'Unknown Project'
        }
        
        response = client.post('/allocation/api/assign-task/', 
                              data=json.dumps(assignment_data),
                              content_type='application/json')
        
        print(f"Assignment response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Assignment success: {data.get('success', False)}")
            print(f"Response message: {data.get('message', 'No message')}")
            if data.get('debug_info'):
                print(f"Debug info: {data['debug_info']}")
            
            # If successful, try to unassign to clean up
            if data.get('success'):
                unassign_response = client.post('/allocation/api/unassign-task/',
                                               data=json.dumps({'assignment_id': data.get('assignment_id')}),
                                               content_type='application/json')
                print(f"Cleanup unassign status: {unassign_response.status_code}")
        else:
            print(f"Error response: {response.content.decode()}")
        
        break  # Only test the first resource to avoid multiple assignments
