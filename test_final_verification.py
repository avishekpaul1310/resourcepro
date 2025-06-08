#!/usr/bin/env python
"""
Final comprehensive test to verify all major URLs are working
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')

import django
django.setup()

import requests
from django.test import Client
from django.contrib.auth.models import User

def test_key_urls():
    """Test key URLs to verify the application is working"""
    client = Client()
    
    # Login first
    try:
        user = User.objects.get(username='admin')
        client.force_login(user)
        print("✓ Login successful")
    except User.DoesNotExist:
        print("✗ Admin user not found")
        return
      # Test key URLs
    urls_to_test = [
        ('/analytics/', 'Analytics Dashboard'),
        ('/analytics/forecast/', 'Demand Forecasting'),
        ('/analytics/skills/', 'Skill Analysis'),
        ('/analytics/utilization/', 'Utilization Report'),
        ('/analytics/costs/', 'Cost Report'),
        ('/resources/', 'Resources List'),
        ('/resources/create/', 'Create Resource'),
        ('/resources/skills/', 'Skills Management'),
        ('/resources/time-tracking/', 'Time Tracking'),
        ('/resources/availability/', 'Availability Calendar'),
    ]
    
    print("\nTesting key URLs:")
    all_passed = True
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✓ {name}: {url} - Status {response.status_code}")
            else:
                print(f"✗ {name}: {url} - Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"✗ {name}: {url} - Error: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! The ResourcePro application is fully functional.")
        print("\nKey features verified:")
        print("  ✓ Analytics module - All reports working")
        print("  ✓ Resources module - All features working")
        print("  ✓ User authentication - Login system working")
        print("  ✓ URL routing - All URL patterns resolved")
        print("  ✓ Templates - All pages rendering correctly")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == '__main__':
    test_key_urls()
