#!/usr/bin/env python
"""
Test script to verify the utilization report functionality
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_utilization_report():
    """Test the utilization report view"""
    
    # Create a test client
    client = Client()
    
    # Log in with admin user
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)
    
    # Test the utilization report URL
    url = reverse('analytics:utilization_report')
    print(f"Testing URL: {url}")
    response = client.get(url)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        # For template response, use response.context instead
        if hasattr(response, 'context') and response.context:
            context = response.context
            print(f"Context keys: {list(context.keys())}")
        else:
            print("No context available - checking response content")
            content = response.content.decode('utf-8')
            if 'No utilization data available' in content:
                print("Found 'No utilization data available' message in response")
            elif 'Total Resources' in content:
                print("Found utilization report content in response")
            else:
                print("Unexpected response content")
            return
        
        # Check if we have utilization data
        utilization_data = context.get('utilization_data', [])
        print(f"Number of resources with utilization data: {len(utilization_data)}")
        
        if utilization_data:
            print("Sample utilization data:")
            for i, data in enumerate(utilization_data[:3]):  # Show first 3
                resource = data['resource']
                print(f"  {i+1}. {resource.name} ({resource.role}): {data['utilization_rate']}%")
        else:
            print("No utilization data found in context")
            
        # Check other context variables
        print(f"Total resources: {context.get('total_resources', 'Not found')}")
        print(f"Average utilization: {context.get('avg_utilization', 'Not found')}")
        print(f"Date range: {context.get('start_date')} to {context.get('end_date')}")
        
    else:
        print(f"Error: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Response content: {response.content[:500]}")

if __name__ == "__main__":
    test_utilization_report()
