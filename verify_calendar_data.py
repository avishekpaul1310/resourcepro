#!/usr/bin/env python
"""
Quick verification of calendar data for manual testing
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource, ResourceAvailability
from django.utils import timezone

def verify_calendar_data():
    """Quick verification of calendar data"""
    print("📊 CALENDAR DATA VERIFICATION")
    print("="*50)
    
    today = timezone.now().date()
    
    # Total records
    total = ResourceAvailability.objects.count()
    print(f"✅ Total availability records: {total}")
    
    # Show current week events
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    current_week = ResourceAvailability.objects.filter(
        start_date__lte=week_end,
        end_date__gte=week_start
    ).order_by('start_date')
    
    print(f"\n📅 Current Week Events ({week_start} to {week_end}):")
    for event in current_week:
        print(f"   • {event.start_date}: {event.resource.name} - {event.availability_type.title()}")
    
    # Show next week events
    next_week_start = week_end + timedelta(days=1)
    next_week_end = next_week_start + timedelta(days=6)
    
    next_week = ResourceAvailability.objects.filter(
        start_date__lte=next_week_end,
        end_date__gte=next_week_start
    ).order_by('start_date')
    
    print(f"\n📅 Next Week Events ({next_week_start} to {next_week_end}):")
    for event in next_week:
        print(f"   • {event.start_date}: {event.resource.name} - {event.availability_type.title()}")
    
    # Show resource summary
    print(f"\n👥 Resource Summary:")
    for resource in Resource.objects.all():
        count = ResourceAvailability.objects.filter(resource=resource).count()
        upcoming = ResourceAvailability.objects.filter(
            resource=resource,
            start_date__gte=today
        ).count()
        print(f"   • {resource.name}: {count} total, {upcoming} upcoming")
    
    # Show type breakdown
    print(f"\n🏷️ Availability Types:")
    type_counts = {}
    for record in ResourceAvailability.objects.all():
        atype = record.availability_type
        type_counts[atype] = type_counts.get(atype, 0) + 1
    
    for atype, count in sorted(type_counts.items()):
        print(f"   • {atype.replace('_', ' ').title()}: {count}")
    
    print(f"\n🎯 Ready for manual testing!")
    print(f"📅 Visit: http://127.0.0.1:8000/resources/availability/")
    print(f"🔐 Login: admin / admin123")

if __name__ == "__main__":
    verify_calendar_data()
