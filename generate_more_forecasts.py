#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.services import PredictiveAnalyticsService
from analytics.models import ResourceDemandForecast

print("=== GENERATING NEW FORECASTS ===")

analytics_service = PredictiveAnalyticsService()

# Generate forecasts for different periods
for days in [7, 14, 30, 60]:
    print(f"Generating forecasts for {days} days ahead...")
    try:
        forecasts = analytics_service.generate_resource_demand_forecast(days)
        if forecasts:
            print(f"  ✅ Generated {len(forecasts)} forecasts")
        else:
            print("  ❌ No forecasts generated")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\nTotal forecasts in database: {ResourceDemandForecast.objects.count()}")

# Show some sample forecasts
print("\nSample forecasts:")
for forecast in ResourceDemandForecast.objects.order_by('-forecast_date')[:5]:
    print(f"- {forecast.forecast_date}: {forecast.resource_role} - {forecast.predicted_demand_hours}h (confidence: {forecast.confidence_score})")

print("\n=== FORECAST GENERATION COMPLETE ===")
