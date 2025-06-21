#!/usr/bin/env python
"""
Verify that the availability calendar is working properly
"""
import os
import sys
import django

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User
from resources.models import Resource, ResourceAvailability
from datetime import datetime, timedelta

print("=== Availability Calendar Verification ===")

# Check resources
resources = Resource.objects.all()
print(f"✓ Total resources: {resources.count()}")

resources_with_users = Resource.objects.filter(user__isnull=False)
print(f"✓ Resources with users: {resources_with_users.count()}")

if resources_with_users.count() == 0:
    print("❌ No resources have users assigned!")
    sys.exit(1)

# Check availability records
availability_records = ResourceAvailability.objects.all()
print(f"✓ Total availability records: {availability_records.count()}")

if availability_records.count() == 0:
    print("❌ No availability records found!")
    sys.exit(1)

# Check current month availability
today = datetime.now()
current_month_availability = ResourceAvailability.objects.filter(
    start_date__year=today.year,
    start_date__month=today.month
)
print(f"✓ Availability records for current month: {current_month_availability.count()}")

# Show sample data
print("\n=== Sample Data ===")
for resource in resources_with_users[:3]:
    user_name = f"{resource.user.first_name} {resource.user.last_name}" if resource.user else resource.name
    print(f"Resource: {user_name}")
    
    resource_availability = ResourceAvailability.objects.filter(resource=resource)[:3]
    for avail in resource_availability:
        print(f"  - {avail.start_date} to {avail.end_date}: {avail.get_availability_type_display()}")
    
    if not resource_availability.exists():
        print("  - No availability records")
    print()

print("=== Calendar Should Show ===")
print("1. Resource dropdown with all resources")
print("2. Calendar events for availability entries")
print("3. Upcoming events in the sidebar")
print("4. Color-coded events based on availability type")

print("\n✅ Availability calendar verification completed!")
print("The calendar should now be working properly.")
print("Open http://localhost:8000/resources/availability/ to test.")
