#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Skill, Resource
from analytics.models import ResourceDemandForecast

print("=== INVESTIGATING SKILL FILTERING ISSUE ===")

print("Available Skills:")
for skill in Skill.objects.all():
    print(f"- ID: {skill.id}, Name: {skill.name}")

print("\nResource Roles in Forecasts:")
roles = ResourceDemandForecast.objects.values_list('resource_role', flat=True).distinct()
for role in roles:
    print(f"- {role}")

print("\nResource Roles and Their Skills:")
for resource in Resource.objects.all():
    skills = resource.skills.all()
    skill_names = [skill.name for skill in skills]
    print(f"- {resource.name} ({resource.role}): {skill_names}")

print("\nForecast Count by Resource Role:")
for role in roles:
    count = ResourceDemandForecast.objects.filter(resource_role=role).count()
    print(f"- {role}: {count} forecasts")

# Test current filtering logic
print("\n=== TESTING CURRENT FILTER LOGIC ===")
test_skill_filter = "SQL"
print(f"Testing filter for skill: {test_skill_filter}")

# Current logic: filter by resource_role containing the skill name
filtered_forecasts = ResourceDemandForecast.objects.filter(resource_role__icontains=test_skill_filter)
print(f"Forecasts with resource_role containing '{test_skill_filter}': {filtered_forecasts.count()}")

# Better logic: filter by resources that have this skill
try:
    sql_skill = Skill.objects.get(name=test_skill_filter)
    resources_with_skill = Resource.objects.filter(skills=sql_skill)
    roles_with_skill = [r.role for r in resources_with_skill]
    print(f"Resources with {test_skill_filter} skill: {[r.name for r in resources_with_skill]}")
    print(f"Roles with {test_skill_filter} skill: {roles_with_skill}")
    
    # Filter forecasts by roles that have this skill
    better_filtered = ResourceDemandForecast.objects.filter(resource_role__in=roles_with_skill)
    print(f"Forecasts for roles with {test_skill_filter} skill: {better_filtered.count()}")
    
except Skill.DoesNotExist:
    print(f"Skill '{test_skill_filter}' not found")

print("\n=== INVESTIGATION COMPLETE ===")
