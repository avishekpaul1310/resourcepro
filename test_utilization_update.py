#!/usr/bin/env python
"""
Quick test to verify that utilization data updates dynamically
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
from projects.models import Task
from allocation.models import Assignment
from analytics.services import UtilizationTrackingService

def test_utilization_update():
    """Test that utilization updates when assignments change"""
    
    print("=== Testing Utilization Update ===")
    
    # Get a resource and a task
    resource = Resource.objects.first()
    task = Task.objects.filter(assignments=None).first()
    
    if not resource or not task:
        print("❌ No available resource or unassigned task found for testing")
        return
    
    print(f"Testing with Resource: {resource.name}")
    print(f"Testing with Task: {task.name}")
    
    # Check initial utilization
    initial_util = resource.current_utilization()
    print(f"Initial utilization: {initial_util:.1f}%")
    
    # Create assignment
    assignment = Assignment.objects.create(
        resource=resource,
        task=task,
        allocated_hours=task.estimated_hours
    )
    print(f"✅ Created assignment: {assignment}")
    
    # Check utilization after assignment
    after_util = resource.current_utilization()
    print(f"Utilization after assignment: {after_util:.1f}%")
    
    # Update historical utilization
    utilization_service = UtilizationTrackingService()
    utilization_service.record_daily_utilization()
    print("✅ Updated historical utilization data")
    
    # Clean up - delete the assignment
    assignment.delete()
    print("✅ Cleaned up assignment")
    
    # Check final utilization
    final_util = resource.current_utilization()
    print(f"Final utilization: {final_util:.1f}%")
    
    if initial_util != after_util:
        print("✅ SUCCESS: Utilization changed when assignment was created")
    else:
        print("⚠️  WARNING: Utilization did not change")
    
    if final_util == initial_util:
        print("✅ SUCCESS: Utilization returned to initial value after cleanup")
    else:
        print("⚠️  WARNING: Utilization did not return to initial value")

if __name__ == "__main__":
    test_utilization_update()
