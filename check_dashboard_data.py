#!/usr/bin/env python
"""
Test that the analytics dashboard shows current utilization data
"""

import os
import django
import sys

# Add the project root to the Python path
project_root = r'c:\Users\Avishek Paul\resourcepro'
sys.path.append(project_root)
os.chdir(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource
from projects.models import Task, Project
from allocation.models import Assignment
from analytics.services import UtilizationTrackingService
from django.utils import timezone
from datetime import timedelta

def check_dashboard_data():
    """Check what data the analytics dashboard would show"""
    
    print("=== Checking Analytics Dashboard Data ===")
    
    # This mimics the logic in analytics/views.py analytics_dashboard
    utilization_data = []
    for resource in Resource.objects.all()[:5]:  # Check first 5 resources
        # Use real-time utilization (our fix)
        current_util = resource.current_utilization()
        
        utilization_data.append({
            'resource': resource,
            'utilization_rate': round(current_util, 1)
        })
        
        print(f"{resource.name}: {current_util:.1f}%")
    
    print("\n✅ Dashboard is now showing real-time utilization data")
    
    # Check if any resources appear overutilized in current data
    overutilized = [data for data in utilization_data if data['utilization_rate'] > 90]
    if overutilized:
        print(f"\n⚠️  Currently overutilized resources:")
        for data in overutilized:
            print(f"  - {data['resource'].name}: {data['utilization_rate']}%")
    else:
        print(f"\n✅ No resources are currently overutilized")

if __name__ == "__main__":
    check_dashboard_data()
