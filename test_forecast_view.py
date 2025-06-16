#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.models import ResourceDemandForecast
from analytics.views import generate_forecast
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.http import HttpRequest

print("=== TESTING FORECASTING VIEW DIRECTLY ===")

# Create a request factory
factory = RequestFactory()

# Create a user
user, created = User.objects.get_or_create(username='testuser')

# Create a GET request
request = factory.get('/analytics/forecast/')
request.user = user

print("Forecasts in database:", ResourceDemandForecast.objects.count())

try:
    response = generate_forecast(request)
    print(f"Response status: {response.status_code}")
    print("✅ View executed successfully!")
    
    # Check if it's a template response
    if hasattr(response, 'context_data'):
        print(f"Context data: {response.context_data}")
    
except Exception as e:
    print(f"❌ Error in view: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING GET WITH PARAMETERS ===")

# Test with forecast_days parameter
request = factory.get('/analytics/forecast/?forecast_days=30')
request.user = user

try:
    response = generate_forecast(request)
    print(f"Response status: {response.status_code}")
    print("✅ View with parameters executed successfully!")
    
except Exception as e:
    print(f"❌ Error in view with parameters: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")
