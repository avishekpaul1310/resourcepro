#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from resources.models import Skill

print("=== FINAL TEST: SQL SKILL FILTERING ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()

login_success = client.login(username='admin', password='admin123')

if login_success:
    sql_skill = Skill.objects.get(name='SQL')
    
    print(f"Testing SQL skill (ID: {sql_skill.id}) with 7 days forecast...")
    
    response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={sql_skill.id}')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if data is shown
        if 'No forecast data available' not in content:
            print("✅ SUCCESS: Forecast data is displayed!")
            
            # Check for both expected roles
            ui_designer_found = 'UI/UX Designer' in content
            senior_dev_found = 'Senior Developer' in content
            
            print(f"✅ UI/UX Designer shown: {ui_designer_found}")
            print(f"✅ Senior Developer shown: {senior_dev_found}")
            
            # Count forecast entries
            forecast_rows = content.count('<tr>') - 1  # Subtract header
            print(f"✅ Total forecast entries: {forecast_rows}")
            
            # Check dropdown selection
            selected_correctly = f'value="{sql_skill.id}" selected' in content
            print(f"✅ SQL selected in dropdown: {selected_correctly}")
            
        else:
            print("❌ FAILED: Still showing 'No forecast data available'")
    else:
        print(f"❌ FAILURE: HTTP {response.status_code}")

print("\n=== FINAL VERIFICATION COMPLETE ===")
