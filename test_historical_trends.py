#!/usr/bin/env python
"""
Test the updated historical trend display
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

from resources.models import Resource
from analytics.models import HistoricalUtilization
from django.utils import timezone
from datetime import timedelta

def test_historical_trend_data():
    """Test the new historical trend calculation"""
    
    print("=== Testing Historical Trend Data ===")
    
    # This mimics the exact logic from analytics/views.py
    for resource in Resource.objects.all()[:5]:  # Test first 5 resources
        # Current utilization
        current_util = resource.current_utilization()
        
        # Historical average (past 30 days)
        historical_avg = HistoricalUtilization.objects.filter(
            resource=resource,
            date__gte=timezone.now().date() - timedelta(days=30)
        ).aggregate(avg=django.db.models.Avg('utilization_percentage'))['avg'] or 0
        
        # Trend change
        if historical_avg > 0:
            trend_change = current_util - float(historical_avg)
        else:
            trend_change = 0
        
        # Display results
        print(f"\n{resource.name}:")
        print(f"  Current Utilization: {current_util:.1f}%")
        print(f"  30-Day Average: {float(historical_avg):.1f}%")
        print(f"  Trend Change: {trend_change:+.1f}%")
        
        # Determine trend direction
        if trend_change > 0:
            trend_symbol = "↗ (increasing)"
        elif trend_change < 0:
            trend_symbol = "↘ (decreasing)"
        else:
            trend_symbol = "→ (stable)"
        
        print(f"  Trend Direction: {trend_symbol}")
    
    print("\n✅ Analytics Dashboard Now Shows:")
    print("  - Current Utilization: Real-time utilization based on active assignments")
    print("  - 30-Day Average: Historical average utilization over past 30 days")  
    print("  - Trend Change: Difference between current and historical (+ means increasing)")
    print("  - Clear trend indicators: ↗ (up), ↘ (down), → (stable)")

if __name__ == "__main__":
    test_historical_trend_data()
