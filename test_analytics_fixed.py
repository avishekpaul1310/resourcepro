#!/usr/bin/env python
"""
Test the updated analytics dashboard data
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

def test_analytics_dashboard_data():
    """Test what the analytics dashboard will now show"""
    
    print("=== Analytics Dashboard Data (After Fix) ===")
    
    # This mimics the new logic in analytics/views.py
    utilization_data = []
    for resource in Resource.objects.all():
        current_util = resource.current_utilization()
        
        utilization_data.append({
            'resource': resource,
            'utilization_rate': round(current_util, 1)
        })
    
    # Sort by utilization rate (highest first)
    utilization_data.sort(key=lambda x: x['utilization_rate'], reverse=True)
    
    print("Top resources by utilization:")
    for i, data in enumerate(utilization_data[:15], 1):  # Show top 15
        resource = data['resource']
        util_rate = data['utilization_rate']
        status = ""
        if util_rate > 90:
            status = "🔴 Overutilized"
        elif util_rate > 75:
            status = "🟡 High utilization"
        elif util_rate > 0:
            status = "🟢 Active"
        else:
            status = "⚪ Available"
            
        print(f"{i:2d}. {resource.name}: {util_rate}% {status}")
    
    print(f"\nTotal resources: {len(utilization_data)}")
    active_resources = [d for d in utilization_data if d['utilization_rate'] > 0]
    print(f"Resources with active assignments: {len(active_resources)}")

if __name__ == "__main__":
    test_analytics_dashboard_data()
