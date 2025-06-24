#!/usr/bin/env python
"""
Debug utilization calculation
"""

import os
import django
import sys

# Add the project root to the Python path
project_root = r'c:\Users\Avishek Paul\resourcepro'
sys.path.append(project_root)
os.chdir(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource
from projects.models import Task
from allocation.models import Assignment
from django.utils import timezone
from datetime import timedelta

def debug_utilization():
    """Debug utilization calculation"""
    
    print("=== Debugging Utilization Calculation ===")
    
    # Get a resource
    resource = Resource.objects.first()
    print(f"Resource: {resource.name}")
    print(f"Resource capacity: {resource.capacity}")
    
    # Check current date and week
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    print(f"Today: {today}")
    print(f"Week start: {start_of_week}")
    print(f"Week end: {end_of_week}")
    
    # Check assignments
    assignments = Assignment.objects.filter(
        resource=resource,
        task__start_date__lte=end_of_week,
        task__end_date__gte=start_of_week
    )
    
    print(f"Current assignments: {assignments.count()}")
    for assignment in assignments:
        print(f"  - {assignment.task.name}: {assignment.allocated_hours}h")
        print(f"    Task dates: {assignment.task.start_date} to {assignment.task.end_date}")
    
    # Check all tasks
    all_tasks = Task.objects.all()[:5]
    print(f"\nSample tasks:")
    for task in all_tasks:
        print(f"  - {task.name}: {task.start_date} to {task.end_date}")
    
    # Calculate current utilization manually
    utilization = resource.current_utilization()
    print(f"\nCurrent utilization: {utilization:.1f}%")

if __name__ == "__main__":
    debug_utilization()
