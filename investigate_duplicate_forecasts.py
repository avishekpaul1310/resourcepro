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

print("=== INVESTIGATING DUPLICATE FORECASTS ===")

# Get skills to compare
python_skill = Skill.objects.get(name='Python')
pm_skill = Skill.objects.get(name='Project Management')

print(f"Python skill ID: {python_skill.id}")
print(f"Project Management skill ID: {pm_skill.id}")

# Check which resources have each skill
print(f"\nResources with Python skill:")
python_resources = Resource.objects.filter(skills=python_skill)
for r in python_resources:
    print(f"  - {r.name} ({r.role})")

print(f"\nResources with Project Management skill:")
pm_resources = Resource.objects.filter(skills=pm_skill)
for r in pm_resources:
    print(f"  - {r.name} ({r.role})")

# Get the roles for each skill
python_roles = [r.role for r in python_resources]
pm_roles = [r.role for r in pm_resources]

print(f"\nPython skill roles: {python_roles}")
print(f"Project Management skill roles: {pm_roles}")

# Check overlap
overlapping_roles = set(python_roles) & set(pm_roles)
print(f"Overlapping roles: {list(overlapping_roles)}")

# Get forecasts for each role combination
print(f"\n=== FORECAST ANALYSIS ===")

print(f"\nForecasts for Python skill roles:")
python_forecasts = ResourceDemandForecast.objects.filter(
    resource_role__in=python_roles
).order_by('resource_role', '-forecast_date')[:10]

for f in python_forecasts:
    print(f"  {f.resource_role}: {f.predicted_demand_hours}h (confidence: {f.confidence_score}) - {f.forecast_date}")

print(f"\nForecasts for Project Management skill roles:")
pm_forecasts = ResourceDemandForecast.objects.filter(
    resource_role__in=pm_roles
).order_by('resource_role', '-forecast_date')[:10]

for f in pm_forecasts:
    print(f"  {f.resource_role}: {f.predicted_demand_hours}h (confidence: {f.confidence_score}) - {f.forecast_date}")

# Test actual filtering results
print(f"\n=== TESTING ACTUAL FILTER RESULTS ===")

client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()
client.login(username='admin', password='admin123')

# Get Python skill forecasts
python_response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={python_skill.id}')
pm_response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={pm_skill.id}')

if python_response.status_code == 200 and pm_response.status_code == 200:
    python_content = python_response.content.decode('utf-8')
    pm_content = pm_response.content.decode('utf-8')
    
    # Check if the HTML content is identical
    if python_content == pm_content:
        print("❌ BUG CONFIRMED: The HTML responses are identical!")
    else:
        print("✅ Different HTML responses (as expected)")
        
    # Extract forecast table data for comparison
    import re
    
    def extract_forecast_data(content):
        # Simple regex to find forecast values
        pattern = r'(\d+\.\d+)h'
        matches = re.findall(pattern, content)
        return matches
    
    python_values = extract_forecast_data(python_content)
    pm_values = extract_forecast_data(pm_content)
    
    print(f"\nPython forecast values: {python_values[:10]}")  # First 10 values
    print(f"Project Management forecast values: {pm_values[:10]}")  # First 10 values
    
    if python_values == pm_values:
        print("❌ BUG CONFIRMED: Forecast values are identical!")
        print("This suggests the filtering is not working correctly.")
    else:
        print("✅ Forecast values are different (as expected)")

print("\n=== INVESTIGATION COMPLETE ===")
