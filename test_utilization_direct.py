#!/usr/bin/env python
"""
Direct test of utilization report view to show actual data
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.views import utilization_report
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_utilization_direct():
    """Test the utilization report view directly"""
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/analytics/utilization/')
    
    # Add user to request (required for @login_required)
    admin_user = User.objects.get(username='admin')
    request.user = admin_user
    
    try:
        # Call the view directly
        response = utilization_report(request)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Utilization report view working successfully!")
            
            # Try to get some context data by examining the response
            context = response.context_data if hasattr(response, 'context_data') else None
            if context:
                print(f"Context keys: {list(context.keys())}")
                utilization_data = context.get('utilization_data', [])
                print(f"Number of resources: {len(utilization_data)}")
            else:
                print("No context data available in response")
                
            # Check if response contains utilization data
            content = response.content.decode('utf-8')
            if 'Total Resources' in content:
                print("✅ Found utilization summary in response")
            if 'Resource Utilization Details' in content:
                print("✅ Found utilization details table in response")
            if 'No utilization data available' in content:
                print("❌ Still showing 'No utilization data available'")
            else:
                print("✅ Not showing 'No utilization data available' message")
        else:
            print(f"❌ Error: Response status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error calling view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_utilization_direct()
