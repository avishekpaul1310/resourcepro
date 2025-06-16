#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from projects.models import Project
from resources.models import Resource
from allocation.models import Assignment
from analytics.models import ResourceDemandForecast, SkillDemandAnalysis, HistoricalUtilization

print("=== DATABASE CONTENT CHECK ===")
print(f"Projects: {Project.objects.count()}")
print(f"Resources: {Resource.objects.count()}")
print(f"Assignments: {Assignment.objects.count()}")
print(f"Resource Demand Forecasts: {ResourceDemandForecast.objects.count()}")
print(f"Skill Demand Analyses: {SkillDemandAnalysis.objects.count()}")
print(f"Historical Utilizations: {HistoricalUtilization.objects.count()}")

print("\n=== PROJECT DETAILS ===")
for project in Project.objects.all()[:5]:
    print(f"- {project.name} (Status: {project.status})")

print("\n=== RESOURCE DETAILS ===")
for resource in Resource.objects.all()[:5]:
    print(f"- {resource.name} (Role: {resource.role})")

print("\n=== ASSIGNMENT DETAILS ===")
for assignment in Assignment.objects.all()[:5]:
    print(f"- {assignment.resource.name} -> Task: {assignment.task.name} ({assignment.allocated_hours}h)")
