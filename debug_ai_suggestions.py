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

print("=== Debugging AI Task Suggestions Issue ===")

# Get all unassigned tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

print(f"Total unassigned tasks: {unassigned_tasks.count()}")

# Initialize AI service
ai_service = AIResourceAllocationService()

suggestions_count = 0
no_suggestions_count = 0

print("\n=== Analyzing each unassigned task ===")

for task in unassigned_tasks[:13]:  # Check the first 13 tasks
    print(f"\nTask {task.id}: {task.name}")
    print(f"  Estimated hours: {task.estimated_hours}")
    print(f"  Duration: {task.start_date} to {task.end_date}")
    print(f"  Skills required: {[skill.name for skill in task.skills_required.all()]}")
    
    # Get available resources for this task
    available_resources = ai_service._get_available_resources(task)
    print(f"  Available resources: {len(available_resources)}")
    
    if available_resources:        # Try to get AI suggestions
        try:
            suggestions = ai_service.suggest_optimal_resource_allocation(task.id)
            if suggestions and suggestions.get('suggestions'):
                suggestions_count += 1
                print(f"  ✅ AI returned {len(suggestions['suggestions'])} suggestion(s)")
                for i, suggestion in enumerate(suggestions['suggestions'], 1):
                    resource_name = suggestion.get('resource_name', 'Unknown')
                    match_score = suggestion.get('match_score', 0)
                    print(f"    {i}. {resource_name} (score: {match_score})")
            else:
                no_suggestions_count += 1
                print(f"  ❌ AI returned no suggestions (but {len(available_resources)} resources available)")
        except Exception as e:
            no_suggestions_count += 1
            print(f"  ❌ AI error: {str(e)}")
    else:
        no_suggestions_count += 1
        print(f"  ❌ No available resources (all above utilization limits)")
          # Show why resources are excluded
        print("  Resource exclusion details:")
        for resource in Resource.objects.all()[:5]:  # Show first 5 resources
            current_util = resource.current_utilization()
            projected_util = ai_service._calculate_projected_utilization(resource, task)
            
            if current_util >= 90:
                print(f"    {resource.name}: Current utilization {current_util}% >= 90%")
            elif projected_util >= 100:
                print(f"    {resource.name}: Projected utilization {projected_util}% >= 100%")

print(f"\n=== Summary ===")
print(f"Tasks with AI suggestions: {suggestions_count}")
print(f"Tasks without AI suggestions: {no_suggestions_count}")
print(f"Total analyzed: {suggestions_count + no_suggestions_count}")
