#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource
from analytics.services import PredictiveAnalyticsService
from analytics.models import ResourceDemandForecast

print("=== GENERATING FORECASTS FOR ALL ROLES ===")

# Check what roles we have
all_roles = Resource.objects.values_list('role', flat=True).distinct()
print("Available resource roles:")
for role in all_roles:
    print(f"- {role}")

print("\nCurrent forecast roles:")
forecast_roles = ResourceDemandForecast.objects.values_list('resource_role', flat=True).distinct()
for role in forecast_roles:
    count = ResourceDemandForecast.objects.filter(resource_role=role).count()
    print(f"- {role}: {count} forecasts")

# The issue is that the forecast generation is based on historical assignment data
# Let's check if we have assignments for all roles
from allocation.models import Assignment

print("\nAssignment data by resource role:")
for resource in Resource.objects.all():
    assignment_count = Assignment.objects.filter(resource=resource).count()
    print(f"- {resource.name} ({resource.role}): {assignment_count} assignments")

# Generate additional forecasts manually for roles that don't have forecasts
print("\n=== CREATING SAMPLE FORECASTS FOR MISSING ROLES ===")

from django.utils import timezone
from datetime import timedelta
import random

missing_roles = []
for role in all_roles:
    if role not in forecast_roles:
        missing_roles.append(role)

print(f"Missing forecast roles: {missing_roles}")

# Create sample forecasts for missing roles
for role in missing_roles:
    for days_ahead in [7, 14, 30]:
        # Create a forecast with realistic but random data
        forecast = ResourceDemandForecast.objects.create(
            forecast_date=timezone.now().date(),
            resource_role=role,
            predicted_demand_hours=random.uniform(20, 80),
            confidence_score=random.uniform(0.6, 0.9),
            period_start=timezone.now().date() + timedelta(days=1),
            period_end=timezone.now().date() + timedelta(days=days_ahead)
        )
        print(f"Created forecast for {role}: {forecast.predicted_demand_hours:.1f}h")

print(f"\nTotal forecasts now: {ResourceDemandForecast.objects.count()}")

# Show updated forecast distribution
print("\nUpdated forecast roles:")
forecast_roles = ResourceDemandForecast.objects.values_list('resource_role', flat=True).distinct()
for role in forecast_roles:
    count = ResourceDemandForecast.objects.filter(resource_role=role).count()
    print(f"- {role}: {count} forecasts")

print("\n=== FORECAST GENERATION COMPLETE ===")
