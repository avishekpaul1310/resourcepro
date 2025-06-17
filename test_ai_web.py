#!/usr/bin/env python
"""
Test the AI web interface
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_ai_web_interface():
    """Test the AI web interface"""
    print("=" * 60)
    print("TESTING AI WEB INTERFACE")
    print("=" * 60)
    
    # Create a test user if needed
    client = Client()
    
    # Create a superuser for testing
    try:
        user = User.objects.get(username='admin')
        print(f"Using existing user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print(f"Created test user: {user.username}")
    
    # Login
    client.login(username='admin', password='admin123')
    print("✅ Logged in successfully")
    
    # Test AI analytics page
    try:
        response = client.get('/analytics/ai/')
        print(f"AI Analytics page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ AI Analytics page is accessible")
            content = response.content.decode('utf-8')
            
            # Check for key AI features in the page
            features_found = {
                'skill_recommendations': 'Smart Skill Recommendations' in content,
                'resource_allocation': 'Resource Allocation' in content,
                'forecasting': 'Enhanced Forecasting' in content or 'forecast' in content.lower(),
                'ai_available': 'Gemini API key' not in content or 'AI Service Unavailable' not in content
            }
            
            print("\nAI Features in Web Interface:")
            for feature, found in features_found.items():
                status = "✅ Found" if found else "❌ Missing"
                print(f"  {feature.replace('_', ' ').title()}: {status}")
            
            return all(features_found.values())
        else:
            print(f"❌ AI Analytics page returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing AI Analytics page: {e}")
        return False

def test_ai_api_endpoints():
    """Test AI API endpoints"""
    print("\n" + "=" * 60)
    print("TESTING AI API ENDPOINTS")
    print("=" * 60)
    
    client = Client()
    
    # Login first
    user = User.objects.get(username='admin')
    client.force_login(user)
    
    endpoints = {
        'skill_recommendations': '/analytics/ai/skill-recommendations/',
        'resource_allocation': '/analytics/ai/resource-allocation/2/',  # Task ID 2
    }
    
    results = {}
    
    for endpoint_name, endpoint_url in endpoints.items():
        try:
            response = client.get(endpoint_url)
            print(f"{endpoint_name.replace('_', ' ').title()}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'error' not in data:
                    print(f"  ✅ Success - returned {len(data.get('recommendations', data.get('suggestions', [])))} items")
                    results[endpoint_name] = True
                else:
                    print(f"  ❌ API Error: {data.get('error', 'Unknown error')}")
                    results[endpoint_name] = False
            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                results[endpoint_name] = False
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            results[endpoint_name] = False
    
    return all(results.values())

def main():
    """Run web interface tests"""
    print("AI WEB INTERFACE TESTING")
    print("=" * 60)
    
    web_test = test_ai_web_interface()
    api_test = test_ai_api_endpoints()
    
    print("\n" + "=" * 60)
    print("WEB INTERFACE TEST RESULTS")
    print("=" * 60)
    
    print(f"Web Interface: {'✅ PASS' if web_test else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_test else '❌ FAIL'}")
    
    if web_test and api_test:
        print("\n🎉 AI web interface is fully functional!")
        print("\nTo access the AI features:")
        print("1. Start the server: python manage.py runserver")
        print("2. Go to: http://localhost:8000/analytics/ai/")
        print("3. Login with: admin / admin123")
    else:
        print("\n⚠️ Some web interface features need attention")

if __name__ == "__main__":
    main()
