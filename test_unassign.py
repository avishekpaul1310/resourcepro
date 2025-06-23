#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from allocation.models import Task, Assignment, Resource

# Test the unassign functionality
client = Client()

# Get the admin user
user = User.objects.get(username='admin')
client.force_login(user)

print("=== Testing Unassign Task Functionality ===")

# Get an existing assignment to test unassignment
existing_assignments = Assignment.objects.all()[:3]

if existing_assignments:
    test_assignment = existing_assignments[0]
    print(f"\nTest assignment: Task {test_assignment.task.id} ({test_assignment.task.name}) -> Resource {test_assignment.resource.name}")
    
    # Test unassignment
    unassign_data = {
        'assignment_id': test_assignment.id
    }
    
    print(f"\n=== Testing unassign API ===")
    response = client.post('/allocation/api/unassign-task/',
                          data=json.dumps(unassign_data),
                          content_type='application/json')
    
    print(f"Unassign response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('success'):
            print("✅ Unassignment successful!")
            
            # Verify the assignment was removed
            assignment_exists = Assignment.objects.filter(id=test_assignment.id).exists()
            if not assignment_exists:
                print("✅ Assignment removed from database")
                  # Restore the assignment for cleanup
                Assignment.objects.create(
                    task=test_assignment.task,
                    resource=test_assignment.resource,
                    allocated_hours=test_assignment.allocated_hours
                )
                print("🧹 Restored original assignment")
            else:
                print("❌ Assignment still exists in database")
        else:
            print("❌ Unassignment failed")
            if result.get('error'):
                print(f"Error: {result['error']}")
    else:
        print(f"❌ Unassign request failed: {response.content.decode()}")
        
    # Test unassignment with invalid ID
    print(f"\n=== Testing unassign with invalid ID ===")
    invalid_unassign_data = {
        'assignment_id': 99999  # Non-existent ID
    }
    
    response = client.post('/allocation/api/unassign-task/',
                          data=json.dumps(invalid_unassign_data),
                          content_type='application/json')
    
    print(f"Invalid unassign response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        if not result.get('success'):
            print(f"Expected error: {result.get('error', 'No error message')}")
            print("✅ Invalid ID properly handled")
        else:
            print("❌ Invalid ID should have failed")
    
    # Test unassignment without assignment_id
    print(f"\n=== Testing unassign without assignment_id ===")
    empty_unassign_data = {}
    
    response = client.post('/allocation/api/unassign-task/',
                          data=json.dumps(empty_unassign_data),
                          content_type='application/json')
    
    print(f"Empty data response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        if not result.get('success'):
            print(f"Expected error: {result.get('error', 'No error message')}")
            print("✅ Missing assignment_id properly handled")
        else:
            print("❌ Missing assignment_id should have failed")

else:
    print("❌ No existing assignments found for testing")
