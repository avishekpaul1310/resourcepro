#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from resources.models import Skill, Resource
from analytics.models import ResourceDemandForecast

print("=== COMPREHENSIVE SKILL FILTERING TEST ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()

login_success = client.login(username='admin', password='admin123')
print(f"Login successful: {login_success}")

if login_success:
    print(f"Total forecasts in database: {ResourceDemandForecast.objects.count()}")
    
    # Test each skill
    print("\n=== TESTING ALL SKILLS ===")
    for skill in Skill.objects.all():
        print(f"\n--- Testing {skill.name} (ID: {skill.id}) ---")
        
        # Find resources with this skill
        resources_with_skill = Resource.objects.filter(skills=skill)
        roles_with_skill = [r.role for r in resources_with_skill]
        
        print(f"Resources with {skill.name}: {[r.name for r in resources_with_skill]}")
        print(f"Roles with {skill.name}: {roles_with_skill}")
        
        # Check if we have forecasts for these roles
        forecasts_for_roles = ResourceDemandForecast.objects.filter(resource_role__in=roles_with_skill)
        print(f"Forecasts available for these roles: {forecasts_for_roles.count()}")
        
        # Test the actual filtering
        response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={skill.id}')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            has_data = 'No forecast data available' not in content
            
            if has_data:
                print(f"✅ {skill.name}: Filter shows forecast data")
                
                # Check if correct roles are shown
                for role in roles_with_skill:
                    if role in content:
                        print(f"  ✅ Found {role} in results")
                    else:
                        print(f"  ❌ Missing {role} in results")
            else:
                if forecasts_for_roles.count() > 0:
                    print(f"❌ {skill.name}: Should have data but shows none")
                else:
                    print(f"⚠️  {skill.name}: No forecasts available for associated roles")
        else:
            print(f"❌ {skill.name}: Error {response.status_code}")
    
    # Test the original issue (SQL skill with 7 days)
    print("\n=== TESTING ORIGINAL ISSUE: SQL + 7 DAYS ===")
    sql_skill = Skill.objects.get(name='SQL')
    response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={sql_skill.id}')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'No forecast data available' not in content:
            print("✅ SUCCESS: SQL skill filter now works with 7 days!")
            
            # Count how many forecast rows are shown
            forecast_rows = content.count('<tr>') - 1  # Subtract header row
            print(f"✅ Showing {forecast_rows} forecast entries")
            
            # Check if both expected roles are present
            if 'UI/UX Designer' in content:
                print("✅ UI/UX Designer forecasts shown")
            if 'Senior Developer' in content:
                print("✅ Senior Developer forecasts shown")
        else:
            print("❌ FAILED: Still showing 'No forecast data available'")
    else:
        print(f"❌ FAILED: Error {response.status_code}")

print("\n=== TEST COMPLETE ===")
