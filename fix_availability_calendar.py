#!/usr/bin/env python
"""
Fix availability calendar by connecting resources to users and creating test data
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

print("=== Fixing Availability Calendar ===")

# First, let's see what we have
users = User.objects.all()
resources = Resource.objects.all()

print(f"Users: {users.count()}")
print(f"Resources: {resources.count()}")

# Connect resources to users if they don't have users
resources_without_users = Resource.objects.filter(user__isnull=True)
print(f"Resources without users: {resources_without_users.count()}")

if resources_without_users.exists() and users.exists():
    print("\nConnecting resources to users...")
    
    # Get available users (those without resources)
    users_without_resources = User.objects.filter(resource__isnull=True)
    
    for i, resource in enumerate(resources_without_users):
        if i < users_without_resources.count():
            user = users_without_resources[i]
            resource.user = user
            resource.save()
            print(f"Connected {resource.name} to user {user.username}")
        else:
            # If we run out of users, create new ones
            username = f"user_{resource.name.lower().replace(' ', '_')}"
            first_name = resource.name.split()[0] if ' ' in resource.name else resource.name
            last_name = resource.name.split()[-1] if ' ' in resource.name and len(resource.name.split()) > 1 else "Doe"
            
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@example.com"
            )
            resource.user = user
            resource.save()
            print(f"Created user {username} and connected to {resource.name}")

# Now create some sample availability data
print("\n=== Creating Sample Availability Data ===")

resources_with_users = Resource.objects.filter(user__isnull=False)
if resources_with_users.exists():
    today = datetime.now().date()
    
    # Create availability for the first resource
    resource = resources_with_users.first()
    
    sample_availability = [
        {
            'start_date': today + timedelta(days=1),
            'end_date': today + timedelta(days=1),
            'availability_type': 'vacation',
            'hours_per_day': 0,
            'notes': 'Personal day off'
        },
        {
            'start_date': today + timedelta(days=3),
            'end_date': today + timedelta(days=5),
            'availability_type': 'vacation',
            'hours_per_day': 0,
            'notes': 'Long weekend vacation'
        },
        {
            'start_date': today + timedelta(days=7),
            'end_date': today + timedelta(days=7),
            'availability_type': 'training',
            'hours_per_day': 8,
            'notes': 'Team training session'
        },
        {
            'start_date': today + timedelta(days=10),
            'end_date': today + timedelta(days=12),
            'availability_type': 'available',
            'hours_per_day': 8,
            'notes': 'Fully available'
        }
    ]
    
    for entry in sample_availability:
        availability, created = ResourceAvailability.objects.get_or_create(
            resource=resource,
            start_date=entry['start_date'],
            end_date=entry['end_date'],
            defaults={
                'availability_type': entry['availability_type'],
                'hours_per_day': entry['hours_per_day'],
                'notes': entry['notes']
            }
        )
        
        if created:
            print(f"Created: {resource.name} - {entry['start_date']} to {entry['end_date']} - {entry['availability_type']}")
        else:
            print(f"Already exists: {resource.name} - {entry['start_date']} to {entry['end_date']} - {entry['availability_type']}")

    # Create some availability for other resources too
    if resources_with_users.count() > 1:
        second_resource = resources_with_users[1]
        
        availability, created = ResourceAvailability.objects.get_or_create(
            resource=second_resource,
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=2),
            defaults={
                'availability_type': 'sick_leave',
                'hours_per_day': 0,
                'notes': 'Sick day'
            }
        )
        
        if created:
            print(f"Created: {second_resource.name} - {availability.start_date} - {availability.availability_type}")

print("\n=== Summary ===")
total_availability = ResourceAvailability.objects.count()
print(f"Total availability records: {total_availability}")

resources_with_users = Resource.objects.filter(user__isnull=False)
print(f"Resources with users: {resources_with_users.count()}")

print("\nAvailability calendar should now work properly!")
print("You can test it by:")
print("1. Going to the Resources tab")
print("2. Clicking on 'Availability Calendar'")
print("3. Selecting a resource from the dropdown")
print("4. You should see the availability entries on the calendar")
