#!/usr/bin/env python
"""
Check current risks and intervention scenarios in the database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.models import DynamicRisk, InterventionScenario, RiskCategory
from projects.models import Project, Task
from resources.models import Resource
from allocation.models import Assignment

print("=== CURRENT RISK ANALYSIS ===")

# Check for existing risks
risks = DynamicRisk.objects.all()
print(f"Dynamic Risks in Database: {risks.count()}")

for risk in risks[:5]:
    print(f"- {risk.title} ({risk.severity}) - {risk.description[:100]}...")

# Check intervention scenarios
scenarios = InterventionScenario.objects.all()
print(f"\nIntervention Scenarios: {scenarios.count()}")

for scenario in scenarios[:5]:
    print(f"- {scenario.title} ({scenario.scenario_type}) - {scenario.get_status_display()}")

# Check projects with potential risks
print("\n=== PROJECT ANALYSIS ===")
projects = Project.objects.all()

for project in projects:
    tasks = project.tasks.all()
    overdue_tasks = [t for t in tasks if hasattr(t, 'is_overdue') and t.is_overdue]
    total_assignments = Assignment.objects.filter(task__project=project).count()
    
    print(f"\nProject: {project.name}")
    print(f"  Status: {project.status}")
    print(f"  Tasks: {tasks.count()}")
    print(f"  Assignments: {total_assignments}")
    print(f"  Deadline: {project.end_date}")
    
    # Check for potential risks
    if project.status == 'active' and tasks.count() > 0:
        incomplete_tasks = [t for t in tasks if t.status != 'completed']
        print(f"  Incomplete tasks: {len(incomplete_tasks)}")
        
        # Resource utilization check
        resource_ids = Assignment.objects.filter(
            task__project=project
        ).values_list('resource_id', flat=True).distinct()
        
        if resource_ids:
            resources = Resource.objects.filter(id__in=resource_ids)
            for resource in resources:
                utilization = resource.current_utilization()
                print(f"  {resource.name}: {utilization}% utilization")

print("\n=== RESOURCES UTILIZATION ===")
resources = Resource.objects.all()

for resource in resources:
    utilization = resource.current_utilization()
    status = "OVERALLOCATED" if utilization > 100 else "HIGH" if utilization > 80 else "NORMAL"
    print(f"{resource.name} ({resource.role}): {utilization}% - {status}")

print("\n=== SUGGESTED TEST SCENARIOS ===")

# Find high utilization resources for reassignment testing
high_util_resources = []
low_util_resources = []

for resource in resources:
    util = resource.current_utilization()
    if util > 80:
        high_util_resources.append((resource.name, util))
    elif util < 60:
        low_util_resources.append((resource.name, util))

if high_util_resources and low_util_resources:
    print("✅ TASK REASSIGNMENT TEST READY:")
    print(f"  From: {high_util_resources[0][0]} ({high_util_resources[0][1]}%)")
    print(f"  To: {low_util_resources[0][0]} ({low_util_resources[0][1]}%)")

# Find active projects with upcoming deadlines
active_projects = Project.objects.filter(status='active')
if active_projects:
    print(f"\n✅ DEADLINE PRESSURE TEST READY:")
    for project in active_projects:
        print(f"  Project: {project.name} (Deadline: {project.end_date})")

# Check for skill gaps
print(f"\n✅ ADDITIONAL RESOURCE TEST READY:")
print(f"  Available roles: {', '.join(set(r.role for r in resources))}")
print(f"  Available skills: {', '.join([skill.name for skill in Resource.objects.first().skills.all()[:5]] if resources else [])}")

print("\n=== RECOMMENDED TESTING ORDER ===")
print("1. Task Reassignment: Use overallocated resources")
print("2. Overtime Authorization: Use active project deadlines") 
print("3. Additional Resource: Simulate skill gaps")
print("4. Deadline Extension: Use tight timeline projects")
print("5. Scope Reduction: Use large projects with many tasks")
