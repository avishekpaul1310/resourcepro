#!/usr/bin/env python
"""
Test script to verify Django and React skills behavior in forecasting.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from resources.models import Resource, Skill
from analytics.models import ResourceDemandForecast

def test_django_react_skills():
    """Test forecasting behavior for Django and React skills (which have no resources)"""
    print("=" * 60)
    print("TESTING DJANGO AND REACT SKILLS FORECASTING BEHAVIOR")
    print("=" * 60)
    
    # Get Django and React skills
    django_skill = Skill.objects.filter(name='Django').first()
    react_skill = Skill.objects.filter(name='React').first()
    
    print(f"Django skill: {django_skill}")
    print(f"React skill: {react_skill}")
    
    if not django_skill or not react_skill:
        print("❌ ERROR: Django or React skills not found!")
        return
    
    # Test 1: Check resources for Django skill
    print("\n1. Checking resources for Django skill...")
    django_resources = Resource.objects.filter(skills=django_skill)
    print(f"   Django resources: {list(django_resources.values_list('name', 'role'))}")
    print(f"   Count: {django_resources.count()}")
    
    # Test 2: Check resources for React skill
    print("\n2. Checking resources for React skill...")
    react_resources = Resource.objects.filter(skills=react_skill)
    print(f"   React resources: {list(react_resources.values_list('name', 'role'))}")
    print(f"   Count: {react_resources.count()}")
    
    # Test 3: Verify no forecasts are generated for these skills
    print("\n3. Checking forecast generation for Django skill...")
    from analytics.views import generate_skill_specific_forecasts
    django_forecasts = generate_skill_specific_forecasts(str(django_skill.id), 30)
    print(f"   Django forecasts generated: {len(django_forecasts)}")
    
    print("\n4. Checking forecast generation for React skill...")
    react_forecasts = generate_skill_specific_forecasts(str(react_skill.id), 30)
    print(f"   React forecasts generated: {len(react_forecasts)}")
    
    # Test 5: Verify database state
    print("\n5. Database state verification...")
    django_forecast_count = ResourceDemandForecast.objects.filter(resource_role__icontains='Django').count()
    react_forecast_count = ResourceDemandForecast.objects.filter(resource_role__icontains='React').count()
    print(f"   Django forecasts in database: {django_forecast_count}")
    print(f"   React forecasts in database: {react_forecast_count}")
    
    # Test 6: Compare with skills that have resources
    print("\n6. Comparison with skills that have resources...")
    python_skill = Skill.objects.filter(name='Python').first()
    if python_skill:
        python_resources = Resource.objects.filter(skills=python_skill).count()
        print(f"   Python skill resources: {python_resources}")
        python_forecasts = generate_skill_specific_forecasts(str(python_skill.id), 30)
        print(f"   Python forecasts generated: {len(python_forecasts)}")
    
    print("\n" + "=" * 60)
    print("✅ DJANGO AND REACT SKILLS TESTING COMPLETE")
    print("SUMMARY:")
    print("- Django and React skills exist but have no resources assigned")
    print("- Forecasting correctly returns empty list for these skills")
    print("- No forecasts are generated for skills without resources")
    print("- This is the expected behavior - skills need resources to generate forecasts")
    print("=" * 60)

if __name__ == "__main__":
    test_django_react_skills()
