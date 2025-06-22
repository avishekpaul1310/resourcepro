#!/usr/bin/env python
"""
Script to populate resources with timezone and location data for testing remote worker features
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource

# Sample timezone data for testing
timezone_data = [
    {
        'name': 'John Doe',
        'timezone': 'US/Eastern',
        'location': 'New York, USA'
    },
    {
        'name': 'Jane Smith',
        'timezone': 'Europe/London',
        'location': 'London, UK'
    },
    {
        'name': 'Bob Johnson',
        'timezone': 'Asia/Tokyo',
        'location': 'Tokyo, Japan'
    },
    {
        'name': 'Alice Brown',
        'timezone': 'Australia/Sydney',
        'location': 'Sydney, Australia'
    },
    {
        'name': 'Mike Wilson',
        'timezone': 'US/Pacific',
        'location': 'San Francisco, USA'
    }
]

def update_resources_with_timezone_data():
    """Update existing resources with timezone and location data"""
    updated_count = 0
    
    for tz_data in timezone_data:
        try:
            resource = Resource.objects.get(name=tz_data['name'])
            resource.timezone = tz_data['timezone']
            resource.location = tz_data['location']
            resource.save()
            updated_count += 1
            print(f"✓ Updated {resource.name} with timezone {tz_data['timezone']} and location {tz_data['location']}")
        except Resource.DoesNotExist:
            print(f"✗ Resource '{tz_data['name']}' not found")
        except Exception as e:
            print(f"✗ Error updating {tz_data['name']}: {e}")
    
    return updated_count

if __name__ == "__main__":
    print("=== Remote Worker Features Test Setup ===")
    print("Updating resources with timezone and location data...")
    
    updated = update_resources_with_timezone_data()
    print(f"\n✓ Updated {updated} resources with timezone data")
    
    print("\n=== Testing Remote Worker Features ===")
    
    # Test timezone methods
    resources = Resource.objects.filter(timezone__isnull=False)
    print(f"Found {resources.count()} resources with timezone data:")
    
    for resource in resources:
        print(f"\n--- {resource.name} ---")
        print(f"Location: {resource.location}")
        print(f"Timezone: {resource.timezone}")
        print(f"Current local time: {resource.get_formatted_local_time()}")
        print(f"Is business hours: {resource.is_business_hours()}")
    
    # Test overlapping hours
    if resources.count() >= 2:
        print(f"\n=== Team Overlap Analysis ===")
        overlap_hours = Resource.get_team_overlap_hours(list(resources))
        if overlap_hours:
            print(f"Team has {len(overlap_hours)} overlapping work hours:")
            for hour in overlap_hours:
                print(f"  - {hour:02d}:00-{hour+1:02d}:00 UTC")
        else:
            print("No overlapping work hours found for the team")
    
    print("\n=== Setup Complete ===")
    print("You can now test the remote worker features:")
    print("1. Visit http://127.0.0.1:8000/resources/ to see resources with local times")
    print("2. Visit http://127.0.0.1:8000/allocation/ to see timezone overlap widget")
    print("3. Visit http://127.0.0.1:8000/resources/availability/ to see timezone-aware calendar")
    print("4. Edit resources to update timezone and location information")
