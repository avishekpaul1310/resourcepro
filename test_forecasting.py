#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User

# Create a test client
client = Client()

# Get or create a user for testing
user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'testpass'})

# Log in the user
client.force_login(user)

print("=== TESTING FORECASTING PAGE ===")

try:
    # Test GET request to forecasting page
    response = client.get('/analytics/forecast/')
    print(f"GET /analytics/forecast/ - Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print("✅ Forecasting page loaded successfully!")
        
        # Check for key elements
        if 'Generate Forecast' in content:
            print("✅ Generate Forecast form found")
        if 'Forecast Period (Days)' in content:
            print("✅ Forecast controls found")
        if 'forecasts' in str(response.context):
            print("✅ Forecasts context variable found")
        
        # Check if we have forecasts data
        if response.context.get('forecasts'):
            forecasts_count = len(response.context['forecasts'])
            print(f"✅ Found {forecasts_count} forecasts in context")
        else:
            print("❌ No forecasts found in context")
    
    # Test GET request with parameters (simulate form submission)
    print("\n--- Testing form submission ---")
    response = client.get('/analytics/forecast/?forecast_days=30')
    print(f"GET /analytics/forecast/?forecast_days=30 - Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Form submission handled successfully!")
        if response.context.get('forecasts'):
            forecasts_count = len(response.context['forecasts'])
            print(f"✅ Found {forecasts_count} forecasts after form submission")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")
