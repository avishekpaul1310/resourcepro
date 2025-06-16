#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from projects.models import Project
from resources.models import Resource

print("=== PROJECT DATA ===")
projects = Project.objects.all()
print(f"Total projects: {projects.count()}")

if projects.count() > 0:
    for p in projects[:5]:
        print(f"Project: {p.name}")
        print(f"  Budget: {getattr(p, 'budget', 'No budget field')}")
        print(f"  Status: {p.status}")
        print(f"  Start: {p.start_date}, End: {p.end_date}")
        print()

print("=== RESOURCE DATA ===")
resources = Resource.objects.all()
print(f"Total resources: {resources.count()}")

if resources.count() > 0:
    for r in resources[:5]:
        username = r.user.username if r.user else "No user assigned"
        print(f"Resource: {username}")
        print(f"  Name: {getattr(r, 'name', 'No name field')}")
        # Check for different possible field names for hourly rate
        cost_field = None
        for field_name in ['cost_per_hour', 'hourly_rate', 'rate']:
            if hasattr(r, field_name):
                cost_field = getattr(r, field_name)
                print(f"  {field_name}: {cost_field}")
                break
        if not cost_field:
            print("  No cost/rate field found")
        print()

print("=== PROJECT MODEL FIELDS ===")
project_fields = [f.name for f in Project._meta.get_fields()]
print("Available fields:", project_fields)

print("\n=== RESOURCE MODEL FIELDS ===")
resource_fields = [f.name for f in Resource._meta.get_fields()]
print("Available fields:", resource_fields)
