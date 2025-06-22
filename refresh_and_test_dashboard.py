#!/usr/bin/env python
"""
Refresh AI analysis and test the dashboard display
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

import requests
from dashboard.ai_services import dashboard_ai_service

def refresh_and_test():
    """Refresh AI analysis and test dashboard display"""
    print("🔄 Refreshing AI Analysis...")
    
    # Generate fresh AI analysis
    analysis = dashboard_ai_service.generate_daily_briefing(force_refresh=True)
    
    print("✅ AI Analysis refreshed")
    print(f"Summary: {analysis.get('summary', 'No summary')[:100]}...")
    
    risks = analysis.get('risks', [])
    print(f"Found {len(risks)} risks:")
    
    for risk in risks:
        risk_id = risk.get('id', risk.get('database_risk_id', 'No ID'))
        print(f"  - {risk.get('title', 'No title')} (ID: {risk_id})")
    
    # Test the dashboard page
    print("\n🌐 Testing Dashboard Page...")
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/', timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard loads successfully")
            
            # Check for AI features
            content = response.text.lower()
            if 'get ai recommendations' in content:
                print("✅ Found 'Get AI Recommendations' button")
            elif 'ai recommendations' in content:
                print("⚠️ Found AI recommendations text but not the exact button")
            elif 'ai' in content:
                print("⚠️ Found AI content but no recommendation button")
            else:
                print("❌ No AI content found")
                
            # Check for risk display
            if 'key risks' in content:
                print("✅ Found 'Key Risks' section")
            else:
                print("⚠️ No 'Key Risks' section found")
                
        else:
            print(f"❌ Dashboard failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
    
    print("\n💡 If the button still doesn't appear, the issue might be:")
    print("   1. Dashboard template not updated to use new JS")
    print("   2. AI analyst widget not loading properly")
    print("   3. Risk data not being passed correctly to frontend")

if __name__ == "__main__":
    refresh_and_test()
