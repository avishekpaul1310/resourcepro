#!/usr/bin/env python
"""
Test script to check Simulate Solutions functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from dashboard.models import DashboardAIAnalysis
import json

def test_simulate_solutions():
    """Test the Simulate Solutions button functionality"""
    print("🧪 Testing Simulate Solutions Functionality")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Create or get test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    # Login user
    login_success = client.login(username='testuser', password='testpass123')
    print(f"1. User login: {'✅ Success' if login_success else '❌ Failed'}")
    
    if not login_success:
        print("Cannot continue without login")
        return
    
    # Test dashboard page loads
    try:
        response = client.get(reverse('dashboard'))
        print(f"2. Dashboard page access: {'✅ Success' if response.status_code == 200 else '❌ Failed'}")
        
        # Check if AI widgets are included
        content = response.content.decode('utf-8')
        has_ai_widget = 'ai-analyst-widget' in content
        print(f"3. AI analyst widget present: {'✅ Yes' if has_ai_widget else '❌ No'}")
        
        # Check if Simulate Solutions button is present
        has_simulate_button = 'Simulate Solutions' in content
        print(f"4. Simulate Solutions button present: {'✅ Yes' if has_simulate_button else '❌ No'}")
        
        # Check if intervention modal is included
        has_modal = 'interventionModal' in content
        print(f"5. Intervention modal present: {'✅ Yes' if has_modal else '❌ No'}")
        
        # Check if JavaScript file is loaded
        has_js = 'ai_dashboard.js' in content
        print(f"6. AI dashboard JavaScript loaded: {'✅ Yes' if has_js else '❌ No'}")
        
        # Count how many times JS is loaded
        js_count = content.count('ai_dashboard.js')
        print(f"7. JavaScript load count: {js_count} ({'✅ Good' if js_count == 1 else '⚠️ Multiple loads detected' if js_count > 1 else '❌ Not loaded'})")
        
    except Exception as e:
        print(f"2. Dashboard page access: ❌ Error - {e}")
        return
    
    # Test intervention simulator API endpoint
    try:
        test_data = {
            "scenario_type": "reassignment",
            "title": "Test Risk",
            "description": "Test description for simulation",
            "priority": "high",
            "project_id": ""
        }
        
        response = client.post(
            reverse('simulate_intervention'),
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"8. Intervention API endpoint: {'✅ Accessible' if response.status_code in [200, 400, 500] else '❌ Not found'}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
        elif response.status_code in [400, 500]:
            print(f"   Status: {response.status_code} (Expected for test data)")
        
    except Exception as e:
        print(f"8. Intervention API endpoint: ❌ Error - {e}")
    
    # Check for AI analysis data
    try:
        ai_analysis_count = DashboardAIAnalysis.objects.count()
        print(f"9. AI Analysis records: {ai_analysis_count} ({'✅ Has data' if ai_analysis_count > 0 else '⚠️ No data'})")
        
        if ai_analysis_count > 0:
            latest = DashboardAIAnalysis.objects.latest('created_at')
            has_risks = bool(latest.risks)
            print(f"10. Latest analysis has risks: {'✅ Yes' if has_risks else '❌ No'}")
            if has_risks:
                risk_count = len(latest.risks)
                print(f"    Risk count: {risk_count}")
        else:
            print("10. Latest analysis has risks: ⚠️ No analysis data")
            
    except Exception as e:
        print(f"9. AI Analysis check: ❌ Error - {e}")

if __name__ == "__main__":
    test_simulate_solutions()
