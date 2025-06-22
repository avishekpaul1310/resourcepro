#!/usr/bin/env python
"""
Test script for the simplified AI recommendation system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

import requests
from dashboard.models import DynamicRisk, AIRecommendation
from dashboard.ai_services import enhanced_risk_service

def test_simplified_ai_system():
    """Test the new simplified AI recommendation system"""
    print("🎯 Testing Simplified AI Recommendation System")
    print("=" * 50)
    
    # Test 1: Check if we have any existing risks
    print("\n1. Checking existing risks...")
    risks = DynamicRisk.objects.all()
    print(f"   Found {risks.count()} risks in the database")
    
    if risks.exists():
        risk = risks.first()
        print(f"   Testing with risk: '{risk.title}'")
        
        # Test 2: Generate recommendations for a risk
        print("\n2. Testing recommendation generation...")
        try:
            result = enhanced_risk_service.generate_risk_recommendations(risk.id)
            
            if result.get('success'):
                recommendations = result.get('recommendations', [])
                print(f"   ✅ Successfully generated {len(recommendations)} recommendations")
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"      {i}. {rec.get('title', 'No title')}")
                    print(f"         Success Rate: {rec.get('success_probability', 0)}%")
                    print(f"         Effort: {rec.get('implementation_effort', 'Unknown')}")
                    print(f"         Timeline: {rec.get('timeframe', 'Unknown')}")
                    print()
            else:
                print(f"   ❌ Failed to generate recommendations: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error generating recommendations: {e}")
    
    # Test 3: Check stored recommendations
    print("\n3. Checking stored recommendations...")
    stored_recs = AIRecommendation.objects.all()
    print(f"   Found {stored_recs.count()} stored recommendations")
    
    if stored_recs.exists():
        for rec in stored_recs[:3]:  # Show first 3
            print(f"   - {rec.title} ({rec.success_probability:.0%} success)")
    
    # Test 4: Test the API endpoint
    print("\n4. Testing API endpoint...")
    try:
        if risks.exists():
            response = requests.get('http://127.0.0.1:8000/dashboard/', timeout=5)
            if response.status_code == 200:
                print("   ✅ Dashboard page loads successfully")
                
                # Check if the page contains the new button
                if 'Get AI Recommendations' in response.text:
                    print("   ✅ Found 'Get AI Recommendations' button on page")
                else:
                    print("   ⚠️ 'Get AI Recommendations' button not found on page")
            else:
                print(f"   ❌ Dashboard page failed to load: {response.status_code}")
        else:
            print("   ⚠️ No risks available to test API endpoint")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error testing API endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Simplified AI System Test Complete!")
    print("\nKey Changes:")
    print("✅ Removed complex 13-step intervention simulator")
    print("✅ Added simple 1-click AI recommendations") 
    print("✅ Streamlined user experience")
    print("✅ Focused on actionable insights with success scores")
    print("\nHow it works now:")
    print("1. Dashboard shows key risks")
    print("2. Users click 'Get AI Recommendations' button")
    print("3. AI generates 2-3 recommendations with success percentages")
    print("4. Simple, clean modal shows results")

if __name__ == "__main__":
    test_simplified_ai_system()
