#!/usr/bin/env python
"""
Check the current state of resource demand forecasts
"""

import os
import django
import sys

# Add the project root to the Python path
project_root = r'c:\Users\Avishek Paul\resourcepro'
sys.path.append(project_root)
os.chdir(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.models import ResourceDemandForecast
from django.utils import timezone
from datetime import timedelta

def check_forecast_data():
    """Check current forecast data and its freshness"""
    
    print("=== Resource Demand Forecast Data Analysis ===")
    
    # Get all forecasts
    all_forecasts = ResourceDemandForecast.objects.all().order_by('-forecast_date')
    
    print(f"Total forecasts in database: {all_forecasts.count()}")
    
    if all_forecasts.exists():
        print(f"\nMost recent forecast date: {all_forecasts.first().forecast_date}")
        print(f"Oldest forecast date: {all_forecasts.last().forecast_date}")
        print(f"Today's date: {timezone.now().date()}")
        
        # Check what the dashboard is currently showing
        recent_forecasts = ResourceDemandForecast.objects.all()[:5]
        print(f"\nForecasts shown on dashboard (first 5):")
        for i, forecast in enumerate(recent_forecasts, 1):
            days_old = (timezone.now().date() - forecast.forecast_date).days
            print(f"  {i}. {forecast.forecast_date} - {forecast.resource_role} - {forecast.predicted_demand_hours}h - {days_old} days old")
        
        # Check for recent forecasts (last 3 days)
        recent_date_threshold = timezone.now().date() - timedelta(days=3)
        recent_count = ResourceDemandForecast.objects.filter(
            forecast_date__gte=recent_date_threshold
        ).count()
        
        print(f"\nForecasts from last 3 days: {recent_count}")
        
        # Check forecast periods
        print(f"\nForecast periods:")
        for forecast in recent_forecasts:
            period_start = forecast.period_start
            period_end = forecast.period_end
            days_to_start = (period_start - timezone.now().date()).days
            days_to_end = (period_end - timezone.now().date()).days
            
            print(f"  {forecast.resource_role}: {period_start} to {period_end}")
            print(f"    Period starts in {days_to_start} days, ends in {days_to_end} days")
        
        # Analysis
        if recent_count == 0:
            print("\n❌ ISSUE: No recent forecasts found (older than 3 days)")
            print("   Recommendation: Generate fresh forecasts")
        elif days_old > 7:
            print(f"\n⚠️  WARNING: Dashboard showing {days_old}-day-old forecasts")
            print("   Recommendation: Update dashboard to show recent forecasts only")
        else:
            print(f"\n✅ OK: Forecasts are reasonably recent ({days_old} days old)")
    
    else:
        print("\n❌ ISSUE: No forecasts found in database")
        print("   Recommendation: Generate initial forecasts")

if __name__ == "__main__":
    check_forecast_data()
