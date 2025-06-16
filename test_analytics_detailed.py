#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from analytics.models import ResourceDemandForecast, SkillDemandAnalysis, HistoricalUtilization

# Create a test client
client = Client()

# Get or create a user for testing
user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'testpass'})

# Log in the user
client.force_login(user)

print("=== DETAILED ANALYTICS DASHBOARD TEST ===")

print(f"Database content:")
print(f"- Resource Demand Forecasts: {ResourceDemandForecast.objects.count()}")
print(f"- Skill Demand Analyses: {SkillDemandAnalysis.objects.count()}")
print(f"- Historical Utilizations: {HistoricalUtilization.objects.count()}")

try:
    response = client.get('/analytics/')
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for data sections
        checks = [
            ('forecast_data', 'No forecast data available' not in content),
            ('skill_demand', 'No skill demand data available' not in content),
            ('utilization_data', 'No utilization data available' not in content),
        ]
        
        for check_name, has_data in checks:
            status = "✅ HAS DATA" if has_data else "❌ NO DATA"
            print(f"{check_name}: {status}")
            
        # Check for specific forecast data
        forecasts = ResourceDemandForecast.objects.all()[:3]
        print(f"\nSample forecasts ({len(forecasts)}):")
        for forecast in forecasts:
            print(f"- {forecast.resource_role}: {forecast.predicted_demand_hours}h (confidence: {forecast.confidence_score})")
            
        # Check for skill data
        skills = SkillDemandAnalysis.objects.all()[:3]
        print(f"\nSample skills ({len(skills)}):")
        for skill in skills:
            print(f"- {skill.skill_name}: demand score {skill.demand_score}")
            
    else:
        print(f"❌ Error: Status code {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DETAILED TEST COMPLETE ===")
