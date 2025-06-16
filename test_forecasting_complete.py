#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from analytics.models import ResourceDemandForecast

print("=== COMPREHENSIVE FORECASTING TEST ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin', defaults={'password': 'admin123'})
user.set_password('admin123')
user.save()

# Log in
login_success = client.login(username='admin', password='admin123')
print(f"Login successful: {login_success}")

if login_success:
    print(f"Total forecasts in database: {ResourceDemandForecast.objects.count()}")
    
    # Test accessing the forecasting page
    print("\n--- Testing forecasting page ---")
    response = client.get('/analytics/forecast/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print("✅ Page loaded successfully")
        
        # Check for key content
        checks = [
            ('Generate Forecast button', 'Generate Forecast' in content),
            ('Forecast form', 'forecast_days' in content),
            ('Existing forecasts', 'No forecast data available' not in content),
            ('Forecast table', 'Resource Role' in content),
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
    
    # Test form submission
    print("\n--- Testing form submission ---")
    response = client.get('/analytics/forecast/?forecast_days=30')
    print(f"Form submission status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Form submission successful")
        content = response.content.decode('utf-8')
        
        # Look for forecast data in the response
        forecast_found = any([
            'UI/UX Designer' in content,
            'Junior Developer' in content,
            'Senior Developer' in content,
        ])
        
        if forecast_found:
            print("✅ Forecast data displayed in response")
        else:
            print("❌ No forecast data found in response")
    
    # Test with different parameters
    print("\n--- Testing different forecast periods ---")
    for days in [7, 14, 30, 60]:
        response = client.get(f'/analytics/forecast/?forecast_days={days}')
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {days} days forecast: {response.status_code}")

else:
    print("❌ Could not log in - authentication issue")

print("\n=== TEST COMPLETE ===")
