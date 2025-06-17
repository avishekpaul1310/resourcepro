#!/usr/bin/env python
"""
Debug the skill recommendations AI feature
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from utils.gemini_ai import gemini_service
from analytics.ai_services import AISkillRecommendationService
from analytics.models import AISkillRecommendation
from django.utils import timezone
from datetime import timedelta

def debug_skill_recommendations():
    """Debug skill recommendations step by step"""
    print("=" * 60)
    print("DEBUGGING SKILL RECOMMENDATIONS")
    print("=" * 60)
    
    # Clear old recommendations first
    print("Clearing old recommendations...")
    AISkillRecommendation.objects.all().delete()
    
    service = AISkillRecommendationService()
    
    # Step 1: Test data gathering
    print("\n1. Testing data gathering...")
    try:
        team_skills = service._get_team_skills_data()
        print(f"✅ Team skills data: {len(team_skills.get('team_members', []))} members")
        print(f"Sample: {team_skills}")
    except Exception as e:
        print(f"❌ Team skills data failed: {e}")
        return False
    
    try:
        project_requirements = service._get_project_requirements_data()
        print(f"✅ Project requirements: {len(project_requirements.get('project_requirements', []))} projects")
        print(f"Sample: {project_requirements}")
    except Exception as e:
        print(f"❌ Project requirements failed: {e}")
        return False
    
    try:
        skill_demand = service._get_skill_demand_data()
        print(f"✅ Skill demand data: {len(skill_demand.get('skill_analysis', []))} skills")
        print(f"Sample: {skill_demand}")
    except Exception as e:
        print(f"❌ Skill demand data failed: {e}")
        return False
    
    # Step 2: Test prompt creation
    print("\n2. Testing prompt creation...")
    try:
        prompt = service._create_skill_recommendation_prompt(
            team_skills, project_requirements, skill_demand
        )
        print(f"✅ Prompt created: {len(prompt)} characters")
        print(f"Prompt preview:\n{prompt[:500]}...")
        print(f"Prompt ending:\n...{prompt[-200:]}")
    except Exception as e:
        print(f"❌ Prompt creation failed: {e}")
        return False
    
    # Step 3: Test AI call directly
    print("\n3. Testing direct AI call...")
    try:
        print("Calling Gemini AI...")
        ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
        print(f"AI response type: {type(ai_response)}")
        print(f"AI response: {ai_response}")
        
        if ai_response is None:
            print("❌ AI returned None - trying with generate_content instead...")
            text_response = gemini_service.generate_content(prompt, temperature=0.3)
            print(f"Text response: {text_response}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_ai_json():
    """Test AI with a simple JSON prompt"""
    print("\n" + "=" * 60)
    print("TESTING SIMPLE AI JSON")
    print("=" * 60)
    
    simple_prompt = """
Please generate a JSON response with the following structure:

{
    "skills_to_develop": [
        {
            "skill_name": "Advanced Python",
            "priority_score": 8,
            "reasoning": "Python is widely needed across projects",
            "confidence_score": 0.9,
            "estimated_impact": "High impact on team productivity"
        }
    ],
    "training_areas": [
        {
            "skill_name": "Machine Learning",
            "priority_score": 7,
            "reasoning": "Growing demand for ML skills",
            "confidence_score": 0.8,
            "estimated_impact": "Medium impact on future projects"
        }
    ],
    "obsolete_skills": []
}

Respond with valid JSON only."""
    
    try:
        response = gemini_service.generate_json_response(simple_prompt, temperature=0.1)
        print(f"Simple JSON test response: {response}")
        print(f"Response type: {type(response)}")
        return response is not None
    except Exception as e:
        print(f"Simple JSON test failed: {e}")
        return False

if __name__ == "__main__":
    # Test simple JSON first
    simple_works = test_simple_ai_json()
    
    if simple_works:
        print("\n✅ Simple JSON works, testing full skill recommendations...")
        debug_skill_recommendations()
    else:
        print("\n❌ Simple JSON failed, AI service has issues")
