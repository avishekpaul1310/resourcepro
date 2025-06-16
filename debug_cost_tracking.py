#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from projects.models import Project
from resources.models import Resource
from analytics.services import CostTrackingService

print("=== TESTING COST TRACKING SERVICE ===")

# Test the cost tracking service
cost_service = CostTrackingService()

print("\n1. Testing get_cost_variance_report():")
try:
    cost_report = cost_service.get_cost_variance_report()
    print(f"Cost report returned {len(cost_report)} items")
    
    if cost_report:
        for i, item in enumerate(cost_report[:3]):
            print(f"Item {i+1}:")
            print(f"  Project: {item.get('project', 'Unknown')}")
            print(f"  Estimated Cost: ${item.get('estimated_cost', 0)}")
            print(f"  Actual Cost: ${item.get('actual_cost', 0)}")
            print(f"  Variance: ${item.get('variance', 0)}")
            print(f"  Budget: ${item.get('budget', 'No budget')}")
    else:
        print("No cost report data returned")
except Exception as e:
    print(f"Error in cost_variance_report: {e}")

print("\n2. Testing individual project cost methods:")
projects = Project.objects.all()[:3]
for project in projects:
    print(f"\nProject: {project.name}")
    try:
        estimated = project.get_estimated_cost()
        print(f"  Estimated cost: ${estimated}")
    except Exception as e:
        print(f"  Error getting estimated cost: {e}")
    
    try:
        actual = project.get_actual_cost()
        print(f"  Actual cost: ${actual}")
    except Exception as e:
        print(f"  Error getting actual cost: {e}")
    
    try:
        variance = project.get_budget_variance()
        print(f"  Budget variance: ${variance}")
    except Exception as e:
        print(f"  Error getting budget variance: {e}")

print("\n3. Checking resource cost_per_hour values:")
resources = Resource.objects.all()
resources_with_rate = 0
total_resources = resources.count()

for resource in resources:
    if resource.cost_per_hour:
        resources_with_rate += 1
        print(f"  {resource.name}: ${resource.cost_per_hour}/hour")

print(f"\nResources with cost_per_hour set: {resources_with_rate}/{total_resources}")

print("\n4. Checking assignments and time entries:")
try:
    from allocation.models import Assignment
    assignments = Assignment.objects.all()
    print(f"Total assignments: {assignments.count()}")
    
    for assignment in assignments[:3]:
        print(f"  Assignment: {assignment.resource.name} -> {assignment.task.project.name}")
        print(f"    Allocated hours: {assignment.allocated_hours}")
        print(f"    Resource rate: ${assignment.resource.cost_per_hour or 0}/hour")
except Exception as e:
    print(f"Error checking assignments: {e}")

try:
    from resources.models import TimeEntry
    time_entries = TimeEntry.objects.all()
    print(f"Total time entries: {time_entries.count()}")
    
    for entry in time_entries[:3]:
        print(f"  Time entry: {entry.resource.name} -> {entry.task.project.name}")
        print(f"    Hours: {entry.hours}")
        print(f"    Resource rate: ${entry.resource.cost_per_hour or 0}/hour")
except Exception as e:
    print(f"Error checking time entries: {e}")
