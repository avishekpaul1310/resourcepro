#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from allocation.models import Task, Assignment, Resource
from projects.models import Project

print('=== TASKS ===')
for task in Task.objects.all()[:10]:
    print(f'Task {task.id}: {task.name} (Project: {task.project.name if task.project else "None"})')

print('\n=== TASK ASSIGNMENTS ===')
for assignment in Assignment.objects.all()[:10]:
    print(f'Assignment {assignment.id}: Task {assignment.task.id} -> Resource {assignment.resource.name}')

print('\n=== RESOURCES ===')
for resource in Resource.objects.all()[:5]:
    print(f'Resource {resource.id}: {resource.name} ({resource.role})')

print('\n=== UNASSIGNED TASKS ===')
assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)
for task in unassigned_tasks[:5]:
    print(f'Unassigned Task {task.id}: {task.name} (Project: {task.project.name if task.project else "None"})')

print(f'\nTotal tasks: {Task.objects.count()}')
print(f'Total assignments: {Assignment.objects.count()}')
print(f'Total unassigned tasks: {unassigned_tasks.count()}')
