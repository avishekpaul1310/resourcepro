#!/usr/bin/env python
"""
Test the intervention simulation API endpoints
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_simulation_endpoint():
    """Test the simulation API endpoint"""
    print("🧪 Testing Intervention Simulation API")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Create or get a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Login the user
    client.force_login(user)
    
    # Test data for simulation
    test_data = {
        'scenario_type': 'communication_plan',
        'title': 'Team Communication Issue Test',
        'description': 'Testing communication plan intervention',
        'communication_type': 'team_meetings',
        'frequency': 'daily',
        'tools': 'documentation_tools'
    }
    
    print(f"📊 Testing simulation with data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        # Make the API call
        response = client.post(
            '/dashboard/simulate-intervention/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"\n📈 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simulation API: WORKING")
            
            if result.get('success'):
                print(f"🎯 Simulation ID: {result['result'].get('id')}")
                print(f"📊 Success Probability: {result['result'].get('success_probability', 0):.0%}")
                print(f"💰 Estimated Cost: ${result['result'].get('estimated_cost', 0):,.0f}")
                print(f"⏱️ Time Impact: {result['result'].get('estimated_time_impact', 0)} hours")
            else:
                print(f"⚠️ Simulation Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw response: {response.content}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Simulation API test completed!")

if __name__ == '__main__':
    test_simulation_endpoint()
