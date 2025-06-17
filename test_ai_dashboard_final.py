#!/usr/bin/env python
"""
Comprehensive test script for AI Dashboard features
Tests all AI components after the fixes have been applied
"""

import os
import django
import sys
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

def test_ai_dashboard_functionality():
    """Test all AI dashboard functionality"""
    print("🤖 Testing AI Dashboard Functionality...")
    print("=" * 60)
    
    # Test 1: Check AI Analysis Generation
    print("\n1. Testing AI Analysis Generation...")
    try:
        from dashboard.ai_services import dashboard_ai_service
        analysis = dashboard_ai_service.generate_daily_briefing()
        
        if 'error' in analysis:
            print(f"   ❌ Error in AI analysis: {analysis['error']}")
        else:
            print(f"   ✅ AI analysis generated successfully")
            print(f"   📊 Summary: {analysis.get('summary', 'N/A')[:100]}...")
            print(f"   ⚠️  Risks found: {len(analysis.get('risks', []))}")
            print(f"   ✅ Recommendations: {len(analysis.get('recommendations', []))}")
            print(f"   🎯 Confidence: {analysis.get('confidence_score', 0):.2f}")
    except Exception as e:
        print(f"   ❌ Exception in AI analysis: {str(e)}")
    
    # Test 2: Check Dashboard View
    print("\n2. Testing Dashboard View...")
    try:
        client = Client()
        
        # Create test user and login
        user = User.objects.get_or_create(username='testuser')[0]
        user.set_password('testpass')
        user.save()
        
        client.login(username='testuser', password='testpass')
        
        response = client.get('/dashboard/')
        
        if response.status_code == 200:
            print("   ✅ Dashboard loads successfully")
            
            # Check if AI widget is present
            content = response.content.decode()
            if 'ai-analyst-widget' in content:
                print("   ✅ AI analyst widget found in HTML")
            else:
                print("   ❌ AI analyst widget missing from HTML")
                
            if 'ai_dashboard.js' in content:
                print("   ✅ AI dashboard JavaScript included")
            else:
                print("   ❌ AI dashboard JavaScript missing")
                
        else:
            print(f"   ❌ Dashboard failed to load: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception in dashboard view: {str(e)}")
    
    # Test 3: Check AI Refresh API
    print("\n3. Testing AI Refresh API...")
    try:
        response = client.post('/dashboard/api/refresh-ai-analysis/')
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if 'error' in data:
                print(f"   ❌ API returned error: {data['error']}")
            else:
                print("   ✅ AI refresh API works correctly")
        else:
            print(f"   ❌ AI refresh API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception in AI refresh API: {str(e)}")
    
    # Test 4: Check JavaScript Functions
    print("\n4. Testing JavaScript Function Definitions...")
    try:
        js_file_path = 'staticfiles/js/ai_dashboard.js'
        if os.path.exists(js_file_path):
            with open(js_file_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
                
            required_functions = [
                'initializeAIFeatures',
                'initializeAIAnalyst', 
                'refreshAIAnalysis',
                'updateAIAnalysisWidget',
                'showNotification',
                'getCsrfToken'
            ]
            
            missing_functions = []
            for func in required_functions:
                if f'function {func}' in js_content:
                    print(f"   ✅ {func} function found")
                else:
                    missing_functions.append(func)
                    print(f"   ❌ {func} function missing")
            
            if not missing_functions:
                print("   🎉 All required JavaScript functions are present!")
            else:
                print(f"   ⚠️  Missing functions: {', '.join(missing_functions)}")
        else:
            print("   ❌ AI dashboard JavaScript file not found")
    except Exception as e:
        print(f"   ❌ Exception checking JavaScript: {str(e)}")
    
    # Test 5: Check Model Relationships
    print("\n5. Testing Model Relationships...")
    try:
        from projects.models import Task, Project
        from allocation.models import Assignment
        from resources.models import Resource
        
        # Test the fixed assigned_resources relationship
        tasks = Task.objects.all()[:1]
        if tasks:
            task = tasks[0]
            print(f"   ✅ Testing task: {task.name}")
            
            # This should work now (fixed the assigned_resources issue)
            assignments = task.assignments.all()
            print(f"   ✅ Task assignments accessible: {assignments.count()} assignments")
            
            # Test resource names through assignments
            resource_names = [assignment.resource.name for assignment in assignments]
            print(f"   ✅ Resource names accessible: {resource_names}")
        else:
            print("   ⚠️  No tasks found for testing")
            
    except Exception as e:
        print(f"   ❌ Exception in model relationships: {str(e)}")
    
    # Test 6: Check Template Tags
    print("\n6. Testing Template Tags...")
    try:
        from dashboard.templatetags.dashboard_tags import jsonify, mul
        
        test_data = {'test': 'value', 'number': 42}
        json_result = jsonify(test_data)
        print(f"   ✅ jsonify filter works: {type(json_result)}")
        
        mul_result = mul(5, 3)
        print(f"   ✅ mul filter works: {mul_result}")
        
    except Exception as e:
        print(f"   ❌ Exception in template tags: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 AI Dashboard Test Summary Complete!")
    print("💡 Check the browser at http://127.0.0.1:8000/dashboard/ to see the visual improvements")

if __name__ == '__main__':
    test_ai_dashboard_functionality()
