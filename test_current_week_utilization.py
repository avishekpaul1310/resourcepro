#!/usr/bin/env python
"""
Test utilization with current week tasks
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
from datetime import timedelta, date

def test_current_week_utilization():
    """Test utilization with tasks in current week"""
    
    print("=== Testing Current Week Utilization ===")
    
    # Get a resource
    resource = Resource.objects.first()
    print(f"Resource: {resource.name} (capacity: {resource.capacity})")
    
    # Create a test task for current week
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    
    print(f"Current week: {start_of_week} to {end_of_week}")
    
    # Get or create a project
    project = Project.objects.first()
    if not project:
        print("❌ No project found")
        return
    
    # Create a test task for this week
    test_task = Task.objects.create(
        name="Test Current Week Task",
        description="Test task for utilization testing",
        project=project,
        start_date=start_of_week,
        end_date=end_of_week,
        estimated_hours=20,
        status="in_progress"
    )
    print(f"✅ Created test task: {test_task.name} ({test_task.start_date} to {test_task.end_date})")
    
    # Check initial utilization
    initial_util = resource.current_utilization()
    print(f"Initial utilization: {initial_util:.1f}%")
    
    # Create assignment
    assignment = Assignment.objects.create(
        resource=resource,
        task=test_task,
        allocated_hours=test_task.estimated_hours
    )
    print(f"✅ Created assignment: {assignment}")
    
    # Check utilization after assignment
    after_util = resource.current_utilization()
    print(f"Utilization after assignment: {after_util:.1f}%")
    
    # Expected utilization calculation:
    # 20 hours over 5 work days = 4 hours per day
    # Resource capacity is 40 hours per week = 8 hours per day
    # So utilization should be 4/8 = 50%
    expected_util = (20 / resource.capacity) * 100
    print(f"Expected utilization: {expected_util:.1f}%")
    
    # Update historical utilization
    utilization_service = UtilizationTrackingService()
    utilization_service.record_daily_utilization()
    print("✅ Updated historical utilization data")
    
    # Clean up
    assignment.delete()
    test_task.delete()
    print("✅ Cleaned up test data")
    
    # Final check
    final_util = resource.current_utilization()
    print(f"Final utilization: {final_util:.1f}%")
    
    # Results
    if abs(after_util - expected_util) < 1:
        print("✅ SUCCESS: Utilization calculation is correct")
    else:
        print(f"⚠️  WARNING: Expected {expected_util:.1f}%, got {after_util:.1f}%")

if __name__ == "__main__":
    test_current_week_utilization()
