#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.services import PredictiveAnalyticsService, UtilizationTrackingService, CostTrackingService
from django.utils import timezone

print("=== POPULATING ANALYTICS DATA ===")

# Initialize services
analytics_service = PredictiveAnalyticsService()
utilization_service = UtilizationTrackingService()
cost_service = CostTrackingService()

# Record utilization for the past 30 days
print("Recording historical utilization data...")
for i in range(30):
    date = timezone.now().date() - timezone.timedelta(days=i)
    utilization_service.record_daily_utilization(date)

print("Generating resource demand forecasts...")
try:
    forecasts = analytics_service.generate_resource_demand_forecast(30)
    if forecasts:
        print(f"Generated {len(forecasts)} forecasts")
    else:
        print("No forecasts generated - insufficient data")
except Exception as e:
    print(f"Error generating forecasts: {e}")

print("Analyzing skill demand...")
try:
    analyses = analytics_service.analyze_skill_demand()
    print(f"Generated {len(analyses)} skill analyses")
except Exception as e:
    print(f"Error analyzing skills: {e}")

print("Updating project costs...")
try:
    cost_service.update_project_costs()
    print("Project costs updated")
except Exception as e:
    print(f"Error updating costs: {e}")

print("=== ANALYTICS DATA POPULATION COMPLETE ===")
