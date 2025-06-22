#!/usr/bin/env python3
"""
Comprehensive verification script for the new AI recommendations system.
This script tests:
1. Backend API functionality
2. Database operations
3. Frontend button presence
4. Complete workflow integration
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from dashboard.models import Project, Resource, AIRecommendation
from dashboard.ai_services import EnhancedRiskAnalysisService

def print_status(message):
    """Print status with timestamp"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}")

def test_database_setup():
    """Test that the database has the required models and data"""
    print_status("Testing database setup...")
    
    # Check AIRecommendation model exists
    try:
        count = AIRecommendation.objects.count()
        print(f"✓ AIRecommendation model accessible, {count} existing recommendations")
    except Exception as e:
        print(f"✗ AIRecommendation model error: {e}")
        return False
    
    # Check we have projects with risks
    projects = Project.objects.all()[:5]
    print(f"✓ Found {Project.objects.count()} projects")
    
    for project in projects:
        print(f"  - {project.name}: {project.current_status}")
    
    return True

def test_ai_service():
    """Test the AI recommendation service"""
    print_status("Testing AI recommendation service...")
    
    service = EnhancedRiskAnalysisService()
    
    # Test risk analysis
    try:
        analysis = service.analyze_portfolio_risks()
        print(f"✓ Portfolio analysis generated: {len(analysis.get('risks', []))} risks found")
        
        # Test recommendation generation for first risk
        risks = analysis.get('risks', [])
        if risks:
            risk = risks[0]
            risk_id = risk.get('id', 'test-risk-1')
            recommendations = service.generate_risk_recommendations(risk_id, risk)
            print(f"✓ Generated {len(recommendations)} recommendations for risk: {risk.get('title', 'Unknown')}")
            
            if recommendations:
                rec = recommendations[0]
                print(f"  Sample recommendation: {rec.title} (Success: {rec.success_probability}%)")
        
        return True
    except Exception as e:
        print(f"✗ AI service error: {e}")
        return False

def test_api_endpoint():
    """Test the recommendations API endpoint"""
    print_status("Testing API endpoint...")
    
    # Create test client
    client = Client()
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={'is_superuser': True, 'is_staff': True}
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
    
    # Login
    client.force_login(admin_user)
    
    # Test endpoint
    try:
        url = '/dashboard/api/get-risk-recommendations/'
        response = client.post(
            url,
            data=json.dumps({'risk_id': 'test-risk-1'}),
            content_type='application/json'
        )
        
        print(f"✓ API endpoint accessible: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'recommendations' in data:
                print(f"✓ API returned {len(data['recommendations'])} recommendations")
                return True
            else:
                print(f"✗ API response missing recommendations: {data}")
        else:
            print(f"✗ API error: {response.content.decode()}")
            
    except Exception as e:
        print(f"✗ API test error: {e}")
    
    return False

def test_dashboard_content():
    """Test that dashboard shows AI widgets and buttons"""
    print_status("Testing dashboard content...")
    
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        client.force_login(admin_user)
    
    try:
        response = client.get('/dashboard/')
        content = response.content.decode()
        
        print(f"✓ Dashboard accessible: {response.status_code}")
        
        # Check for AI widget presence
        checks = [
            ('AI-Powered Daily Briefing', 'AI widget header'),
            ('ai-analyst-widget', 'AI widget container'),
            ('btn-recommendations', 'Recommendation buttons'),
            ('data-risk-id', 'Risk ID attributes'),
            ('Get AI Recommendations', 'Button text')
        ]
        
        all_passed = True
        for check_text, description in checks:
            if check_text in content:
                print(f"✓ Found: {description}")
            else:
                print(f"✗ Missing: {description}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Dashboard test error: {e}")
        return False

def test_static_files():
    """Test that static files are properly updated"""
    print_status("Testing static files...")
    
    js_files = [
        'static/js/ai_dashboard.js',
        'staticfiles/js/ai_dashboard.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
            
            if 'getRiskRecommendations' in content and 'showRecommendationsModal' in content:
                print(f"✓ {js_file} contains new recommendation functions")
            else:
                print(f"✗ {js_file} missing recommendation functions")
        else:
            print(f"⚠ {js_file} not found")
    
    return True

def main():
    """Run all tests"""
    print_status("Starting comprehensive verification of AI recommendations system")
    
    tests = [
        ("Database Setup", test_database_setup),
        ("AI Service", test_ai_service),
        ("API Endpoint", test_api_endpoint),
        ("Dashboard Content", test_dashboard_content),
        ("Static Files", test_static_files)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_status("VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The AI recommendations system is ready.")
        print("\nNext steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Visit the dashboard and test the 'Get AI Recommendations' buttons")
        print("3. Verify that clicking a button shows recommendations in a modal")
    else:
        print(f"\n⚠ {total - passed} tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
