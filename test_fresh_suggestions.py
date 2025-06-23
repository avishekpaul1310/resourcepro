#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from allocation.models import Task, Assignment, Resource
from analytics.ai_services import AIResourceAllocationService
from analytics.models import AIResourceAllocationSuggestion

# Clear all cached AI suggestions to force fresh generation
print("=== Clearing AI Suggestion Cache ===")
deleted_count = AIResourceAllocationSuggestion.objects.all().delete()[0]
print(f"Deleted {deleted_count} cached suggestions")

# Test with fresh suggestions
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

if unassigned_tasks:
    test_task = unassigned_tasks.first()
    print(f"\nTesting task: {test_task.id} - {test_task.name}")
    
    ai_service = AIResourceAllocationService()
    
    # Test the available resources filtering directly
    print(f"\n=== Available Resources Filtering (Direct Test) ===")
    available_resources = ai_service._get_available_resources(test_task)
    
    print(f"Total resources in system: {Resource.objects.count()}")
    print(f"Available resources after filtering: {len(available_resources)}")
    
    if available_resources:
        print("\nAvailable resources:")
        for resource in available_resources:
            current_util = resource.current_utilization()
            projected_util = ai_service._calculate_projected_utilization(resource, test_task)
            print(f"  - {resource.name} ({resource.role}): {current_util}% -> {projected_util}%")
    else:
        print("\n❌ No resources meet the utilization criteria!")
        
        print("\nAll resources and their utilizations:")
        for resource in Resource.objects.all()[:10]:
            current_util = resource.current_utilization()
            projected_util = ai_service._calculate_projected_utilization(resource, test_task)
            print(f"  - {resource.name}: {current_util}% -> {projected_util}% (exceeds threshold)")
    
    # Test the full AI suggestion process with force_refresh
    print(f"\n=== Testing AI Suggestions (Force Refresh) ===")
    suggestions = ai_service.suggest_optimal_resource_allocation(
        task_id=test_task.id, 
        force_refresh=True
    )
    
    if suggestions.get('error'):
        print(f"✅ Expected error due to no available resources: {suggestions['error']}")
    elif suggestions.get('suggestions'):
        print(f"⚠️  Unexpected: AI still returned {len(suggestions['suggestions'])} suggestions")
        for suggestion in suggestions['suggestions']:
            print(f"  - {suggestion['resource']['name']}: {suggestion['match_score']}")
    else:
        print("✅ No suggestions returned (expected)")

else:
    print("❌ No unassigned tasks available")
