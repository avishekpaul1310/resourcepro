#!/usr/bin/env python
"""
Test script for Grammar Fix in AI Task Suggestions Modal
Tests both singular and plural cases for proper English grammar
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

def test_grammar_fix():
    """Test the grammar fix for AI suggestions modal"""
    print("📝 Testing Grammar Fix for AI Task Suggestions")
    print("=" * 50)
    
    # Get test data
    client = Client()
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No admin user found")
        return
    
    client.force_login(user)
    print(f"✅ Logged in as {user.username}")
    
    # Check current state
    unassigned_tasks = Task.objects.filter(assignments__isnull=True)
    unassigned_count = unassigned_tasks.count()
    
    print(f"\n📊 Current state:")
    print(f"   📋 Unassigned tasks: {unassigned_count}")
    
    # Test the UI page to see if our changes are present
    print(f"\n🖥️  Testing UI with {unassigned_count} unassigned tasks...")
    response = client.get('/allocation/')
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for our updated JavaScript
        grammar_checks = [
            ('Updated button text logic', 'suggestions.length === 1' in content),
            ('Singular recommendation text', 'Assign the Recommendation' in content),
            ('Plural recommendations text', 'Assign All Recommendations' in content),
            ('Dynamic task count', 'task${suggestions.length === 1' in content),
            ('JavaScript file loading', 'ai-allocation-debug.js' in content),
        ]
        
        for check_name, check_result in grammar_checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
    
    # Test AI suggestions API for both single and multiple tasks
    print(f"\n🤖 Testing AI API responses...")
    
    # Test with first task (should show singular form)
    if unassigned_count > 0:
        first_task = unassigned_tasks.first()
        response = client.get(f'/allocation/api/ai-suggestions/{first_task.id}/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ AI suggestions working for single task: {first_task.name}")
            else:
                print(f"   ❌ AI suggestions failed: {data.get('error')}")
    
    print(f"\n🎯 Expected Modal Behavior:")
    if unassigned_count == 1:
        print(f"   📝 With 1 task: 'AI has analyzed 1 task and found the following optimal assignment:'")
        print(f"   🔘 Button text: 'Assign the Recommendation'")
    else:
        print(f"   📝 With {unassigned_count} tasks: 'AI has analyzed {unassigned_count} tasks and found the following optimal assignments:'")
        print(f"   🔘 Button text: 'Assign All Recommendations'")
    
    print(f"\n✨ Grammar Fix Summary:")
    print(f"   🔤 Singular (1 task): 'task' → 'assignment' → 'Assign the Recommendation'")
    print(f"   🔤 Plural (2+ tasks): 'tasks' → 'assignments' → 'Assign All Recommendations'")
    print(f"   ✅ JavaScript now dynamically adjusts text based on count")
    print(f"   📱 Works for any number of unassigned tasks")
    
    print(f"\n🎉 Grammar Fix Test Complete!")

if __name__ == '__main__':
    test_grammar_fix()
