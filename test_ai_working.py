#!/usr/bin/env python
"""
Working AI Features Test Script
Tests all AI features using correct method names
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from utils.gemini_ai import gemini_service
from analytics.ai_services import AISkillRecommendationService, AIResourceAllocationService, AIForecastEnhancementService
from analytics.services import PredictiveAnalyticsService
from resources.models import Resource, Skill
from projects.models import Task, Project
from allocation.models import Assignment
from analytics.models import AISkillRecommendation, ResourceDemandForecast
from django.utils import timezone
from datetime import timedelta


def test_basic_ai_service():
    """Test basic AI service functionality"""
    print("=" * 60)
    print("TESTING BASIC AI SERVICE")
    print("=" * 60)
    
    print(f"AI Service Available: {gemini_service.is_available()}")
    
    # Test simple content generation
    try:
        simple_response = gemini_service.generate_content("Say 'Hello AI Test' in exactly those words.", temperature=0.1)
        print(f"Simple Test Response: {simple_response}")
        
        return simple_response is not None and "Hello AI Test" in simple_response
        
    except Exception as e:
        print(f"Basic AI test failed: {e}")
        return False


def test_data_availability():
    """Test if we have sufficient data for AI features"""
    print("\n" + "=" * 60)
    print("TESTING DATA AVAILABILITY")
    print("=" * 60)
    
    print(f"Resources: {Resource.objects.count()}")
    print(f"Skills: {Skill.objects.count()}")
    print(f"Projects: {Project.objects.count()}")
    print(f"Tasks: {Task.objects.count()}")
    print(f"Assignments: {Assignment.objects.count()}")
    
    # Show sample data
    print("\nSample Resources and Skills:")
    for resource in Resource.objects.all()[:3]:
        skills = [skill.name for skill in resource.skills.all()]
        print(f"  - {resource.name}: Skills = {skills}")
    
    print("\nSample Tasks and Required Skills:")
    tasks_with_skills = 0
    for task in Task.objects.all()[:5]:
        required_skills = [skill.name for skill in task.skills_required.all()]
        print(f"  - {task.name}: Required Skills = {required_skills}")
        if required_skills:
            tasks_with_skills += 1
    
    print(f"\nTasks with required skills: {tasks_with_skills}")
    
    return (Resource.objects.count() > 0 and 
            Skill.objects.count() > 0 and 
            Task.objects.count() > 0)


def test_skill_recommendations():
    """Test skill recommendations feature"""
    print("\n" + "=" * 60)
    print("TESTING SKILL RECOMMENDATIONS")
    print("=" * 60)
    
    try:
        service = AISkillRecommendationService()
        recommendations = service.generate_skill_recommendations(force_refresh=True)
        
        if 'error' in recommendations:
            print(f"❌ Error: {recommendations['error']}")
            return False
        
        print("✅ Skill recommendations generated successfully!")
        
        # Display results summary
        total_recommendations = 0
        for category, items in recommendations.items():
            if isinstance(items, list) and items:
                print(f"\n{category.replace('_', ' ').title()}: {len(items)} recommendations")
                total_recommendations += len(items)
                # Show first recommendation as example
                first_item = items[0]
                print(f"  Example: {first_item.get('skill_name', 'N/A')} (Priority: {first_item.get('priority_score', 'N/A')}/10)")
                print(f"  Reasoning: {first_item.get('reasoning', 'N/A')[:100]}...")
        
        print(f"\nTotal recommendations: {total_recommendations}")
        return total_recommendations > 0
        
    except Exception as e:
        print(f"❌ Skill recommendations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_allocation():
    """Test resource allocation feature"""
    print("\n" + "=" * 60)
    print("TESTING RESOURCE ALLOCATION")
    print("=" * 60)
    
    try:
        # Find a suitable task
        task = Task.objects.filter(
            status__in=['not_started', 'in_progress']
        ).first()
        
        if not task:
            print("❌ No suitable task found for allocation testing")
            return False
        
        print(f"Testing with task: {task.name}")
        
        service = AIResourceAllocationService()
        suggestions = service.suggest_optimal_resource_allocation(
            task_id=task.id, 
            force_refresh=True
        )
        
        if not suggestions or 'error' in suggestions:
            error_msg = suggestions.get('error', 'Unknown error') if suggestions else 'No response'
            print(f"❌ Error: {error_msg}")
            return False
        
        print("✅ Resource allocation suggestions generated successfully!")
        
        # Display results summary
        if 'suggestions' in suggestions and suggestions['suggestions']:
            print(f"\nTask: {suggestions['task']['name']}")
            print(f"Number of suggestions: {len(suggestions['suggestions'])}")
            
            for i, suggestion in enumerate(suggestions['suggestions'][:3], 1):
                print(f"\n  Suggestion {i}:")
                print(f"    Resource: {suggestion.get('resource_name', 'N/A')}")
                print(f"    Match Score: {suggestion.get('match_score', 'N/A')}")
                print(f"    Reasoning: {suggestion.get('reasoning', 'N/A')[:100]}...")
            
            return True
        else:
            print("❌ No suggestions returned")
            return False
            
    except Exception as e:
        print(f"❌ Resource allocation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_forecasting():
    """Test enhanced forecasting feature"""
    print("\n" + "=" * 60)
    print("TESTING ENHANCED FORECASTING")
    print("=" * 60)
    
    try:        # First, generate some statistical forecasts
        analytics_service = PredictiveAnalyticsService()
        print("Generating statistical forecasts...")
        forecast_result = analytics_service.generate_resource_demand_forecast(days_ahead=30, include_ai_enhancement=False)
        
        if not forecast_result:
            print("❌ No statistical forecasts available")
            return False
        
        # Extract the actual forecasts (could be dict or list)
        if isinstance(forecast_result, dict) and 'statistical_forecasts' in forecast_result:
            statistical_forecasts = forecast_result['statistical_forecasts']
        elif isinstance(forecast_result, list):
            statistical_forecasts = forecast_result
        else:
            print(f"❌ Unexpected forecast format: {type(forecast_result)}")
            return False
        
        print(f"✅ Generated {len(statistical_forecasts)} statistical forecasts")        # The statistical forecasts are already ResourceDemandForecast objects, so we can use them directly
        print(f"✅ Using {len(statistical_forecasts)} existing forecast objects for AI enhancement")
        
        # Now test AI enhancement
        ai_service = AIForecastEnhancementService()
        enhanced_forecasts = ai_service.enhance_resource_demand_forecast(
            statistical_forecasts=statistical_forecasts,
            business_context="Testing AI features for ResourcePro implementation"
        )
        
        if not enhanced_forecasts or 'error' in enhanced_forecasts:
            error_msg = enhanced_forecasts.get('error', 'Unknown error') if enhanced_forecasts else 'No response'
            print(f"❌ Forecasting enhancement failed: {error_msg}")
            return False
        
        print("✅ Forecast enhancement successful!")
        
        # Display results summary
        if 'enhanced_forecasts' in enhanced_forecasts:
            forecasts = enhanced_forecasts['enhanced_forecasts']
            print(f"Enhanced forecasts: {len(forecasts)}")
            
            for forecast in forecasts[:3]:
                print(f"  - Skill: {forecast.get('skill_name', 'N/A')}")
                print(f"    Adjusted Demand: {forecast.get('adjusted_demand', 'N/A')}")
                if 'ai_reasoning' in forecast:
                    print(f"    AI Reasoning: {forecast['ai_reasoning'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Forecasting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_web_interface():
    """Test if web interface is accessible"""
    print("\n" + "=" * 60)
    print("TESTING WEB INTERFACE ACCESS")
    print("=" * 60)
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        from django.urls import reverse
        
        # Create test client
        client = Client()
        
        # Try to access AI analytics page (might require login)
        try:
            response = client.get('/analytics/ai/')
            print(f"AI Analytics page status: {response.status_code}")
            if response.status_code == 200:
                print("✅ AI Analytics page is accessible")
                return True
            elif response.status_code == 302:
                print("⚠️  AI Analytics page requires login (redirected)")
                return True
            else:
                print(f"❌ AI Analytics page returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not access AI Analytics page: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("COMPREHENSIVE AI FEATURES TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Basic AI Service
    results['basic_ai'] = test_basic_ai_service()
    
    # Test 2: Data Availability
    results['data_availability'] = test_data_availability()
    
    # Only continue if basic tests pass
    if results['basic_ai'] and results['data_availability']:
        # Test 3: Skill Recommendations
        results['skill_recommendations'] = test_skill_recommendations()
        
        # Test 4: Resource Allocation
        results['resource_allocation'] = test_resource_allocation()
        
        # Test 5: Forecasting
        results['forecasting'] = test_forecasting()
        
        # Test 6: Web Interface
        results['web_interface'] = test_web_interface()
    else:
        print("\nSkipping detailed tests due to basic test failures")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All AI features are working correctly!")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/analytics/ai/ to use the web interface")
        print("2. Try the API endpoints documented in AI_FEATURES_README.md")
        print("3. Check the analytics dashboard for AI-powered insights")
    elif passed_tests > 0:
        print("⚠️  Some AI features are working, but others need attention")
    else:
        print("🚨 AI features need debugging")


if __name__ == "__main__":
    main()
