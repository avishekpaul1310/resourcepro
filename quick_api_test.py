#!/usr/bin/env python
"""
Quick API test to check if the endpoint is working
"""
import requests

BASE_URL = 'http://localhost:8000'
TOKEN = 'cf0fb1902fbf3af5da65359ea9a1e6d26d9b86f9'

print("Testing API endpoints...")

# Test 1: Check if server is responding
try:
    response = requests.get(f'{BASE_URL}/')
    print(f"✅ Server responding: {response.status_code}")
except Exception as e:
    print(f"❌ Server not responding: {e}")
    exit(1)

# Test 2: Check API documentation endpoint
try:
    response = requests.get(f'{BASE_URL}/api/docs/')
    print(f"✅ API docs accessible: {response.status_code}")
except Exception as e:
    print(f"❌ API docs not accessible: {e}")

# Test 3: Test authentication endpoint
try:
    headers = {'Authorization': f'Token {TOKEN}'}
    response = requests.get(f'{BASE_URL}/api/v1/users/me/', headers=headers)
    print(f"Authentication test: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Authenticated as: {data['username']}")
    else:
        print(f"❌ Authentication failed: {response.text}")
except Exception as e:
    print(f"❌ Authentication error: {e}")

# Test 4: Check URL patterns
print("\nChecking available URL patterns...")
try:
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
    django.setup()
    
    from django.urls import get_resolver
    resolver = get_resolver()
    
    print("Available API patterns:")
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'pattern') and 'api' in str(pattern.pattern):
            print(f"  - {pattern.pattern}")
    
except Exception as e:
    print(f"Could not check URL patterns: {e}")
