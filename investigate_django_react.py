#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Skill, Resource
from analytics.models import ResourceDemandForecast

print("=== INVESTIGATING DJANGO AND REACT SKILLS ===")

# Check Django skill
try:
    django_skill = Skill.objects.get(name='Django')
    print(f"Django skill found - ID: {django_skill.id}")
    
    # Check which resources have Django skill
    django_resources = Resource.objects.filter(skills=django_skill)
    print(f"Resources with Django skill: {[r.name for r in django_resources]}")
    
    if django_resources:
        django_roles = [r.role for r in django_resources]
        print(f"Roles with Django skill: {django_roles}")
    else:
        print("❌ NO RESOURCES have Django skill!")
        
except Skill.DoesNotExist:
    print("❌ Django skill not found")

print("\n" + "="*50)

# Check React skill
try:
    react_skill = Skill.objects.get(name='React')
    print(f"React skill found - ID: {react_skill.id}")
    
    # Check which resources have React skill
    react_resources = Resource.objects.filter(skills=react_skill)
    print(f"Resources with React skill: {[r.name for r in react_resources]}")
    
    if react_resources:
        react_roles = [r.role for r in react_resources]
        print(f"Roles with React skill: {react_roles}")
    else:
        print("❌ NO RESOURCES have React skill!")
        
except Skill.DoesNotExist:
    print("❌ React skill not found")

print("\n" + "="*50)

# Check all resources and their skills
print("ALL RESOURCES AND THEIR SKILLS:")
for resource in Resource.objects.all():
    skills = resource.skills.all()
    skill_names = [skill.name for skill in skills]
    print(f"- {resource.name} ({resource.role}): {skill_names}")

print("\n" + "="*50)

# Check all skills and which resources have them
print("ALL SKILLS AND THEIR RESOURCES:")
for skill in Skill.objects.all():
    resources = Resource.objects.filter(skills=skill)
    resource_names = [r.name for r in resources]
    print(f"- {skill.name}: {resource_names if resource_names else 'NO RESOURCES'}")

print("\n=== INVESTIGATION COMPLETE ===")
