#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.working_enhanced_ai import WorkingEnhancedAIService
from allocation.models import Assignment
from projects.models import Task
from resources.models import Resource

print("🔍 ENHANCED AI DIAGNOSTIC TEST")
print("=" * 50)

# Initialize enhanced AI
enhanced_ai = WorkingEnhancedAIService()

# Get a few sample tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)
sample_tasks = unassigned_tasks[:5]

print(f"📊 RESOURCE UTILIZATION OVERVIEW:")
print("-" * 30)

resources = Resource.objects.all()[:10]  # Check first 10 resources
for resource in resources:
    current_util = resource.current_utilization()
    print(f"{resource.name}: {current_util:.1f}% utilization")

print(f"\n🎯 TESTING ENHANCED AI ON SAMPLE TASKS:")
print("-" * 40)

for task in sample_tasks:
    print(f"\nTask: {task.name}")
    print(f"Priority: {task.priority}/5")
    print(f"Hours: {task.estimated_hours}h")
    print(f"Skills: {', '.join([skill.name for skill in task.skills_required.all()])}")
    
    # Test each pass individually
    print(f"\n📋 TESTING AI PASSES:")
    
    # Pass 1: Ideal assignments
    ideal_suggestions = enhanced_ai._find_ideal_assignments(task)
    print(f"   Pass 1 (Ideal): {len(ideal_suggestions)} suggestions")
    if ideal_suggestions:
        for s in ideal_suggestions[:2]:
            print(f"      • {s['resource_name']}: {s['skill_match']:.0%} skill match, {s['projected_utilization']:.1f}% projected util")
    
    # Pass 2: Future assignments
    future_suggestions = enhanced_ai._find_future_assignments(task)
    print(f"   Pass 2 (Future): {len(future_suggestions)} suggestions")
    if future_suggestions:
        for s in future_suggestions[:2]:
            print(f"      • {s['resource_name']}: {s['skill_match']:.0%} skill match, {s['delay_days']} days delay")
    
    # Pass 3: Good fit assignments
    good_fit_suggestions = enhanced_ai._find_good_fit_assignments(task)
    print(f"   Pass 3 (Good Fit): {len(good_fit_suggestions)} suggestions")
    if good_fit_suggestions:
        for s in good_fit_suggestions[:2]:
            print(f"      • {s['resource_name']}: {s['skill_match']:.0%} skill match, gaps: {', '.join(s['skill_gap']) if s['skill_gap'] else 'None'}")
    
    # Pass 4: Over-allocation (only for high priority)
    if task.priority >= 4:
        over_suggestions = enhanced_ai._find_overallocation_assignments(task)
        print(f"   Pass 4 (Over-allocation): {len(over_suggestions)} suggestions")
        if over_suggestions:
            for s in over_suggestions[:2]:
                print(f"      • {s['resource_name']}: {s['skill_match']:.0%} skill match, +{s['overallocation_percentage']:.1f}% over-allocation")
    else:
        print(f"   Pass 4 (Over-allocation): Skipped (priority {task.priority} < 4)")
    
    print("-" * 40)

print(f"\n💡 DIAGNOSTIC INSIGHTS:")
print("If the enhanced AI is finding fewer suggestions than expected, it could be because:")
print("1. Most resources are already heavily utilized")
print("2. Skills don't match well between resources and tasks")  
print("3. Tasks are very large (many hours) making utilization calculations restrictive")
print("4. Resource capacity calculations might need adjustment")

print(f"\n🔧 RECOMMENDATIONS:")
print("1. Consider adjusting resource capacities if they're too conservative")
print("2. Review skill mappings between resources and tasks")
print("3. Consider splitting large tasks into smaller chunks")
print("4. Implement the 'task splitting' and 'collaborative assignment' features for better coverage")
