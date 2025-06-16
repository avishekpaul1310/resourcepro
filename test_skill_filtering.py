#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from resources.models import Skill

print("=== TESTING FIXED SKILL FILTERING ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()

login_success = client.login(username='admin', password='admin123')
print(f"Login successful: {login_success}")

if login_success:
    # Get SQL skill ID
    try:
        sql_skill = Skill.objects.get(name='SQL')
        sql_skill_id = sql_skill.id
        print(f"SQL skill ID: {sql_skill_id}")
        
        # Test filtering by SQL skill
        print(f"\n--- Testing SQL skill filter ---")
        response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={sql_skill_id}')
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if forecasts are displayed
            if 'No forecast data available' in content:
                print("❌ Still showing 'No forecast data available'")
            else:
                print("✅ Forecast data is now displayed!")
                
                # Check for specific roles that should have SQL skill
                if 'UI/UX Designer' in content:
                    print("✅ Found UI/UX Designer forecasts (Alice Brown has SQL skill)")
                if 'Senior Developer' in content:
                    print("✅ Found Senior Developer forecasts (John Doe has SQL skill)")
                    
            # Check form values
            if f'value="{sql_skill_id}" selected' in content:
                print("✅ SQL skill properly selected in dropdown")
        
        # Test other skills
        print(f"\n--- Testing other skills ---")
        for skill in Skill.objects.all()[:3]:
            response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={skill.id}')
            status = "✅" if response.status_code == 200 else "❌"
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                has_data = 'No forecast data available' not in content
                data_status = "HAS DATA" if has_data else "NO DATA"
                print(f"{status} {skill.name} (ID: {skill.id}): {data_status}")
            else:
                print(f"{status} {skill.name} (ID: {skill.id}): ERROR {response.status_code}")
                
    except Skill.DoesNotExist:
        print("❌ SQL skill not found")

else:
    print("❌ Could not log in")

print("\n=== TEST COMPLETE ===")
