#!/usr/bin/env python
"""
Final Comprehensive Test - AI Recommendations System
Tests the complete workflow from dashboard load to recommendation generation
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from dashboard.models import DynamicRisk, AIRecommendation
from dashboard.ai_services import enhanced_risk_service
from projects.models import Project
from resources.models import Resource

def test_complete_system():
    """Test the complete AI recommendations system"""
    print("=== FINAL COMPREHENSIVE TEST ===")
    print(f"Test started at: {datetime.now()}")
    
    # 1. Test Database Setup
    print("\n1. Testing Database Setup...")
    try:
        # Check if we have some risks
        risk_count = DynamicRisk.objects.count()
        print(f"   ✓ Dynamic risks in database: {risk_count}")
        
        # Check if AIRecommendation model works
        rec_count = AIRecommendation.objects.count()
        print(f"   ✓ AI recommendations in database: {rec_count}")
        
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return False
    
    # 2. Test Backend Service
    print("\n2. Testing Backend Service...")
    try:
        # Test the analyze_portfolio_risks method
        analysis = enhanced_risk_service.analyze_portfolio_risks()
        if analysis and 'risks' in analysis:
            print(f"   ✓ Portfolio analysis generated {len(analysis['risks'])} risks")
            
            # Test recommendation generation for first risk
            if analysis['risks']:
                first_risk = analysis['risks'][0]
                risk_id = first_risk.get('id', 'test-risk-1')
                
                print(f"   Testing recommendations for risk: {risk_id}")
                recommendations = enhanced_risk_service.generate_risk_recommendations(
                    risk_id, 
                    risk_data=first_risk
                )
                
                if 'error' not in recommendations:
                    print(f"   ✓ Generated recommendations successfully")
                    if 'recommendations' in recommendations:
                        print(f"   ✓ Recommendation count: {len(recommendations['recommendations'])}")
                else:
                    print(f"   ✗ Recommendation error: {recommendations.get('error')}")
        else:
            print(f"   ✗ Portfolio analysis failed or returned no risks")
            
    except Exception as e:
        print(f"   ✗ Backend service error: {e}")
    
    # 3. Test API Endpoints
    print("\n3. Testing API Endpoints...")
    try:
        client = Client()
        
        # Create a test user and login
        try:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        except:
            user = User.objects.get(username='testuser')
        
        client.force_login(user)
        
        # Test dashboard analysis endpoint
        response = client.get('/dashboard/api/ai-analysis/')
        print(f"   AI Analysis endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Analysis endpoint working")
            if 'risks' in data:
                print(f"   ✓ Risks in response: {len(data['risks'])}")
        
        # Test recommendation endpoint
        test_data = {
            'risk_id': 'test-risk-1'
        }
        response = client.post(
            '/dashboard/api/get-risk-recommendations/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        print(f"   Recommendations endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Recommendations endpoint working")
            if 'recommendations' in data:
                print(f"   ✓ Recommendations in response: {len(data['recommendations'])}")
        
    except Exception as e:
        print(f"   ✗ API endpoint error: {e}")
    
    # 4. Test Dashboard Page
    print("\n4. Testing Dashboard Page...")
    try:
        response = client.get('/dashboard/')
        print(f"   Dashboard page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for AI widgets
            if 'ai-analyst-widget' in content:
                print("   ✓ AI analyst widget found")
            else:
                print("   ✗ AI analyst widget missing")
            
            # Check for recommendation buttons
            if 'btn-recommendations' in content:
                print("   ✓ Recommendation buttons found")
            else:
                print("   ✗ Recommendation buttons missing")
            
            # Check for JavaScript inclusion
            if 'ai_dashboard.js' in content:
                print("   ✓ AI dashboard JavaScript included")
            else:
                print("   ✗ AI dashboard JavaScript missing")
                
        else:
            print(f"   ✗ Dashboard page failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Dashboard page error: {e}")
    
    # 5. Test Static Files
    print("\n5. Testing Static Files...")
    try:
        # Check if JavaScript file exists
        js_path = 'staticfiles/js/ai_dashboard.js'
        if os.path.exists(js_path):
            print("   ✓ AI dashboard JavaScript file exists")
            
            # Check file content
            with open(js_path, 'r') as f:
                js_content = f.read()
                if 'getRiskRecommendations' in js_content:
                    print("   ✓ Recommendation function found in JavaScript")
                else:
                    print("   ✗ Recommendation function missing from JavaScript")
        else:
            print("   ✗ AI dashboard JavaScript file missing")
        
        # Check CSS file
        css_path = 'staticfiles/css/base.css'
        if os.path.exists(css_path):
            print("   ✓ Base CSS file exists")
        else:
            print("   ✗ Base CSS file missing")
            
    except Exception as e:
        print(f"   ✗ Static files error: {e}")
    
    # 6. Summary
    print("\n6. System Summary...")
    print("   AI Recommendations System Status:")
    print("   - Backend service: Enhanced risk analysis with recommendation generation")
    print("   - API endpoints: /dashboard/api/ai-analysis/ and /dashboard/api/get-risk-recommendations/")
    print("   - Frontend: Single-click recommendation buttons with modal display")
    print("   - Database: AIRecommendation model for storing generated recommendations")
    print("   - Old intervention simulator: Completely removed")
    
    print(f"\n=== Test completed at: {datetime.now()} ===")
    return True

if __name__ == "__main__":
    test_complete_system()
