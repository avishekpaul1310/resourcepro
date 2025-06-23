#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from allocation.models import Task, Assignment, Resource
from analytics.ai_services import AIResourceAllocationService

# Test utilization awareness in AI suggestions
client = Client()

# Get the admin user
user = User.objects.get(username='admin')
client.force_login(user)

print("=== Testing AI Utilization Awareness ===")

# Get resources and their current utilization
resources = Resource.objects.all()[:5]
print(f"\n📊 Current Resource Utilization:")
for resource in resources:
    utilization = resource.current_utilization()
    print(f"  {resource.name} ({resource.role}): {utilization}% utilization")

# Find a resource with high utilization
high_util_resource = None
for resource in resources:
    if resource.current_utilization() > 70:  # High but not over 90%
        high_util_resource = resource
        break

if not high_util_resource:
    # Find any resource and artificially increase their utilization by assigning more tasks
    test_resource = resources[0]
    print(f"\n🧪 Creating high utilization scenario for {test_resource.name}")
    
    # Get unassigned tasks to create assignments
    assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
    unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)[:3]
    
    created_assignments = []
    for task in unassigned_tasks:
        assignment = Assignment.objects.create(
            task=task,
            resource=test_resource,
            allocated_hours=task.estimated_hours
        )
        created_assignments.append(assignment)
        print(f"  Added assignment: {task.name} ({task.estimated_hours}h)")
    
    high_util_resource = test_resource
    utilization_after = test_resource.current_utilization()
    print(f"  {test_resource.name} utilization now: {utilization_after}%")

# Test AI suggestions for a new task
remaining_unassigned = Task.objects.exclude(id__in=Assignment.objects.values_list('task_id', flat=True))
if remaining_unassigned:
    test_task = remaining_unassigned.first()
    print(f"\n🤖 Testing AI suggestions for: {test_task.name} ({test_task.estimated_hours}h)")
    
    # Get AI suggestions
    ai_service = AIResourceAllocationService()
    suggestions = ai_service.suggest_optimal_resource_allocation(test_task.id, force_refresh=True)
    
    if suggestions and suggestions.get('success') != False:
        if 'suggestions' in suggestions:
            print(f"✅ AI returned {len(suggestions['suggestions'])} suggestions")
            
            for i, suggestion in enumerate(suggestions['suggestions']):
                resource_name = suggestion['resource']['name']
                match_score = suggestion['match_score']
                
                # Get the suggested resource and calculate what utilization would be
                suggested_resource = Resource.objects.get(id=suggestion['resource']['id'])
                current_util = suggested_resource.current_utilization()
                
                # Estimate new utilization (rough calculation)
                # This is simplified - doesn't account for date overlaps properly
                hours_per_week = suggested_resource.capacity
                estimated_additional_util = (test_task.estimated_hours / hours_per_week) * 100
                projected_util = current_util + estimated_additional_util
                
                print(f"  Suggestion {i+1}: {resource_name}")
                print(f"    Current utilization: {current_util}%")
                print(f"    Projected utilization: {projected_util:.1f}%")
                print(f"    Match score: {match_score}")
                print(f"    ⚠️ Over 100%: {'YES' if projected_util > 100 else 'NO'}")
                
                if projected_util > 100:
                    print(f"    🚨 WARNING: This assignment would overallocate the resource!")
        else:
            print(f"❌ AI suggestions failed: {suggestions.get('error', 'Unknown error')}")
    else:
        print(f"❌ AI suggestions failed: {suggestions}")

# Test the _get_available_resources method directly
print(f"\n🔍 Testing _get_available_resources method:")
if remaining_unassigned:
    test_task = remaining_unassigned.first()
    ai_service = AIResourceAllocationService()
    available_resources = ai_service._get_available_resources(test_task)
    
    print(f"Available resources for task '{test_task.name}':")
    for resource in available_resources:
        utilization = resource.current_utilization()
        print(f"  ✅ {resource.name}: {utilization}% utilization (< 90% threshold)")
    
    excluded_resources = Resource.objects.exclude(id__in=[r.id for r in available_resources])
    if excluded_resources:
        print(f"\nExcluded resources (≥90% utilization):")
        for resource in excluded_resources:
            utilization = resource.current_utilization()
            print(f"  ❌ {resource.name}: {utilization}% utilization")

# Clean up created assignments
if 'created_assignments' in locals():
    print(f"\n🧹 Cleaning up {len(created_assignments)} test assignments...")
    for assignment in created_assignments:
        assignment.delete()
    print("✅ Cleanup complete")

print(f"\n📋 Summary:")
print(f"- AI service has utilization filtering (90% threshold)")
print(f"- Resources above 90% utilization are excluded from suggestions")
print(f"- However, AI doesn't calculate if NEW task would cause over-allocation")
print(f"- This could lead to recommendations that push resources over 100%")
