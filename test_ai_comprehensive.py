#!/usr/bin/env python
"""
Comprehensive AI Features Test Script
Tests all AI features step by step with detailed debugging
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from utils.gemini_ai import gemini_service
from analytics.ai_services import AISkillRecommendationService, AIResourceAllocationService, AIForecastEnhancementService
from resources.models import Resource, Skill
from projects.models import Task, Project
from allocation.models import Assignment
from analytics.models import AISkillRecommendation
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
        simple_response = gemini_service.generate_content("Say 'Hello World' in exactly those words.", temperature=0.1)
        print(f"Simple Test Response: {simple_response}")
        
        # Test JSON response
        json_prompt = """
        Generate a simple JSON object with this structure:
        {
            "test": "success",
            "message": "This is a test"
        }
        """
        json_response = gemini_service.generate_json_response(json_prompt, temperature=0.1)
        print(f"JSON Test Response: {json_response}")
        
        return json_response is not None
        
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
    print("\nSample Resources:")
    for resource in Resource.objects.all()[:3]:
        skills = [skill.name for skill in resource.skills.all()]
        print(f"  - {resource.name}: Skills = {skills}")
    
    print("\nSample Tasks:")
    for task in Task.objects.all()[:3]:
        required_skills = [skill.name for skill in task.skills_required.all()]
        print(f"  - {task.name}: Required Skills = {required_skills}")
    
    return (Resource.objects.count() > 0 and 
            Skill.objects.count() > 0 and 
            Task.objects.count() > 0)


def test_skill_recommendations_detailed():
    """Test skill recommendations with detailed debugging"""
    print("\n" + "=" * 60)
    print("TESTING SKILL RECOMMENDATIONS")
    print("=" * 60)
    
    try:
        # Clear old recommendations
        AISkillRecommendation.objects.filter(
            created_at__lt=timezone.now() - timedelta(hours=1)
        ).delete()
        
        service = AISkillRecommendationService()
        
        # Test data preparation
        print("Preparing team skills data...")
        team_skills = service._gather_team_skills_data()
        print(f"Team skills data: {len(team_skills)} entries")
        
        print("Preparing project requirements...")
        project_requirements = service._gather_project_requirements()
        print(f"Project requirements: {len(project_requirements)} projects")
        
        print("Preparing skill demand analysis...")
        skill_demand = service._gather_skill_demand_analysis()
        print(f"Skill demand: {len(skill_demand)} skills")
        
        # Test prompt creation
        print("Creating AI prompt...")
        prompt = service._create_skill_recommendation_prompt(
            team_skills, project_requirements, skill_demand
        )
        print(f"Prompt created, length: {len(prompt)} characters")
        print(f"Prompt preview: {prompt[:200]}...")
        
        # Test AI call
        print("Calling Gemini AI...")
        ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
        print(f"AI Response: {ai_response}")
        
        if ai_response:
            print("Processing AI response...")
            result = service._process_skill_recommendations(ai_response)
            print(f"Processed result: {result}")
            return True
        else:
            print("Failed to get AI response")
            return False
            
    except Exception as e:
        print(f"Skill recommendations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_allocation_detailed():
    """Test resource allocation with detailed debugging"""
    print("\n" + "=" * 60)
    print("TESTING RESOURCE ALLOCATION")
    print("=" * 60)
    
    try:
        # Find a suitable task
        task = Task.objects.filter(
            status__in=['not_started', 'in_progress']
        ).first()
        
        if not task:
            print("No suitable task found for allocation testing")
            return False
        
        print(f"Testing with task: {task.name}")
        
        service = AIResourceAllocationService()
        
        # Test data preparation
        print("Preparing task data...")
        task_data = service._prepare_task_data(task)
        print(f"Task data: {task_data}")
        
        print("Preparing resources data...")
        resources_data = service._prepare_resources_data()
        print(f"Resources data: {len(resources_data)} resources")
        
        # Test prompt creation
        print("Creating AI prompt...")
        prompt = service._create_allocation_prompt(task_data, resources_data)
        print(f"Prompt created, length: {len(prompt)} characters")
        print(f"Prompt preview: {prompt[:200]}...")
        
        # Test AI call
        print("Calling Gemini AI...")
        ai_response = gemini_service.generate_json_response(prompt, temperature=0.2)
        print(f"AI Response: {ai_response}")
        
        if ai_response:
            print("Processing AI response...")
            result = service._process_allocation_suggestions(task.id, ai_response)
            print(f"Processed result: {result}")
            return True
        else:
            print("Failed to get AI response")
            return False
            
    except Exception as e:
        print(f"Resource allocation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_forecasting_detailed():
    """Test forecasting with detailed debugging"""
    print("\n" + "=" * 60)
    print("TESTING ENHANCED FORECASTING")
    print("=" * 60)
    
    try:
        service = AIForecastEnhancementService()
        
        # Test forecast enhancement
        print("Testing forecast enhancement...")
        enhanced_forecasts = service.enhance_forecasts(
            days_ahead=30,
            business_context="Testing AI features implementation",
            force_refresh=True
        )
        
        print(f"Enhanced forecasts result: {enhanced_forecasts}")
        
        if 'error' not in enhanced_forecasts:
            print("Forecasting test successful!")
            return True
        else:
            print(f"Forecasting test failed: {enhanced_forecasts['error']}")
            return False
            
    except Exception as e:
        print(f"Forecasting test failed: {e}")
        import traceback
        traceback.print_exc()
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
        results['skill_recommendations'] = test_skill_recommendations_detailed()
        
        # Test 4: Resource Allocation
        results['resource_allocation'] = test_resource_allocation_detailed()
        
        # Test 5: Forecasting
        results['forecasting'] = test_forecasting_detailed()
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
    elif passed_tests > 0:
        print("⚠️  Some AI features need attention")
    else:
        print("🚨 AI features need debugging")


if __name__ == "__main__":
    main()
