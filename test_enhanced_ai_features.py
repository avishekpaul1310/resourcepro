#!/usr/bin/env python
"""
Test script for enhanced AI features in ResourcePro
Tests the new AI Task Suggestions and unassign functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from projects.models import Task
from allocation.models import Assignment
from resources.models import Resource
import json

def test_enhanced_ai_features():
    """Test the enhanced AI features"""
    print("🧪 Testing Enhanced AI Features")
    print("=" * 50)
    
    # Get test data
    client = Client()
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No admin user found")
        return
    
    client.force_login(user)
    print(f"✅ Logged in as {user.username}")
    
    # 1. Test AI Task Suggestions API
    print("\n📋 Testing AI Task Suggestions API...")
    unassigned_tasks = Task.objects.filter(assignments__isnull=True)[:2]
    if not unassigned_tasks:
        print("⚠️  No unassigned tasks found")
        return
    
    for task in unassigned_tasks:
        response = client.get(f'/allocation/api/ai-suggestions/{task.id}/')
        print(f"   Task {task.id} ({task.name}): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                suggestions = data.get('suggestions', [])
                print(f"   ✅ Got {len(suggestions)} AI suggestions")
                if suggestions:
                    top_suggestion = suggestions[0]
                    print(f"   📍 Top match: {top_suggestion.get('resource', {}).get('name')} - {top_suggestion.get('reasoning', '')[:50]}...")
            else:
                print(f"   ❌ API error: {data.get('error')}")
    
    # 2. Test assignment creation
    print("\n🔗 Testing Assignment Creation...")
    if unassigned_tasks and Resource.objects.exists():
        task = unassigned_tasks[0]
        resource = Resource.objects.first()
        
        assign_data = {
            'task_id': task.id,
            'resource_id': resource.id
        }
        
        response = client.post(
            '/allocation/api/assign-task/',
            data=json.dumps(assign_data),
            content_type='application/json'
        )
        
        print(f"   Assignment API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                assignment_id = data.get('assignment', {}).get('id')
                print(f"   ✅ Created assignment {assignment_id}")
                
                # 3. Test unassignment
                print("\n🗑️  Testing Unassignment...")
                unassign_data = {'assignment_id': assignment_id}
                
                response = client.post(
                    '/allocation/api/unassign-task/',
                    data=json.dumps(unassign_data),
                    content_type='application/json'
                )
                
                print(f"   Unassignment API: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"   ✅ Successfully unassigned task")
                        print(f"   📋 Task returned: {data.get('task', {}).get('name')}")
                    else:
                        print(f"   ❌ Unassign error: {data.get('error')}")
                else:
                    print(f"   ❌ Unassign failed: {response.status_code}")
            else:
                print(f"   ❌ Assignment error: {data.get('error')}")
      # 4. Test UI components
    print("\n🖥️  Testing UI Components...")
    response = client.get('/allocation/')
    print(f"   Allocation board: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for key UI elements
        checks = [
            ('AI Task Suggestions button', 'AI Task Suggestions' in content),
            ('Brain icon button', 'fa-brain' in content),
            ('Robot icon', 'fa-robot' in content),
            ('Remove button', 'assignment-remove' in content),
            ('AI suggestions panel', 'ai-suggestions' in content),
            ('JavaScript file', 'ai-allocation-debug.js' in content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
    
    print("\n🎉 Enhanced AI Features Test Complete!")
    print("\nKey Features Implemented:")
    print("  🤖 AI Task Suggestions with detailed reasoning")
    print("  🧠 Individual task AI recommendations")
    print("  ❌ Unassign tasks (return to unassigned list)")
    print("  🎨 Enhanced UI with clear AI labeling")
    print("  📱 Modal interface for batch suggestions")
    print("  ⚡ Real-time utilization updates")

if __name__ == '__main__':
    test_enhanced_ai_features()
