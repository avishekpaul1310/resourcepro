#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.enhanced_ai_services import EnhancedAIResourceAllocationService
from allocation.models import Task, Assignment

print("=== Testing Enhanced AI Task Suggestions ===")

# Get unassigned tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

print(f"Total unassigned tasks: {unassigned_tasks.count()}")

# Initialize enhanced AI service
enhanced_ai = EnhancedAIResourceAllocationService()

# Test the enhanced suggestions
test_task_ids = list(unassigned_tasks.values_list('id', flat=True)[:5])  # Test first 5 tasks
print(f"Testing with task IDs: {test_task_ids}")

results = enhanced_ai.get_enhanced_task_suggestions(test_task_ids)

print(f"\n=== Enhanced AI Results ===")
print(f"Total tasks analyzed: {results['total_tasks_analyzed']}")
print(f"Tasks with suggestions: {results['tasks_with_suggestions']}")

print(f"\n=== Detailed Suggestions ===")
for task_id, suggestion_data in results['suggestions'].items():
    task = Task.objects.get(id=task_id)
    print(f"\nTask {task_id}: {task.name}")
    print(f"  Priority: {getattr(task, 'priority', 'medium')}")
    print(f"  Estimated hours: {task.estimated_hours}")
    print(f"  Type: {suggestion_data['type']}")
    print(f"  Reasoning: {suggestion_data['reasoning']}")
    
    for i, suggestion in enumerate(suggestion_data['suggestions'], 1):
        print(f"  Suggestion {i}:")
        if suggestion_data['type'] == 'ideal':
            print(f"    Resource: {suggestion['resource_name']}")
            print(f"    Skill match: {suggestion['skill_match']:.2f}")
            print(f"    Current utilization: {suggestion['current_utilization']:.1f}%")
            print(f"    Projected utilization: {suggestion['projected_utilization']:.1f}%")
            
        elif suggestion_data['type'] == 'future_scheduled':
            print(f"    Resource: {suggestion['resource_name']}")
            print(f"    Skill match: {suggestion['skill_match']:.2f}")
            print(f"    Delay: {suggestion['delay_days']} days")
            print(f"    Suggested start: {suggestion['suggested_start_date']}")
            
        elif suggestion_data['type'] == 'collaborative':
            if suggestion.get('collaborators'):
                print(f"    Collaborative assignment:")
                for collab in suggestion['collaborators']:
                    print(f"      - {collab['resource_name']}: {collab['available_hours']:.1f}h available")
                print(f"    Total coverage: {suggestion['coverage_percentage']:.1f}%")
            else:
                print(f"    Task splitting suggested over {suggestion.get('total_duration_weeks', 'N/A')} weeks")
                
        elif suggestion_data['type'] == 'good_fit':
            print(f"    Resource: {suggestion['resource_name']}")
            print(f"    Skill match: {suggestion['skill_match']:.2f}")
            print(f"    Skill gaps: {suggestion.get('skill_gap', [])}")
            print(f"    Mentoring needed: {suggestion.get('mentoring_needed', False)}")
            
        elif suggestion_data['type'] == 'overallocation':
            print(f"    Resource: {suggestion['resource_name']}")
            print(f"    Skill match: {suggestion['skill_match']:.2f}")
            print(f"    ⚠️ Over-allocation: {suggestion['overallocation_percentage']:.1f}%")
            print(f"    Risk: {suggestion['risk_analysis']['delay_risk']}")
            print(f"    Mitigation options:")
            for option in suggestion['mitigation_options'][:2]:
                print(f"      - {option['description']} ({option['cost_impact']} impact)")

print(f"\n=== Summary ===")
print("The enhanced AI now provides:")
print("✅ Priority-based task analysis")
print("✅ Future-aware scheduling recommendations") 
print("✅ Collaborative assignment options")
print("✅ Adjacent skill matching")
print("✅ Informed over-allocation with risk analysis")
print("✅ Specific mitigation strategies")
