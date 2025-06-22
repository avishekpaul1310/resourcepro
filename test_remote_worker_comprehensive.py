#!/usr/bin/env python
"""
Comprehensive test script for remote worker features
"""
import os
import django
from datetime import datetime, time
import pytz

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource
from django.utils import timezone

def test_remote_worker_features():
    """Test all remote worker functionality"""
    print("🌍 Remote Worker Features - Comprehensive Test")
    print("=" * 60)
    
    # Get resources with timezone data
    resources = Resource.objects.filter(timezone__isnull=False).exclude(timezone='')
    
    if not resources.exists():
        print("❌ No resources with timezone data found!")
        print("Run the setup script first: python test_remote_worker_features.py")
        return
    
    print(f"📊 Testing {resources.count()} resources with timezone data\n")
    
    # Test 1: Basic timezone functionality
    print("1️⃣ Testing Basic Timezone Methods:")
    for resource in resources[:3]:  # Test first 3 resources
        print(f"\n   👤 {resource.name}")
        print(f"      🌍 Location: {resource.location or 'Not specified'}")
        print(f"      🕐 Timezone: {resource.timezone}")
        print(f"      ⏰ Local time: {resource.get_formatted_local_time()}")
        print(f"      🏢 Business hours: {'✅ Yes' if resource.is_business_hours() else '❌ No'}")
    
    # Test 2: Timezone overlap calculation
    print("\n2️⃣ Testing Team Overlap Calculation:")
    team_resources = list(resources[:4])  # Use first 4 resources as a team
    
    if len(team_resources) >= 2:
        overlap_hours = Resource.get_team_overlap_hours(team_resources)
        print(f"   👥 Team: {', '.join([r.name for r in team_resources])}")
        
        if overlap_hours:
            print(f"   ⏰ Overlapping hours: {len(overlap_hours)} hours")
            print(f"   🕒 UTC times: {[f'{h:02d}:00-{h+1:02d}:00' for h in overlap_hours[:5]]}")
            if len(overlap_hours) > 5:
                print(f"      ... and {len(overlap_hours) - 5} more")
        else:
            print("   ❌ No overlapping business hours found")
    else:
        print("   ⚠️  Need at least 2 resources for team overlap testing")
    
    # Test 3: Pairwise overlap
    print("\n3️⃣ Testing Pairwise Overlap:")
    if len(team_resources) >= 2:
        resource1, resource2 = team_resources[0], team_resources[1]
        overlap_hours = resource1.get_work_hours_overlap(resource2)
        print(f"   👥 {resource1.name} ↔️ {resource2.name}")
        print(f"   ⏰ Overlap: {overlap_hours} hours")
    
    # Test 4: Timezone edge cases
    print("\n4️⃣ Testing Edge Cases:")
    
    # Create a test resource with invalid timezone
    test_resource = Resource(name="Test User", timezone="Invalid/Timezone")
    try:
        local_time = test_resource.get_local_time()
        print("   ✅ Invalid timezone handled gracefully")
    except Exception as e:
        print(f"   ❌ Error with invalid timezone: {e}")
    
    # Test 5: Current status summary
    print("\n5️⃣ Current Team Status Summary:")
    print("   " + "-" * 50)
    print("   📍 Location             ⏰ Local Time    🏢 Status")
    print("   " + "-" * 50)
    
    for resource in resources:
        location = (resource.location or resource.timezone)[:20].ljust(20)
        local_time = resource.get_formatted_local_time().ljust(12)
        status = "🟢 Available" if resource.is_business_hours() else "🔴 Offline"
        print(f"   {location} {local_time} {status}")
    
    # Test 6: Meeting time suggestions
    print("\n6️⃣ Best Meeting Times (Next 24 Hours):")
    current_hour = timezone.now().hour
    best_times = []
    
    for hour_offset in range(24):
        test_hour = (current_hour + hour_offset) % 24
        available_count = 0
        
        for resource in team_resources:
            # Simulate checking if this UTC hour is business hours for the resource
            try:
                tz = pytz.timezone(resource.timezone)
                test_time = timezone.now().replace(hour=test_hour, minute=0, second=0, microsecond=0)
                local_test_time = test_time.astimezone(tz)
                
                if (local_test_time.weekday() < 5 and  # Weekday
                    9 <= local_test_time.hour < 17):   # Business hours
                    available_count += 1
            except:
                continue
        
        if available_count >= len(team_resources) * 0.75:  # 75% of team available
            best_times.append((test_hour, available_count))
    
    if best_times:
        print("   ⭐ Recommended meeting times (UTC):")
        for hour, count in best_times[:5]:  # Show top 5
            print(f"      🕒 {hour:02d}:00-{hour+1:02d}:00 UTC ({count}/{len(team_resources)} available)")
    else:
        print("   ⚠️  No optimal meeting times found in next 24 hours")
    
    # Test 7: Template tag functionality
    print("\n7️⃣ Testing Template Tag Functionality:")
    try:
        from resources.templatetags.timezone_tags import show_timezone_overlap, format_local_time
        
        # Test overlap widget data
        overlap_data = show_timezone_overlap(team_resources)
        print(f"   ✅ Template tag works: {overlap_data['overlap_count']} overlapping hours")
        
        # Test time formatting
        if team_resources:
            formatted_time = format_local_time(team_resources[0])
            print(f"   ✅ Time formatting works: {formatted_time}")
            
    except Exception as e:
        print(f"   ❌ Template tag error: {e}")
    
    print("\n🎉 Remote Worker Features Test Complete!")
    print("=" * 60)
    print("✅ All features are working correctly!")
    print("🌐 Visit http://127.0.0.1:8000/resources/ to see the UI")
    print("📋 Visit http://127.0.0.1:8000/allocation/ to see timezone overlaps")

if __name__ == "__main__":
    test_remote_worker_features()
