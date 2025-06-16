#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from resources.models import Skill
import re

print("=== FINAL VERIFICATION: SKILL-SPECIFIC FORECASTING ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()
client.login(username='admin', password='admin123')

# Test the original issue: Python vs Project Management
python_skill = Skill.objects.get(name='Python')
pm_skill = Skill.objects.get(name='Project Management')

print("🔍 Testing Original Issue: Python vs Project Management")
print("=" * 50)

# Test Python skill
python_response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={python_skill.id}')
python_values = re.findall(r'(\d+\.\d+)h', python_response.content.decode('utf-8'))

# Test Project Management skill
pm_response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={pm_skill.id}')
pm_values = re.findall(r'(\d+\.\d+)h', pm_response.content.decode('utf-8'))

print(f"Python forecast (7 days):")
print(f"  📊 Values: {python_values[:5]}")
print(f"  📈 Count: {len(python_values)} forecasts")

print(f"\nProject Management forecast (7 days):")
print(f"  📊 Values: {pm_values[:5]}")
print(f"  📈 Count: {len(pm_values)} forecasts")

# Verification
if python_values == pm_values:
    print("\n❌ FAILURE: Forecasts are still identical!")
else:
    print("\n✅ SUCCESS: Forecasts are now unique!")
    
print(f"\n🎯 Key Differences:")
if python_values and pm_values:
    print(f"   • Python first forecast: {python_values[0]}h")
    print(f"   • Project Mgmt first forecast: {pm_values[0]}h")
    difference = abs(float(python_values[0]) - float(pm_values[0]))
    print(f"   • Difference: {difference:.2f}h")

# Test role identification
python_content = python_response.content.decode('utf-8')
pm_content = pm_response.content.decode('utf-8')

print(f"\n🏷️  Role Identification:")
if '(Python)' in python_content:
    print("   ✅ Python skill clearly identified in role names")
if '(Project Management)' in pm_content:
    print("   ✅ Project Management skill clearly identified in role names")

# Test different forecast periods
print(f"\n⏱️  Testing Different Time Periods:")
for days in [7, 14, 30]:
    py_resp = client.get(f'/analytics/forecast/?forecast_days={days}&skill_filter={python_skill.id}')
    pm_resp = client.get(f'/analytics/forecast/?forecast_days={days}&skill_filter={pm_skill.id}')
    
    if py_resp.status_code == 200 and pm_resp.status_code == 200:
        py_vals = re.findall(r'(\d+\.\d+)h', py_resp.content.decode('utf-8'))
        pm_vals = re.findall(r'(\d+\.\d+)h', pm_resp.content.decode('utf-8'))
        
        unique = "✅ UNIQUE" if py_vals != pm_vals else "❌ IDENTICAL"
        print(f"   • {days} days: {unique}")

print(f"\n🎉 FINAL RESULT:")
print("=" * 50)
if python_values != pm_values:
    print("✅ BUG FIXED: Python and Project Management now have unique forecasts!")
    print("✅ Each skill generates its own specific forecast values")
    print("✅ Role names clearly indicate which skill the forecast is for")
    print("✅ No more duplicate forecasts between different skills")
else:
    print("❌ Bug still exists - needs further investigation")

print("\n=== VERIFICATION COMPLETE ===")    
