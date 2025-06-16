#!/usr/bin/env python
"""
Test script to verify the time tracking filtering functionality.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from resources.models import TimeEntry, Resource
from projects.models import Project, Task


def test_time_tracking_data():
    """Test that time tracking data is available and properly structured"""
    print("Testing Time Tracking Data Structure")
    print("=" * 50)
    
    # Check basic data availability
    total_entries = TimeEntry.objects.count()
    total_resources = Resource.objects.count()
    total_projects = Project.objects.count()
    total_tasks = Task.objects.count()
    
    print(f"✓ Time Entries: {total_entries}")
    print(f"✓ Resources: {total_resources}")
    print(f"✓ Projects: {total_projects}")
    print(f"✓ Tasks: {total_tasks}")
    
    if total_entries == 0:
        print("❌ No time entries found!")
        return False
    
    # Test data relationships
    entry = TimeEntry.objects.select_related('resource', 'task', 'task__project').first()
    print(f"\nSample Entry:")
    print(f"  Resource: {entry.resource.name}")
    print(f"  Task: {entry.task.name}")
    print(f"  Project: {entry.task.project.name}")
    print(f"  Hours: {entry.hours}")
    print(f"  Billable: {entry.is_billable}")
    print(f"  Date: {entry.date}")
    
    return True


def test_filtering_functionality():
    """Test the filtering functionality"""
    print("\n\nTesting Filtering Functionality")
    print("=" * 50)
    
    # Test basic queries that the view uses
    try:
        # Test total hours calculation
        from django.db.models import Sum, Count
        
        stats = TimeEntry.objects.aggregate(
            total_entries=Count('id'),
            total_hours=Sum('hours')
        )
        
        billable_stats = TimeEntry.objects.filter(is_billable=True).aggregate(
            billable_hours=Sum('hours')
        )
        
        print(f"✓ Total Entries: {stats['total_entries']}")
        print(f"✓ Total Hours: {stats['total_hours']}")
        print(f"✓ Billable Hours: {billable_stats['billable_hours']}")
        
        # Test filtering by resource
        first_resource = Resource.objects.first()
        resource_entries = TimeEntry.objects.filter(resource=first_resource).count()
        print(f"✓ Entries for {first_resource.name}: {resource_entries}")
        
        # Test filtering by project
        first_project = Project.objects.first()
        project_entries = TimeEntry.objects.filter(task__project=first_project).count()
        print(f"✓ Entries for {first_project.name}: {project_entries}")
        
        # Test billable filtering
        billable_entries = TimeEntry.objects.filter(is_billable=True).count()
        non_billable_entries = TimeEntry.objects.filter(is_billable=False).count()
        print(f"✓ Billable entries: {billable_entries}")
        print(f"✓ Non-billable entries: {non_billable_entries}")
        
        return True
        
    except Exception as e:
        print(f"❌ Filtering test failed: {e}")
        return False


def test_estimated_value_calculation():
    """Test the estimated value calculation"""
    print("\n\nTesting Estimated Value Calculation")
    print("=" * 50)
    
    try:
        from django.db.models import Sum
        
        # Get billable entries
        billable_entries = TimeEntry.objects.filter(is_billable=True)
        billable_hours = billable_entries.aggregate(Sum('hours'))['hours__sum'] or Decimal('0')
        
        # Get resources with cost per hour that have billable time
        resources_with_billable_time = Resource.objects.filter(
            time_entries__in=billable_entries,
            cost_per_hour__isnull=False
        ).distinct()
        
        print(f"✓ Billable hours: {billable_hours}")
        print(f"✓ Resources with billable time and cost rates: {resources_with_billable_time.count()}")
        
        if resources_with_billable_time.exists() and billable_hours > 0:
            total_cost_per_hour = sum(r.cost_per_hour for r in resources_with_billable_time)
            avg_cost_per_hour = total_cost_per_hour / len(resources_with_billable_time)
            estimated_value = billable_hours * avg_cost_per_hour
            print(f"✓ Average cost per hour: ${avg_cost_per_hour}")
            print(f"✓ Estimated value: ${estimated_value}")
        else:
            print("! No cost data available for estimated value calculation")
        
        return True
        
    except Exception as e:
        print(f"❌ Estimated value test failed: {e}")
        return False


if __name__ == "__main__":
    print("Time Tracking Functionality Test")
    print("=" * 60)
    
    test1 = test_time_tracking_data()
    test2 = test_filtering_functionality()
    test3 = test_estimated_value_calculation()
    
    print("\n" + "=" * 60)
    if test1 and test2 and test3:
        print("✅ All tests passed! Time tracking should work properly.")
    else:
        print("❌ Some tests failed. Check the implementation.")
