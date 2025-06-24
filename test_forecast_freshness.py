#!/usr/bin/env python
"""
Test the updated forecast functionality
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

def test_forecast_freshness():
    """Test the forecast freshness logic"""
    
    print("=== Testing Forecast Freshness Logic ===")
    
    # Get current forecasts
    all_forecasts = ResourceDemandForecast.objects.all().order_by('-forecast_date')
    
    print(f"Total forecasts in database: {all_forecasts.count()}")
    
    if all_forecasts.exists():
        print("\nForecast Analysis:")
        for forecast in all_forecasts[:5]:
            days_old = (timezone.now().date() - forecast.forecast_date).days
            is_stale = days_old > 3
            
            print(f"  {forecast.resource_role}:")
            print(f"    Date: {forecast.forecast_date}")
            print(f"    Age: {days_old} days")
            print(f"    Status: {'🔴 STALE' if is_stale else '🟢 FRESH'}")
    
    # Test the dashboard logic
    print("\n=== Dashboard Forecast Logic Test ===")
    
    forecast_threshold = timezone.now().date() - timedelta(days=3)
    recent_forecasts = ResourceDemandForecast.objects.filter(
        forecast_date__gte=forecast_threshold
    ).order_by('-forecast_date')[:5]
    
    print(f"Recent forecasts (within 3 days): {recent_forecasts.count()}")
    
    if recent_forecasts.exists():
        print("✅ Dashboard will show fresh forecasts")
    else:
        print("⚠️  Dashboard will trigger automatic forecast generation")
    
    # Show what the dashboard template will display
    print("\n=== Template Display Preview ===")
    
    # Simulate the forecast_data structure from the view
    forecast_data = []
    target_forecasts = recent_forecasts if recent_forecasts.exists() else all_forecasts.order_by('-forecast_date')[:5]
    
    for forecast in target_forecasts:
        days_old = (timezone.now().date() - forecast.forecast_date).days
        forecast_data.append({
            'forecast': forecast,
            'days_old': days_old,
            'is_stale': days_old > 3
        })
    
    for item in forecast_data:
        forecast = item['forecast']
        print(f"  {forecast.resource_role}: {forecast.predicted_demand_hours}h")
        print(f"    Date: {forecast.forecast_date} ({item['days_old']}d old)")
        print(f"    Display: {'⚠️ Highlighted as stale' if item['is_stale'] else '✅ Normal display'}")

if __name__ == "__main__":
    test_forecast_freshness()
