#!/usr/bin/env python
"""
Check forecast generation requirements
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

from analytics.services import PredictiveAnalyticsService
from allocation.models import Assignment
from django.utils import timezone
from datetime import timedelta

def check_forecast_requirements():
    """Check why forecast generation might be failing"""
    
    print("=== Checking Forecast Generation Requirements ===")
    
    # Check historical assignment data
    assignments = Assignment.objects.all()
    print(f"Total assignments: {assignments.count()}")
    
    recent_assignments = Assignment.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=180)
    )
    print(f"Recent assignments (last 180 days): {recent_assignments.count()}")
    
    if recent_assignments.exists():
        print("Sample recent assignments:")
        for assignment in recent_assignments[:3]:
            print(f"  - {assignment.resource.name} -> {assignment.task.name} ({assignment.allocated_hours}h)")
    
    # Try forecast generation with debug
    print("\n=== Testing Forecast Generation ===")
    
    service = PredictiveAnalyticsService()
    
    # Test the internal method to see what data is available
    try:
        historical_data = service._get_historical_assignment_data()
        print(f"Historical data points: {len(historical_data)}")
        
        if len(historical_data) >= 10:
            print("✅ Sufficient historical data for forecasting")
            
            # Try to generate forecasts
            forecasts = service.generate_resource_demand_forecast(30)
            if forecasts:
                print(f"✅ Successfully generated {len(forecasts)} forecasts")
                for forecast in forecasts[:3]:
                    print(f"  - {forecast.resource_role}: {forecast.predicted_demand_hours}h")
            else:
                print("❌ Forecast generation returned None")
        else:
            print(f"❌ Insufficient historical data. Need at least 10 points, have {len(historical_data)}")
            
            # Let's create some test data
            print("\n=== Creating Test Assignment Data ===")
            from resources.models import Resource
            from projects.models import Task
            
            resources = Resource.objects.all()[:3]
            tasks = Task.objects.all()[:3]
            
            if resources.exists() and tasks.exists():
                for i, (resource, task) in enumerate(zip(resources, tasks)):
                    if not Assignment.objects.filter(resource=resource, task=task).exists():
                        assignment = Assignment.objects.create(
                            resource=resource,
                            task=task,
                            allocated_hours=20 + (i * 10)
                        )
                        print(f"Created test assignment: {assignment}")
                
                # Try again
                print("\nRetrying forecast generation...")
                forecasts = service.generate_resource_demand_forecast(30)
                if forecasts:
                    print(f"✅ Successfully generated {len(forecasts)} forecasts")
                else:
                    print("❌ Still unable to generate forecasts")
            
    except Exception as e:
        print(f"Error in forecast generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_forecast_requirements()
