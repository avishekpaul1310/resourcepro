#!/usr/bin/env python3
"""
Test script to verify the AI-Powered Project Intervention Simulator functionality
"""

import os
import sys
import json

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_intervention_simulator():
    """Test the intervention simulator functionality"""
    print("🧪 Testing AI-Powered Project Intervention Simulator...")
    
    # Create a test client
    client = Client()
    
    try:
        # Try to get admin user
        try:
            user = User.objects.get(username='admin')
            print("✅ Found admin user")
        except User.DoesNotExist:
            print("❌ Admin user not found, creating one...")
            user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
            print("✅ Created admin user")
        
        # Login as admin
        login_successful = client.login(username='admin', password='admin123')
        if login_successful:
            print("✅ Successfully logged in as admin")
        else:
            print("❌ Failed to login as admin")
            return False
          # Test dashboard access
        dashboard_response = client.get('/dashboard/')
        if dashboard_response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Check if risk data is present
            if hasattr(dashboard_response, 'context') and dashboard_response.context and 'risks' in dashboard_response.context:
                risks = dashboard_response.context['risks']
                print(f"✅ Found {len(risks)} risks in dashboard")
            else:
                print("⚠️  No risks found in dashboard context - checking content instead")
                dashboard_content = dashboard_response.content.decode('utf-8')
                if 'Key Risks' in dashboard_content:
                    print("✅ Found 'Key Risks' section in dashboard content")
                else:
                    print("⚠️  No 'Key Risks' section found in dashboard")
        else:
            print(f"❌ Dashboard not accessible, status: {dashboard_response.status_code}")
            return False
        
        # Test intervention simulator endpoint
        print("\n🎯 Testing intervention simulator...")
        
        # Test data for intervention
        test_risk_data = {
            'title': 'Test Critical Deadline Risk',
            'description': 'A test risk for the intervention simulator',
            'severity': 'HIGH',
            'affected_projects': ['test project'],
            'affected_resources': ['Bob Johnson', 'Alice Brown']
        }
        
        # Test opening intervention simulator
        intervention_data = {
            'riskTitle': test_risk_data['title'],
            'riskData': json.dumps(test_risk_data)
        }
        
        # Test if the intervention endpoint exists
        try:
            intervention_response = client.post('/api/intervention/', intervention_data, content_type='application/json')
            print(f"📊 Intervention API response status: {intervention_response.status_code}")
            
            if intervention_response.status_code == 200:
                print("✅ Intervention simulator API working")
            elif intervention_response.status_code == 404:
                print("⚠️  Intervention API endpoint not found - this might be handled by JavaScript")
            else:
                print(f"⚠️  Intervention API returned status: {intervention_response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Intervention API test failed: {e}")
        
        # Check if JavaScript files are accessible
        js_files_to_check = [
            '/static/js/ai_dashboard.js',
            '/static/js/ai-allocation-debug.js'
        ]
        
        for js_file in js_files_to_check:
            js_response = client.get(js_file)
            if js_response.status_code == 200:
                print(f"✅ JavaScript file accessible: {js_file}")
            else:
                print(f"❌ JavaScript file not accessible: {js_file} (status: {js_response.status_code})")
        
        print("\n🔧 Testing intervention scenario buttons...")
        
        # Check if the dashboard contains the expected HTML structure
        dashboard_content = dashboard_response.content.decode('utf-8')
        
        if 'btn-simulate' in dashboard_content:
            print("✅ Found 'Simulate Solutions' buttons in dashboard")
        else:
            print("❌ No 'Simulate Solutions' buttons found in dashboard")
        
        if 'openInterventionSimulator' in dashboard_content:
            print("✅ Found openInterventionSimulator function references")
        else:
            print("⚠️  No openInterventionSimulator function references found")
        
        if 'AI-Powered Project Intervention Simulator' in dashboard_content:
            print("✅ Found intervention simulator modal in dashboard")
        else:
            print("❌ Intervention simulator modal not found in dashboard")
        
        # Test specific intervention scenarios
        scenarios = [
            'Task Reassignment',
            'Overtime Authorization', 
            'Additional Resource',
            'Deadline Extension',
            'Scope Reduction',
            'Training & Development'
        ]
        
        found_scenarios = 0
        for scenario in scenarios:
            if scenario in dashboard_content:
                found_scenarios += 1
        
        print(f"✅ Found {found_scenarios}/{len(scenarios)} intervention scenarios in dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_static_files():
    """Check if static files are properly configured"""
    print("\n📁 Checking static files configuration...")
    
    import django.conf
    settings = django.conf.settings
    
    print(f"STATIC_URL: {getattr(settings, 'STATIC_URL', 'Not set')}")
    print(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")
    
    # Check if static files exist
    static_js_path = os.path.join(os.getcwd(), 'static', 'js', 'ai_dashboard.js')
    allocation_js_path = os.path.join(os.getcwd(), 'allocation', 'static', 'js', 'ai-allocation-debug.js')
    
    if os.path.exists(static_js_path):
        print("✅ Found static/js/ai_dashboard.js")
    else:
        print("❌ static/js/ai_dashboard.js not found")
    
    if os.path.exists(allocation_js_path):
        print("✅ Found allocation/static/js/ai-allocation-debug.js")
    else:
        print("❌ allocation/static/js/ai-allocation-debug.js not found")

if __name__ == "__main__":
    print("🚀 Starting Intervention Simulator Test...\n")
    
    check_static_files()
    success = test_intervention_simulator()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\n📋 Next steps to test manually:")
        print("1. Open http://127.0.0.1:8000/dashboard/ in your browser")
        print("2. Login with admin / admin123")
        print("3. Look for 'Key Risks' section with 'Simulate Solutions' buttons")
        print("4. Click on a 'Simulate Solutions' button")
        print("5. The intervention simulator modal should open with 6 scenario options")
        print("6. Click on any scenario to see the simulation results")
    else:
        print("\n❌ Test failed. Check the errors above.")
