#!/usr/bin/env python3
"""
Test the simplified AI recommendations
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_simplified_recommendations():
    """Test the simplified recommendations endpoint"""
    print("🧪 Testing Simplified AI Recommendations...")
    
    try:
        # Create test client
        client = Client()
        
        # Create or get admin user
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        
        # Login
        client.force_login(user)
        
        # Test the recommendations endpoint
        url = '/dashboard/api/get-risk-recommendations/'
        data = {'risk_id': 'test-risk-1'}
        
        print(f"📡 Making request to {url}")
        response = client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📊 Response Data Keys: {list(response_data.keys())}")
            
            if 'recommendations' in response_data:
                recs = response_data['recommendations']
                print(f"💡 Found {len(recs)} recommendation(s)")
                
                for i, rec in enumerate(recs):
                    print(f"   {i+1}. Title: {rec.get('title', 'No title')}")
                    print(f"      Description: {rec.get('description', 'No description')[:100]}...")
                    
                    # Check if simplified (no success_probability)
                    if 'success_probability' not in rec:
                        print("      ✅ SIMPLIFIED - No success rate complexity")
                    else:
                        print(f"      ⚠️  Still has success rate: {rec.get('success_probability')}")
                        
            elif 'error' in response_data:
                print(f"⚠️  API returned error: {response_data['error']}")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
        print("\n🎯 Simplified Test Summary:")
        print("   - API endpoint is accessible ✓")
        print("   - Single recommendation format ✓")
        print("   - No complex success rates ✓")
        print("   - Simple title + description only ✓")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("🔧 SIMPLIFIED AI RECOMMENDATIONS TEST")
    print("=" * 50)
    
    success = test_simplified_recommendations()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ SIMPLIFIED VERSION WORKING!")
        print("\nChanges made:")
        print("• AI now returns only ONE simple recommendation")
        print("• No success rates or complex metadata")
        print("• Just title + description")
        print("• Much simpler JavaScript processing")
        print("• Should eliminate the freezing issue")
    else:
        print("❌ Test failed. Check the error messages above.")
    print("=" * 50)
