#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from resources.models import Resource, ResourceAvailability
from accounts.models import User
from datetime import datetime, timedelta

print("=== Checking Availability Calendar Data ===")

# Check if we have any resources
resources = Resource.objects.all()
print(f"Total resources: {resources.count()}")
for resource in resources:
    print(f"- {resource.user.get_full_name()} (ID: {resource.id})")

# Check if we have any availability records
availability_records = ResourceAvailability.objects.all()
print(f"\nTotal availability records: {availability_records.count()}")

if availability_records.exists():
    print("\nAvailability records:")
    for record in availability_records:
        print(f"- Resource: {record.resource.user.get_full_name()}")
        print(f"  Date: {record.date}")
        print(f"  Type: {record.availability_type}")
        print(f"  Hours: {record.hours_available}")
        print("")
else:
    print("No availability records found.")
    
    # Let's create some sample data for testing
    print("\nCreating sample availability data...")
    
    if resources.exists():
        first_resource = resources.first()
        today = datetime.now().date()
        
        # Create some sample availability entries
        sample_entries = [
            {
                'resource': first_resource,
                'date': today + timedelta(days=1),
                'availability_type': 'vacation',
                'hours_available': 0,
                'notes': 'Annual leave'
            },
            {
                'resource': first_resource,
                'date': today + timedelta(days=3),
                'availability_type': 'sick_leave',
                'hours_available': 0,
                'notes': 'Sick day'
            },
            {
                'resource': first_resource,
                'date': today + timedelta(days=5),
                'availability_type': 'holiday',
                'hours_available': 0,
                'notes': 'Public holiday'
            },
            {
                'resource': first_resource,
                'date': today + timedelta(days=7),
                'availability_type': 'available',
                'hours_available': 8,
                'notes': 'Full day available'
            }
        ]
        
        for entry_data in sample_entries:
            availability, created = ResourceAvailability.objects.get_or_create(
                resource=entry_data['resource'],
                date=entry_data['date'],
                defaults={
                    'availability_type': entry_data['availability_type'],
                    'hours_available': entry_data['hours_available'],
                    'notes': entry_data['notes']
                }
            )
            if created:
                print(f"Created: {availability.resource.user.get_full_name()} - {availability.date} - {availability.availability_type}")
            else:
                print(f"Already exists: {availability.resource.user.get_full_name()} - {availability.date} - {availability.availability_type}")

print("\n=== Testing Calendar Event Generation ===")

# Test the calendar event generation logic
from datetime import datetime
import calendar

def test_calendar_events():
    # Get the current month and year for testing
    today = datetime.now()
    year = today.year
    month = today.month
    
    print(f"Testing calendar events for {calendar.month_name[month]} {year}")
    
    # Get availability data for the month
    availability_data = ResourceAvailability.objects.filter(
        date__year=year,
        date__month=month
    )
    
    print(f"Found {availability_data.count()} availability records for this month")
    
    # Convert to calendar events format
    calendar_events = []
    for availability in availability_data:
        event = {
            'id': availability.id,
            'title': f"{availability.resource.user.get_full_name()} - {availability.get_availability_type_display()}",
            'start': availability.date.isoformat(),
            'backgroundColor': {
                'vacation': '#ff6b6b',
                'sick_leave': '#feca57', 
                'holiday': '#48dbfb',
                'available': '#1dd1a1',
                'partial': '#ff9ff3'
            }.get(availability.availability_type, '#6c757d'),
            'borderColor': 'transparent'
        }
        calendar_events.append(event)
    
    print(f"Generated {len(calendar_events)} calendar events:")
    for event in calendar_events:
        print(f"- {event['title']} on {event['start']}")
    
    return calendar_events

test_calendar_events()

print("\n=== Checking Form and View Requirements ===")

# Check if ResourceAvailabilityForm exists and what fields it has
try:
    from resources.forms import ResourceAvailabilityForm
    print("ResourceAvailabilityForm found")
    
    # Try to create an instance to see the fields
    if resources.exists():
        form = ResourceAvailabilityForm(user=resources.first().user)
        print(f"Form fields: {list(form.fields.keys())}")
    
except ImportError as e:
    print(f"ResourceAvailabilityForm not found: {e}")
except Exception as e:
    print(f"Error with ResourceAvailabilityForm: {e}")

print("\n=== Check Complete ===")
