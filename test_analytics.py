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

print("=== TESTING ANALYTICS DASHBOARD ===")

try:
    response = client.get('/analytics/')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Analytics dashboard loaded successfully!")
        # Check if the response contains expected content
        content = response.content.decode('utf-8')
        if 'Analytics Dashboard' in content:
            print("✅ Dashboard title found")
        if 'Total Resources' in content:
            print("✅ Resource metrics section found")
        if 'Resource Demand Forecast' in content:
            print("✅ Forecast section found")
        if 'Top Skills in Demand' in content:
            print("✅ Skills section found")
    else:
        print(f"❌ Error: Status code {response.status_code}")
        
except Exception as e:
    print(f"❌ Error accessing analytics dashboard: {e}")
    import traceback
    traceback.print_exc()

print("=== TEST COMPLETE ===")
