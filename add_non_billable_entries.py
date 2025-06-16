#!/usr/bin/env python
"""
Script to add some non-billable time entries for testing the billable filter.
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from resources.models import TimeEntry, Resource
from projects.models import Task
import random


def create_non_billable_entries():
    """Create some non-billable time entries for testing"""
    print("Creating non-billable time entries for testing...")
    
    # Get some existing resources and tasks
    resources = list(Resource.objects.all()[:3])  # Use first 3 resources
    tasks = list(Task.objects.all()[:5])  # Use first 5 tasks
    
    non_billable_entries = []
    
    # Create 10 non-billable entries
    for i in range(10):
        resource = random.choice(resources)
        task = random.choice(tasks)
        entry_date = date.today() - timedelta(days=random.randint(1, 30))
        hours = Decimal(str(round(random.uniform(0.5, 4.0), 2)))
        
        # Create non-billable entry
        entry = TimeEntry.objects.create(
            resource=resource,
            task=task,
            date=entry_date,
            hours=hours,
            description=f"Non-billable work: Training, meetings, or internal tasks",
            is_billable=False
        )
        non_billable_entries.append(entry)
        print(f"✓ Created non-billable entry: {resource.name} - {task.name} - {hours}h")
    
    print(f"\n✅ Created {len(non_billable_entries)} non-billable entries")
    
    # Show updated statistics
    total_entries = TimeEntry.objects.count()
    billable_entries = TimeEntry.objects.filter(is_billable=True).count()
    non_billable_entries_count = TimeEntry.objects.filter(is_billable=False).count()
    
    print(f"\nUpdated Statistics:")
    print(f"  Total entries: {total_entries}")
    print(f"  Billable entries: {billable_entries}")
    print(f"  Non-billable entries: {non_billable_entries_count}")


if __name__ == "__main__":
    create_non_billable_entries()
