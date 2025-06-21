#!/usr/bin/env python3
"""
Test the dashboard refresh functionality and timestamp display
"""
import os
import sys
import django
import requests
import time
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from dashboard.ai_services import DashboardAIService

def test_refresh_functionality():
    """Test that refresh functionality works correctly"""
    print("Testing Dashboard Refresh Functionality")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Create or get test user
    User = get_user_model()
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return False
    
    # Login
    client.force_login(user)
    
    # Test 1: Get dashboard page
    print("1. Testing dashboard page load...")
    response = client.get('/dashboard/')
    if response.status_code == 200:
        print("✅ Dashboard loads successfully")
    else:
        print(f"❌ Dashboard failed to load: {response.status_code}")
        return False
    
    # Test 2: Check AI analysis data
    print("2. Testing AI analysis data...")
    ai_service = DashboardAIService()
    ai_data = ai_service.generate_daily_briefing()
    
    if 'error' in ai_data:
        print(f"❌ AI analysis error: {ai_data['error']}")
        return False
    
    if 'created_at' in ai_data:
        print(f"✅ AI analysis has timestamp: {ai_data['created_at']}")
    else:
        print("❌ AI analysis missing timestamp")
        return False
    
    # Test 3: Test refresh API endpoint
    print("3. Testing refresh API endpoint...")
    response = client.post('/dashboard/api/refresh-ai-analysis/')
    
    if response.status_code == 200:
        print("✅ Refresh API works successfully")
        refresh_data = response.json()
        if 'created_at' in refresh_data:
            print(f"✅ Refresh returns timestamp: {refresh_data['created_at']}")
        else:
            print("❌ Refresh missing timestamp")
            return False
    else:
        print(f"❌ Refresh API failed: {response.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Dashboard refresh functionality is working.")
    print("\nTo test manually:")
    print("1. Open http://127.0.0.1:8000/dashboard/")
    print("2. Look for 'Updated: [timestamp]' at bottom right of AI widget")
    print("3. Click 'Refresh' button and verify timestamp updates")
    
    return True

if __name__ == "__main__":
    test_refresh_functionality()
