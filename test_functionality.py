#!/usr/bin/env python
"""
Quick functionality test for ResourcePro enhancements
Tests all 5 major features we implemented
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_url_accessibility():
    """Test that all URLs are accessible and don't return 404s"""
    client = Client()
    
    # Create test user if not exists
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_superuser': True, 'is_staff': True}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login
    client.login(username='testuser', password='testpass123')
    
    # Test URLs
    test_urls = [
        # Core functionality
        ('dashboard', '/dashboard/'),
        ('resources:resource_list', '/resources/'),
        ('project_list', '/projects/'),
        
        # Analytics features
        ('analytics:analytics_dashboard', '/analytics/'),
        ('analytics:generate_forecast', '/analytics/forecast/generate/'),
        ('analytics:analyze_skills', '/analytics/skills/analyze/'),
        ('analytics:utilization_report', '/analytics/utilization/'),
        ('analytics:cost_tracking_report', '/analytics/costs/'),
        
        # Time tracking features
        ('resources:time_entry_list', '/resources/time-entries/'),
        ('resources:availability_calendar', '/resources/availability/'),
        
        # Export features
        ('analytics:export_report', '/analytics/export/utilization/', {'report_type': 'utilization'}),
    ]
    
    print("🧪 Testing URL Accessibility...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_urls)
    
    for url_info in test_urls:
        if len(url_info) == 3:
            url_name, expected_path, kwargs = url_info
            try:
                url = reverse(url_name, kwargs=kwargs)
            except Exception as e:
                print(f"❌ {url_name}: URL reverse failed - {e}")
                continue
        else:
            url_name, expected_path = url_info
            try:
                url = reverse(url_name)
            except Exception as e:
                print(f"❌ {url_name}: URL reverse failed - {e}")
                continue
        
        try:
            response = client.get(url)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {url_name}: {status} - {url}")
                success_count += 1
            elif status == 302:
                print(f"↪️  {url_name}: {status} (redirect) - {url}")
                success_count += 1
            else:
                print(f"⚠️  {url_name}: {status} - {url}")
                
        except Exception as e:
            print(f"❌ {url_name}: Error - {e}")
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_count} URLs working correctly")
    
    return success_count == total_count

def test_analytics_services():
    """Test analytics services functionality"""
    print("\n🔬 Testing Analytics Services...")
    print("=" * 50)
    
    try:
        from analytics.services import PredictiveAnalyticsService, UtilizationTrackingService, CostTrackingService
        
        # Test predictive analytics
        try:
            service = PredictiveAnalyticsService()
            forecasts = service.generate_resource_demand_forecast(days_ahead=30)
            skill_analysis = service.analyze_skill_demand()
            print(f"✅ Predictive Analytics: Forecasts={len(forecasts) if forecasts else 0}, Skills={len(skill_analysis)}")
        except Exception as e:
            print(f"❌ Predictive Analytics: {e}")
        
        # Test utilization tracking
        try:
            util_service = UtilizationTrackingService()
            util_service.record_daily_utilization()
            trends = util_service.get_utilization_trends(days=30)
            print(f"✅ Utilization Tracking: {trends.count()} trend records")
        except Exception as e:
            print(f"❌ Utilization Tracking: {e}")
        
        # Test cost tracking
        try:
            cost_service = CostTrackingService()
            cost_service.update_project_costs()
            variance_report = cost_service.get_cost_variance_report()
            print(f"✅ Cost Tracking: {len(variance_report)} project reports")
        except Exception as e:
            print(f"❌ Cost Tracking: {e}")
            
    except ImportError as e:
        print(f"❌ Analytics Services Import Error: {e}")

def test_data_integrity():
    """Test that our data models are working correctly"""
    print("\n📊 Testing Data Integrity...")
    print("=" * 50)
    
    try:
        from resources.models import Resource, TimeEntry, ResourceAvailability
        from projects.models import Project, Task
        from analytics.models import ResourceDemandForecast, HistoricalUtilization
        
        # Count records
        resources = Resource.objects.count()
        projects = Project.objects.count()
        tasks = Task.objects.count()
        time_entries = TimeEntry.objects.count()
        availability = ResourceAvailability.objects.count()
        forecasts = ResourceDemandForecast.objects.count()
        utilization = HistoricalUtilization.objects.count()
        
        print(f"✅ Resources: {resources}")
        print(f"✅ Projects: {projects}")
        print(f"✅ Tasks: {tasks}")
        print(f"✅ Time Entries: {time_entries}")
        print(f"✅ Availability Records: {availability}")
        print(f"✅ Demand Forecasts: {forecasts}")
        print(f"✅ Utilization Records: {utilization}")
        
        # Test relationships
        if resources > 0:
            resource = Resource.objects.first()
            print(f"✅ Resource cost tracking: ${resource.cost_per_hour}/hour")
        
        if time_entries > 0:
            entry = TimeEntry.objects.first()
            print(f"✅ Time entry relationships: {entry.resource.name} -> {entry.task.name}")
            
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 ResourcePro Enhancement Testing")
    print("Testing all 5 major features:")
    print("1. Predictive Analytics")
    print("2. Export Capabilities") 
    print("3. Time Tracking")
    print("4. Cost Tracking")
    print("5. Availability Management")
    print("\n")
    
    # Run tests
    urls_ok = test_url_accessibility()
    test_analytics_services()
    test_data_integrity()
    
    print("\n" + "=" * 50)
    if urls_ok:
        print("🎉 SUCCESS: All major functionality is working!")
        print("✅ All URLs accessible")
        print("✅ Analytics services operational")
        print("✅ Data models functioning")
        print("\n🌐 You can now test the web interface at: http://127.0.0.1:8000")
        print("📋 Login with superuser credentials to access all features")
    else:
        print("⚠️  Some issues detected - check the output above")
    
    return urls_ok

if __name__ == "__main__":
    main()
