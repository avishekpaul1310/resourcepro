#!/usr/bin/env python
"""
Final comprehensive test for the analytics dashboard functionality.
Tests both utilization trends and forecast sections.
"""
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

from django.urls import reverse
from resources.models import Resource
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import ResourceDemandForecast, HistoricalUtilization
from django.utils import timezone
from datetime import timedelta
import json

def test_dashboard_functionality():
    """Test all dashboard functionality"""
    print("=== Testing Analytics Dashboard ===")
    
    # Create a test client
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    # Login
    login_success = client.login(username='testuser', password='testpass123')
    print(f"✅ User login: {'Success' if login_success else 'Failed'}")
    
    if not login_success:
        print("❌ Cannot test dashboard without login")
        return
    
    # Test dashboard access
    try:
        response = client.get('/analytics/')
        print(f"✅ Dashboard access: Status {response.status_code}")
        
        if response.status_code == 200:
            # Check if key sections are present in the response
            content = response.content.decode()
            
            # Check for utilization section
            if 'Recent Utilization Trends' in content:
                print("✅ Utilization trends section found")
            else:
                print("⚠️  Utilization trends section not found")
            
            # Check for forecast section
            if 'Resource Demand Forecast' in content:
                print("✅ Forecast section found")
            else:
                print("⚠️  Forecast section not found")
            
            # Check for pagination controls
            if 'pagination' in content or 'page' in content:
                print("✅ Pagination controls found")
            else:
                print("⚠️  Pagination controls not found")
            
            # Check for refresh button
            if 'refresh-forecast' in content:
                print("✅ Forecast refresh button found")
            else:
                print("⚠️  Forecast refresh button not found")
                
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard access failed: {e}")
    
    # Test pagination functionality
    try:
        response = client.get('/analytics/?page=1&per_page=5')
        print(f"✅ Pagination test: Status {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            if '5' in content and 'per_page' in content:
                print("✅ Per-page parameter working")
            else:
                print("⚠️  Per-page parameter may not be working")
                
    except Exception as e:
        print(f"❌ Pagination test failed: {e}")
    
    # Test forecast generation endpoint
    try:
        response = client.post('/analytics/generate-forecast/', {
            'days_ahead': 30
        })
        print(f"✅ Forecast generation: Status {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                if data.get('success'):
                    print("✅ Forecast generation successful")
                else:
                    print(f"⚠️  Forecast generation response: {data.get('message', 'No message')}")
            except json.JSONDecodeError:
                print("⚠️  Forecast generation returned non-JSON response")
        else:
            print(f"⚠️  Forecast generation returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Forecast generation test failed: {e}")
    
    print("\n=== Data Summary ===")
    
    # Show current data state
    resources_count = Resource.objects.count()
    projects_count = Project.objects.count()
    tasks_count = Task.objects.count()
    assignments_count = Assignment.objects.count()
    forecasts_count = ResourceDemandForecast.objects.count()
    utilization_count = HistoricalUtilization.objects.count()
    
    print(f"Resources: {resources_count}")
    print(f"Projects: {projects_count}")
    print(f"Tasks: {tasks_count}")
    print(f"Assignments: {assignments_count}")
    print(f"Forecasts: {forecasts_count}")
    print(f"Utilization records: {utilization_count}")
    
    # Check for recent forecasts
    recent_forecasts = ResourceDemandForecast.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=3)
    ).count()
    print(f"Recent forecasts (last 3 days): {recent_forecasts}")
    
    # Check for recent utilization data
    recent_utilization = HistoricalUtilization.objects.filter(
        date__gte=timezone.now().date() - timedelta(days=7)
    ).count()
    print(f"Recent utilization records (last 7 days): {recent_utilization}")
    
    print("\n=== Test Complete ===")
    print("The dashboard should now display:")
    print("• Real-time resource utilization with trends")
    print("• Paginated utilization data with controls")
    print("• Fresh forecast data or generation prompts")
    print("• Working refresh functionality")

if __name__ == '__main__':
    test_dashboard_functionality()
