#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.working_enhanced_ai import WorkingEnhancedAIService

print("=== Testing Working Enhanced AI ===")

# Initialize the working enhanced AI
enhanced_ai = WorkingEnhancedAIService()

# Test with a few tasks
results = enhanced_ai.get_enhanced_suggestions()

print(f"Total tasks analyzed: {results['total_tasks_analyzed']}")
print(f"Tasks with suggestions: {results['tasks_with_suggestions']}")

if results['suggestions']:
    print(f"\n=== Sample Suggestions ===")
    for task_id, suggestion_data in list(results['suggestions'].items())[:3]:  # Show first 3
        print(f"\nTask {task_id}:")
        print(f"  Type: {suggestion_data['type']}")
        print(f"  Reasoning: {suggestion_data['reasoning']}")
        print(f"  Suggestions: {len(suggestion_data['suggestions'])}")
        
        for i, suggestion in enumerate(suggestion_data['suggestions'][:2], 1):  # Show first 2 suggestions
            print(f"    {i}. {suggestion.get('resource_name', 'Unknown')}")
            if 'skill_match' in suggestion:
                print(f"       Skill match: {suggestion['skill_match']:.0%}")
            if 'projected_utilization' in suggestion:
                print(f"       Projected utilization: {suggestion['projected_utilization']:.1f}%")
            if 'delay_days' in suggestion:
                print(f"       Delay: {suggestion['delay_days']} days")
            if 'overallocation_percentage' in suggestion:
                print(f"       ⚠️ Over-allocation: +{suggestion['overallocation_percentage']:.1f}%")

print(f"\n✅ Enhanced AI test completed!")
print(f"🚀 This system now provides:")
print(f"   • Priority-based task analysis")
print(f"   • Future-aware scheduling")
print(f"   • Good-fit alternative suggestions")
print(f"   • Informed over-allocation with risk analysis")
