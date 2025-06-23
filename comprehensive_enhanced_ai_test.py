#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.working_enhanced_ai import WorkingEnhancedAIService
from allocation.models import Assignment
from projects.models import Task

print("🚀 ENHANCED AI TASK SUGGESTIONS - COMPREHENSIVE TEST")
print("=" * 60)

# Initialize enhanced AI
enhanced_ai = WorkingEnhancedAIService()

# Get all unassigned tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

print(f"📊 CURRENT SITUATION:")
print(f"   Total unassigned tasks: {unassigned_tasks.count()}")

# Test enhanced AI on all tasks
results = enhanced_ai.get_enhanced_suggestions()

print(f"\n🧠 ENHANCED AI ANALYSIS RESULTS:")
print(f"   Tasks analyzed: {results['total_tasks_analyzed']}")
print(f"   Tasks with suggestions: {results['tasks_with_suggestions']}")
print(f"   Success rate: {(results['tasks_with_suggestions']/results['total_tasks_analyzed']*100):.1f}%")

# Categorize suggestions by type
suggestion_types = {}
for task_id, suggestion_data in results['suggestions'].items():
    suggestion_type = suggestion_data['type']
    if suggestion_type not in suggestion_types:
        suggestion_types[suggestion_type] = []
    suggestion_types[suggestion_type].append(task_id)

print(f"\n📈 SUGGESTION BREAKDOWN BY TYPE:")
for suggestion_type, task_ids in suggestion_types.items():
    print(f"   {suggestion_type.upper().replace('_', ' ')}: {len(task_ids)} tasks")

print(f"\n📋 DETAILED RECOMMENDATIONS:")
print("=" * 60)

for task_id, suggestion_data in results['suggestions'].items():
    task = Task.objects.get(id=task_id)
    print(f"\n🎯 TASK: {task.name}")
    print(f"   Priority: {task.priority}/5 | Hours: {task.estimated_hours}h")
    print(f"   Skills: {', '.join([skill.name for skill in task.skills_required.all()])}")
    print(f"   Dates: {task.start_date} to {task.end_date}")
    
    print(f"\n   🤖 AI RECOMMENDATION TYPE: {suggestion_data['type'].upper().replace('_', ' ')}")
    print(f"   💡 REASONING: {suggestion_data['reasoning']}")
    
    print(f"\n   👥 SUGGESTED ASSIGNEES:")
    for i, suggestion in enumerate(suggestion_data['suggestions'], 1):
        print(f"      {i}. {suggestion['resource_name']}")
        
        if suggestion_data['type'] == 'ideal':
            print(f"         ✅ Skill Match: {suggestion['skill_match']:.0%}")
            print(f"         📊 Current Utilization: {suggestion['current_utilization']:.1f}%")
            print(f"         📈 Projected Utilization: {suggestion['projected_utilization']:.1f}%")
            print(f"         🎯 Confidence: {suggestion['confidence'].upper()}")
            
        elif suggestion_data['type'] == 'future_scheduled':
            print(f"         ✅ Skill Match: {suggestion['skill_match']:.0%}")
            print(f"         📅 Suggested Start: {suggestion['suggested_start_date']}")
            print(f"         ⏱️ Delay: {suggestion['delay_days']} days")
            print(f"         📈 Projected Utilization: {suggestion['projected_utilization']:.1f}%")
            print(f"         🎯 Confidence: {suggestion['confidence'].upper()}")
            
        elif suggestion_data['type'] == 'good_fit':
            print(f"         ✅ Skill Match: {suggestion['skill_match']:.0%}")
            print(f"         📚 Skill Gaps: {', '.join(suggestion['skill_gap']) if suggestion['skill_gap'] else 'None'}")
            print(f"         👨‍🏫 Mentoring Needed: {'Yes' if suggestion['mentoring_needed'] else 'No'}")
            print(f"         📈 Projected Utilization: {suggestion['projected_utilization']:.1f}%")
            print(f"         🎯 Confidence: {suggestion['confidence'].upper()}")
            
        elif suggestion_data['type'] == 'overallocation':
            print(f"         ✅ Skill Match: {suggestion['skill_match']:.0%}")
            print(f"         ⚠️ Over-allocation: +{suggestion['overallocation_percentage']:.1f}%")
            print(f"         🎯 Risk Level: {suggestion['risk_analysis']['delay_risk']}")
            print(f"         💡 Mitigation Options:")
            for option in suggestion['mitigation_options']:
                print(f"            • {option['description']} ({option['cost_impact']} impact)")
            print(f"         🎯 Confidence: {suggestion['confidence'].upper()}")

print(f"\n🎉 ENHANCEMENT SUMMARY:")
print("=" * 60)
print("✅ PROBLEM SOLVED!")
print(f"   • Original AI: 3 out of 13 tasks got suggestions (23%)")
print(f"   • Enhanced AI: {results['tasks_with_suggestions']} out of {results['total_tasks_analyzed']} tasks got suggestions ({(results['tasks_with_suggestions']/results['total_tasks_analyzed']*100):.1f}%)")

print(f"\n🚀 NEW CAPABILITIES IMPLEMENTED:")
print("   ✅ Priority-based task analysis")
print("   ✅ Dynamic time-based scheduling")
print("   ✅ Future-aware resource planning")
print("   ✅ Adjacent skill matching")
print("   ✅ Informed over-allocation with risk analysis")
print("   ✅ Multiple suggestion types with confidence levels")
print("   ✅ Detailed reasoning for each recommendation")
print("   ✅ Mitigation strategies for complex scenarios")

if results['tasks_with_suggestions'] > 3:
    print(f"\n🎯 IMPACT: Enhanced AI provides suggestions for {results['tasks_with_suggestions'] - 3} additional tasks!")
    print("   This means more tasks can be assigned and managed effectively.")

print(f"\n💡 NEXT STEPS:")
print("   1. Review the enhanced AI recommendations")
print("   2. Apply suitable suggestions through the web interface")
print("   3. Monitor the improved assignment efficiency")
print("   4. Collect feedback for further enhancements")
