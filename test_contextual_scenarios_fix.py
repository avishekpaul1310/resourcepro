#!/usr/bin/env python
"""
Test script to verify the contextual scenarios endpoint is working
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from dashboard.views import get_contextual_scenarios

def test_contextual_scenarios():
    """Test the get_contextual_scenarios view directly"""
    print("=== Testing Contextual Scenarios Endpoint ===")
    
    # Create a test user
    try:
        user = User.objects.get(username='testuser')
        print("✓ Using existing test user")
    except User.DoesNotExist:
        user = User.objects.create_user(username='testuser', password='testpass')
        print("✓ Created test user")
    
    # Create a request factory
    factory = RequestFactory()
    
    # Create test data
    test_data = {
        'project_id': None,
        'problem_title': 'Resource Shortage',
        'problem_description': 'Team is overallocated and missing key skills',
        'risk_data': {
            'category_type': 'resource',
            'severity': 'medium'
        }
    }
    
    # Create POST request
    request = factory.post(
        '/dashboard/api/get-contextual-scenarios/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    request.user = user
    
    try:
        print("📡 Making request to get_contextual_scenarios...")
        response = get_contextual_scenarios(request)
        
        if isinstance(response, JsonResponse):
            response_data = json.loads(response.content.decode())
            print(f"✅ Request successful! Status: {response.status_code}")
            print(f"✅ Response keys: {list(response_data.keys())}")
            
            if 'success' in response_data and response_data['success']:
                print("✅ Endpoint returned success=True")
                if 'scenarios' in response_data:
                    scenarios = response_data['scenarios']
                    if isinstance(scenarios, dict):
                        recommended_count = len(scenarios.get('recommended', []))
                        additional_count = len(scenarios.get('additional', []))
                        print(f"✅ Found {recommended_count} recommended and {additional_count} additional scenarios")
                    else:
                        print(f"✅ Found {len(scenarios)} scenarios")
                else:
                    print("⚠️  No scenarios in response")
            else:
                print(f"❌ Endpoint returned success=False: {response_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response type: {type(response)}")
            print(f"Response content: {response.content[:500]}...")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

def test_ai_services_directly():
    """Test the AI services directly"""
    print("\n=== Testing AI Services Directly ===")
    
    try:
        from dashboard.ai_services import enhanced_risk_service
        print("✓ Successfully imported enhanced_risk_service")
        
        # Test the method that was causing issues
        mock_risk = {
            'title': 'Test Risk',
            'description': 'Test description',
            'category_type': 'resource',
            'severity': 'medium',
        }
        
        context = {
            'project_context': {
                'budget': 50000,
                'days_remaining': 30,
                'completion_percentage': 50,
                'team_size': 5
            },
            'team_size': 5
        }
        
        print("📡 Testing _generate_dynamic_interventions...")
        interventions = enhanced_risk_service._generate_dynamic_interventions(mock_risk, context)
        print(f"✅ Generated {len(interventions)} interventions successfully")
        
        for i, intervention in enumerate(interventions[:3]):  # Show first 3
            print(f"  {i+1}. {intervention.get('name', 'Unknown')} - {intervention.get('description', 'No description')[:50]}...")
            
    except Exception as e:
        print(f"❌ Error in AI services: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_contextual_scenarios()
    test_ai_services_directly()
    print("\n=== Test Complete ===")
