#!/usr/bin/env python
"""
Test the final analytics dashboard logic
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

def test_final_analytics_logic():
    """Test the final analytics dashboard logic"""
    
    print("=== Final Analytics Dashboard Logic ===")
    
    # Replicate the exact logic from the updated analytics view
    utilization_data = []
    for resource in Resource.objects.all():
        current_util = resource.current_utilization()
        
        utilization_data.append({
            'resource': resource,
            'utilization_rate': round(current_util, 1)
        })
    
    # Sort by utilization rate (highest first)
    utilization_data.sort(key=lambda x: x['utilization_rate'], reverse=True)
    
    # Show top 15 resources, but ensure all resources with >0% utilization are included
    active_resources = [d for d in utilization_data if d['utilization_rate'] > 0]
    available_resources = [d for d in utilization_data if d['utilization_rate'] == 0]
    
    print(f"Active resources (>0%): {len(active_resources)}")
    print(f"Available resources (0%): {len(available_resources)}")
    
    # Take all active resources + fill remaining slots with available resources up to 15 total
    max_display = 15
    if len(active_resources) <= max_display:
        remaining_slots = max_display - len(active_resources)
        final_utilization_data = active_resources + available_resources[:remaining_slots]
    else:
        final_utilization_data = active_resources
    
    print(f"\nAnalytics Dashboard will show {len(final_utilization_data)} resources:")
    print("=" * 50)
    
    for i, data in enumerate(final_utilization_data, 1):
        resource = data['resource']
        util_rate = data['utilization_rate']
        status = ""
        if util_rate > 90:
            status = "🔴 Overutilized"
        elif util_rate > 75:
            status = "🟡 High utilization"
        elif util_rate > 50:
            status = "🟢 Normal"
        elif util_rate > 0:
            status = "🟢 Active"
        else:
            status = "⚪ Available"
            
        print(f"{i:2d}. {resource.name}: {util_rate}% {status}")
    
    # Verify Jack Brown and Kate Davis are included
    jack_included = any(d['resource'].name == 'Jack Brown' for d in final_utilization_data)
    kate_included = any(d['resource'].name == 'Kate Davis' for d in final_utilization_data)
    
    print(f"\n✅ Jack Brown included: {jack_included}")
    print(f"✅ Kate Davis included: {kate_included}")
    
    if jack_included and kate_included:
        print("\n🎉 SUCCESS: Both Jack Brown and Kate Davis will now appear in analytics!")
    else:
        print("\n❌ ERROR: Missing resources in analytics dashboard")

if __name__ == "__main__":
    test_final_analytics_logic()
