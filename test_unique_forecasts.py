#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from resources.models import Skill

print("=== TESTING FIXED SKILL-SPECIFIC FORECASTING ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()
client.login(username='admin', password='admin123')

# Test Python and Project Management skills
python_skill = Skill.objects.get(name='Python')
pm_skill = Skill.objects.get(name='Project Management')

print(f"Python skill ID: {python_skill.id}")
print(f"Project Management skill ID: {pm_skill.id}")

# Generate fresh forecasts for Python skill
print(f"\n--- Testing Python skill forecasting ---")
python_response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={python_skill.id}')

if python_response.status_code == 200:
    python_content = python_response.content.decode('utf-8')
    print("✅ Python forecast page loaded")
    
    # Extract forecast values
    import re
    python_values = re.findall(r'(\d+\.\d+)h', python_content)
    print(f"Python forecast values: {python_values[:5]}")  # First 5 values
    
    # Check if skill name appears in role names
    if '(Python)' in python_content:
        print("✅ Python skill identifier found in role names")
    else:
        print("❌ No Python skill identifier in role names")

# Generate fresh forecasts for Project Management skill  
print(f"\n--- Testing Project Management skill forecasting ---")
pm_response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={pm_skill.id}')

if pm_response.status_code == 200:
    pm_content = pm_response.content.decode('utf-8')
    print("✅ Project Management forecast page loaded")
    
    # Extract forecast values
    pm_values = re.findall(r'(\d+\.\d+)h', pm_content)
    print(f"Project Management forecast values: {pm_values[:5]}")  # First 5 values
    
    # Check if skill name appears in role names
    if '(Project Management)' in pm_content:
        print("✅ Project Management skill identifier found in role names")
    else:
        print("❌ No Project Management skill identifier in role names")

# Compare the results
print(f"\n--- Comparing Results ---")
if python_response.status_code == 200 and pm_response.status_code == 200:
    if python_values == pm_values:
        print("❌ BUG STILL EXISTS: Forecast values are identical!")
    else:
        print("✅ SUCCESS: Forecast values are now different!")
        print(f"Python first value: {python_values[0] if python_values else 'None'}")
        print(f"Project Management first value: {pm_values[0] if pm_values else 'None'}")

# Test a few more skills to ensure they're all different
print(f"\n--- Testing Multiple Skills for Uniqueness ---")
skills_to_test = ['SQL', 'JavaScript', 'HTML/CSS']
all_values = {}

for skill_name in skills_to_test:
    try:
        skill = Skill.objects.get(name=skill_name)
        response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={skill.id}')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            values = re.findall(r'(\d+\.\d+)h', content)
            all_values[skill_name] = values[:3]  # First 3 values
            print(f"✅ {skill_name}: {values[:3]}")
        else:
            print(f"❌ {skill_name}: Error {response.status_code}")
            
    except Skill.DoesNotExist:
        print(f"❌ {skill_name}: Skill not found")

# Check if all skills have unique forecasts
print(f"\n--- Uniqueness Check ---")
unique_values = set()
duplicates = []

for skill_name, values in all_values.items():
    values_tuple = tuple(values)
    if values_tuple in unique_values:
        duplicates.append(skill_name)
    else:
        unique_values.add(values_tuple)

if duplicates:
    print(f"❌ Duplicate forecasts found for: {duplicates}")
else:
    print("✅ All skills have unique forecasts!")

print("\n=== TEST COMPLETE ===")
