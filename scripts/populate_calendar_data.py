#!/usr/bin/env python
"""
Populate Availability Calendar with Comprehensive Test Data
This script adds realistic availability data for manual testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
from random import choice, randint

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource, ResourceAvailability
from django.utils import timezone

def populate_calendar_data():
    """Populate calendar with comprehensive test data"""
    print("🗂️ Populating Availability Calendar with Test Data")
    print("="*60)
    
    # Clear existing data for clean test
    print("🧹 Clearing existing availability data...")
    ResourceAvailability.objects.all().delete()
    print("✅ Existing data cleared")
    
    # Get all resources
    resources = Resource.objects.all()
    if not resources.exists():
        print("❌ No resources found. Please create resources first.")
        return
    
    print(f"👥 Found {resources.count()} resources to populate data for")
    
    # Define availability scenarios
    availability_scenarios = [
        # Recent past events (to show history)
        {'days_offset': -15, 'type': 'vacation', 'duration': 3, 'notes': 'Spring vacation'},
        {'days_offset': -10, 'type': 'sick_leave', 'duration': 1, 'notes': 'Flu recovery'},
        {'days_offset': -5, 'type': 'training', 'duration': 2, 'notes': 'Professional development course'},
        
        # Current/near future events (next 7 days)
        {'days_offset': 0, 'type': 'available', 'duration': 1, 'notes': 'Available for urgent tasks'},
        {'days_offset': 1, 'type': 'vacation', 'duration': 1, 'notes': 'Personal day'},
        {'days_offset': 3, 'type': 'meeting', 'duration': 1, 'notes': 'All-hands company meeting'},
        {'days_offset': 5, 'type': 'training', 'duration': 1, 'notes': 'Security training'},
        
        # Next 2 weeks
        {'days_offset': 8, 'type': 'vacation', 'duration': 5, 'notes': 'Summer vacation - Europe trip'},
        {'days_offset': 15, 'type': 'sick_leave', 'duration': 2, 'notes': 'Medical appointment + recovery'},
        {'days_offset': 18, 'type': 'training', 'duration': 3, 'notes': 'Advanced technical certification'},
        {'days_offset': 22, 'type': 'personal_leave', 'duration': 1, 'notes': 'Family event'},
        
        # Next month
        {'days_offset': 25, 'type': 'vacation', 'duration': 2, 'notes': 'Weekend getaway'},
        {'days_offset': 30, 'type': 'unavailable', 'duration': 1, 'notes': 'Equipment maintenance day'},
        {'days_offset': 35, 'type': 'meeting', 'duration': 1, 'notes': 'Quarterly review meetings'},
        {'days_offset': 40, 'type': 'training', 'duration': 2, 'notes': 'Leadership development workshop'},
        
        # Future planning (2-3 months ahead)
        {'days_offset': 50, 'type': 'vacation', 'duration': 7, 'notes': 'Annual summer break'},
        {'days_offset': 65, 'type': 'training', 'duration': 3, 'notes': 'Industry conference attendance'},
        {'days_offset': 80, 'type': 'vacation', 'duration': 3, 'notes': 'Back-to-school break'},
        {'days_offset': 90, 'type': 'personal_leave', 'duration': 2, 'notes': 'Moving to new apartment'},
    ]
    
    created_count = 0
    today = timezone.now().date()
    
    # Create availability entries for each resource
    for resource in resources:
        print(f"\n👤 Creating availability data for: {resource.name}")
        
        # Each resource gets different scenarios (not all)
        resource_scenarios = choice([
            availability_scenarios[:12],  # First 12 scenarios
            availability_scenarios[3:15], # Middle scenarios
            availability_scenarios[6:],   # Last scenarios
            availability_scenarios[::2],  # Every other scenario
        ])
        
        for scenario in resource_scenarios:
            start_date = today + timedelta(days=scenario['days_offset'])
            end_date = start_date + timedelta(days=scenario['duration'] - 1)
            
            # Add some randomness to make it more realistic
            if randint(1, 3) == 1:  # Skip some entries randomly for variety
                continue
                
            # Create the availability entry
            availability = ResourceAvailability.objects.create(
                resource=resource,
                start_date=start_date,
                end_date=end_date,
                availability_type=scenario['type'],
                notes=scenario['notes'],
                hours_per_day=8.0 if scenario['type'] == 'available' else 0.0
            )
            
            print(f"   ✅ {scenario['type'].title()}: {start_date} to {end_date}")
            created_count += 1
    
    # Add some additional random entries for more variety
    print(f"\n🎲 Adding additional random entries...")
    
    additional_scenarios = [
        {'type': 'vacation', 'notes': 'Last-minute vacation'},
        {'type': 'sick_leave', 'notes': 'Unexpected illness'},
        {'type': 'training', 'notes': 'Emergency training session'},
        {'type': 'meeting', 'notes': 'Client presentation'},
        {'type': 'personal_leave', 'notes': 'Personal matters'},
        {'type': 'available', 'notes': 'Available for project work'},
    ]
    
    for i in range(10):  # Add 10 random entries
        resource = choice(resources)
        scenario = choice(additional_scenarios)
        
        # Random date within next 60 days
        random_offset = randint(1, 60)
        start_date = today + timedelta(days=random_offset)
        duration = randint(1, 3)
        end_date = start_date + timedelta(days=duration - 1)
        
        # Check for conflicts (basic check)
        existing = ResourceAvailability.objects.filter(
            resource=resource,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()
        
        if not existing:
            availability = ResourceAvailability.objects.create(
                resource=resource,
                start_date=start_date,
                end_date=end_date,
                availability_type=scenario['type'],
                notes=scenario['notes'],
                hours_per_day=8.0 if scenario['type'] == 'available' else 0.0
            )
            print(f"   🎲 Random {scenario['type']}: {resource.name} ({start_date})")
            created_count += 1
    
    print(f"\n📊 Data Population Summary")
    print(f"✅ Total entries created: {created_count}")
    
    # Show statistics
    total_records = ResourceAvailability.objects.count()
    print(f"✅ Total availability records: {total_records}")
    
    # Show breakdown by type
    type_counts = {}
    for record in ResourceAvailability.objects.all():
        atype = record.availability_type
        type_counts[atype] = type_counts.get(atype, 0) + 1
    
    print(f"\n📈 Availability type breakdown:")
    for atype, count in sorted(type_counts.items()):
        percentage = (count / total_records) * 100
        print(f"   • {atype.replace('_', ' ').title()}: {count} records ({percentage:.1f}%)")
    
    # Show temporal distribution
    past_count = ResourceAvailability.objects.filter(end_date__lt=today).count()
    current_count = ResourceAvailability.objects.filter(
        start_date__lte=today, end_date__gte=today
    ).count()
    future_count = ResourceAvailability.objects.filter(start_date__gt=today).count()
    
    print(f"\n📅 Temporal distribution:")
    print(f"   • Past events: {past_count}")
    print(f"   • Current events: {current_count}")
    print(f"   • Future events: {future_count}")
    
    # Show upcoming events (next 30 days)
    upcoming = ResourceAvailability.objects.filter(
        start_date__gte=today,
        start_date__lte=today + timedelta(days=30)
    ).order_by('start_date')[:10]
    
    print(f"\n📋 Next 10 upcoming events:")
    for event in upcoming:
        print(f"   • {event.start_date}: {event.resource.name} - {event.availability_type.replace('_', ' ').title()}")
    
    # Show per-resource summary
    print(f"\n👥 Per-resource summary:")
    for resource in resources:
        resource_count = ResourceAvailability.objects.filter(resource=resource).count()
        print(f"   • {resource.name}: {resource_count} availability records")
    
    print(f"\n🎉 Calendar population complete!")
    print(f"📅 You can now manually check the calendar at: http://127.0.0.1:8000/resources/availability/")
    
    return created_count

def create_demo_scenarios():
    """Create specific demo scenarios for testing"""
    print(f"\n🎭 Creating Demo Scenarios for Manual Testing")
    print("="*50)
    
    today = timezone.now().date()
    resources = list(Resource.objects.all())
    
    if len(resources) < 2:
        print("❌ Need at least 2 resources for demo scenarios")
        return
    
    demo_scenarios = [
        {
            'name': 'Team Vacation Overlap',
            'description': 'Two team members on vacation same week',
            'entries': [
                {'resource': 0, 'offset': 7, 'duration': 5, 'type': 'vacation', 'notes': 'Beach vacation'},
                {'resource': 1, 'offset': 9, 'duration': 3, 'type': 'vacation', 'notes': 'City break'},
            ]
        },
        {
            'name': 'Training Week',
            'description': 'Multiple team members in training',
            'entries': [
                {'resource': 0, 'offset': 20, 'duration': 2, 'type': 'training', 'notes': 'React advanced workshop'},
                {'resource': 1, 'offset': 21, 'duration': 2, 'type': 'training', 'notes': 'Python certification'},
                {'resource': 2 if len(resources) > 2 else 0, 'offset': 22, 'duration': 1, 'type': 'training', 'notes': 'Security training'},
            ]
        },
        {
            'name': 'Sick Leave Coverage',
            'description': 'One person sick, others available',
            'entries': [
                {'resource': 0, 'offset': 2, 'duration': 3, 'type': 'sick_leave', 'notes': 'Flu recovery'},
                {'resource': 1, 'offset': 2, 'duration': 1, 'type': 'available', 'notes': 'Available for extra tasks'},
            ]
        },
        {
            'name': 'End of Month Pattern',
            'description': 'Mixed availability at month end',
            'entries': [
                {'resource': 0, 'offset': 28, 'duration': 1, 'type': 'meeting', 'notes': 'Monthly review'},
                {'resource': 1, 'offset': 29, 'duration': 2, 'type': 'personal_leave', 'notes': 'Personal time off'},
                {'resource': 2 if len(resources) > 2 else 0, 'offset': 30, 'duration': 1, 'type': 'available', 'notes': 'Available for month-end tasks'},
            ]
        }
    ]
    
    for scenario in demo_scenarios:
        print(f"\n🎬 Creating: {scenario['name']}")
        print(f"   📝 {scenario['description']}")
        
        for entry in scenario['entries']:
            if entry['resource'] < len(resources):
                resource = resources[entry['resource']]
                start_date = today + timedelta(days=entry['offset'])
                end_date = start_date + timedelta(days=entry['duration'] - 1)
                
                # Check for existing conflicts
                existing = ResourceAvailability.objects.filter(
                    resource=resource,
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).exists()
                
                if not existing:
                    ResourceAvailability.objects.create(
                        resource=resource,
                        start_date=start_date,
                        end_date=end_date,
                        availability_type=entry['type'],
                        notes=entry['notes'],
                        hours_per_day=8.0 if entry['type'] == 'available' else 0.0
                    )
                    print(f"   ✅ {resource.name}: {entry['type']} ({start_date})")
                else:
                    print(f"   ⚠️ Conflict detected for {resource.name} on {start_date}")

if __name__ == "__main__":
    try:
        # Populate main calendar data
        created_count = populate_calendar_data()
        
        # Create demo scenarios
        create_demo_scenarios()
        
        print(f"\n" + "="*60)
        print(f"🎉 CALENDAR DATA POPULATION COMPLETE!")
        print(f"="*60)
        print(f"📊 Total entries created: {created_count}")
        print(f"📅 Calendar URL: http://127.0.0.1:8000/resources/availability/")
        print(f"🔐 Login with: admin / admin123")
        print(f"\n📋 Manual Testing Checklist:")
        print(f"✅ View calendar in month view")
        print(f"✅ Switch to week and list views")
        print(f"✅ Filter by different resources")
        print(f"✅ Click on events to see details")
        print(f"✅ Check upcoming events sidebar")
        print(f"✅ Try adding new availability entry")
        print(f"✅ Verify color coding for different types")
        print(f"✅ Navigate between months")
        print(f"✅ Check responsive design on different screen sizes")
        
    except Exception as e:
        print(f"❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
