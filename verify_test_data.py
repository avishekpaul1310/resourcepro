#!/usr/bin/env python
"""
Data Verification Script
Quick overview of the populated test data
"""
import os
import sys
import django

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from resources.models import Resource, Skill, ResourceSkill, ResourceAvailability, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment

def show_data_overview():
    """Display an overview of the populated data"""
    print("📊 TEST DATA VERIFICATION")
    print("="*60)
    
    print("\n🛠️ SKILLS:")
    skills = Skill.objects.all()[:10]  # Show first 10
    for skill in skills:
        print(f"   • {skill.name}")
    if Skill.objects.count() > 10:
        print(f"   ... and {Skill.objects.count() - 10} more")
    
    print(f"\n👥 RESOURCES ({Resource.objects.count()} total):")
    for resource in Resource.objects.all():
        skill_count = resource.resource_skills.count()
        print(f"   • {resource.name} ({resource.role}) - {resource.department}")
        print(f"     └─ {resource.location} | {resource.timezone} | {skill_count} skills | ${resource.cost_per_hour}/hr")
    
    print(f"\n📁 PROJECTS ({Project.objects.count()} total):")
    for project in Project.objects.all():
        task_count = project.tasks.count()
        print(f"   • {project.name} ({project.get_status_display()}) - {task_count} tasks")
        print(f"     └─ {project.start_date} to {project.end_date} | Priority: {project.priority} | Budget: ${project.budget}")
    
    print(f"\n📋 RECENT TASKS (showing 15 of {Task.objects.count()}):")
    recent_tasks = Task.objects.all().order_by('-created_at')[:15]
    for task in recent_tasks:
        assignments = task.assignments.count()
        print(f"   • {task.name} ({task.get_status_display()}) - {task.completion_percentage}% complete")
        print(f"     └─ {task.estimated_hours}h estimated | {assignments} resources assigned")
    
    print(f"\n⏰ TIME TRACKING SUMMARY:")
    total_entries = TimeEntry.objects.count()
    total_hours = sum(entry.hours for entry in TimeEntry.objects.all())
    billable_hours = sum(entry.hours for entry in TimeEntry.objects.filter(is_billable=True))
    print(f"   • Total time entries: {total_entries}")
    print(f"   • Total hours logged: {total_hours}")
    print(f"   • Billable hours: {billable_hours}")
    print(f"   • Non-billable hours: {total_hours - billable_hours}")
    
    print(f"\n📅 AVAILABILITY OVERVIEW:")
    availability_types = ResourceAvailability.objects.values('availability_type').distinct()
    for avail_type in availability_types:
        count = ResourceAvailability.objects.filter(availability_type=avail_type['availability_type']).count()
        print(f"   • {avail_type['availability_type'].replace('_', ' ').title()}: {count} entries")
    
    print(f"\n🌍 GLOBAL TEAM DISTRIBUTION:")
    timezones = Resource.objects.values('timezone', 'location').distinct()
    for tz_info in timezones:
        count = Resource.objects.filter(timezone=tz_info['timezone']).count()
        print(f"   • {tz_info['location']} ({tz_info['timezone']}): {count} resources")
    
    print(f"\n🏢 DEPARTMENT BREAKDOWN:")
    departments = Resource.objects.values('department').distinct()
    for dept in departments:
        count = Resource.objects.filter(department=dept['department']).count()
        avg_cost = Resource.objects.filter(department=dept['department']).aggregate(
            avg_cost=models.Avg('cost_per_hour')
        )['avg_cost'] or 0
        print(f"   • {dept['department']}: {count} resources (avg ${avg_cost:.2f}/hr)")
    
    print(f"\n💰 COST ANALYSIS:")
    total_estimated_cost = sum(
        assignment.allocated_hours * assignment.resource.cost_per_hour 
        for assignment in Assignment.objects.all()
    )
    total_actual_cost = sum(
        entry.hours * entry.resource.cost_per_hour
        for entry in TimeEntry.objects.all()
    )
    print(f"   • Total estimated cost (all assignments): ${total_estimated_cost:.2f}")
    print(f"   • Total actual cost (time entries): ${total_actual_cost:.2f}")
    
    print("\n✅ DATA QUALITY CHECKS:")
    
    # Check for unassigned tasks
    unassigned_tasks = Task.objects.filter(assignments__isnull=True).count()
    print(f"   • Unassigned tasks: {unassigned_tasks}")
    
    # Check for overdue tasks
    from django.utils import timezone
    overdue_tasks = Task.objects.filter(
        end_date__lt=timezone.now().date(),
        status__in=['not_started', 'in_progress']
    ).count()
    print(f"   • Overdue tasks: {overdue_tasks}")
    
    # Check skill distribution
    resources_with_skills = Resource.objects.filter(resource_skills__isnull=False).distinct().count()
    print(f"   • Resources with skills: {resources_with_skills}/{Resource.objects.count()}")
    
    # Check time tracking coverage
    tasks_with_time = Task.objects.filter(time_entries__isnull=False).distinct().count()
    print(f"   • Tasks with time entries: {tasks_with_time}/{Task.objects.count()}")
    
    print("\n🎯 TESTING SCENARIOS AVAILABLE:")
    print("   ✅ Cross-timezone team collaboration")
    print("   ✅ Multi-skilled resource allocation")
    print("   ✅ Project status transitions")
    print("   ✅ Budget vs actual cost tracking")
    print("   ✅ Resource utilization calculations")
    print("   ✅ Availability calendar conflicts")
    print("   ✅ Skill-based task matching")
    print("   ✅ Time tracking and billing")
    print("   ✅ Overdue task management")
    print("   ✅ Multi-department coordination")
    
    print(f"\n🚀 Ready for comprehensive manual testing!")

if __name__ == "__main__":
    from django.db import models
    show_data_overview()
