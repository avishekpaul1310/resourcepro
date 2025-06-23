#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from allocation.models import Assignment
from projects.models import Task
from resources.models import Resource

print("=== Testing Basic Enhanced AI Setup ===")

# Test basic imports and model access
print("Testing model imports...")

# Get unassigned tasks
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)

print(f"Total unassigned tasks: {unassigned_tasks.count()}")

# Test priority field
if unassigned_tasks.exists():
    first_task = unassigned_tasks.first()
    print(f"First task: {first_task.name}")
    print(f"Priority: {first_task.priority} (type: {type(first_task.priority)})")
    
    # Test skills access
    skills = first_task.skills_required.all()
    print(f"Skills required: {[skill.name for skill in skills]}")

# Test resources
resources = Resource.objects.all()
print(f"Total resources: {resources.count()}")

if resources.exists():
    first_resource = resources.first()
    print(f"First resource: {first_resource.name}")
    print(f"Skills: {[skill.name for skill in first_resource.skills.all()]}")

print("✅ Basic setup test completed successfully!")
