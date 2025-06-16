#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.services import CostTrackingService
from projects.models import Project

print("=== DEBUG: TESTING FILTERS STEP BY STEP ===")

cost_service = CostTrackingService()

print("\n1. All projects in database:")
all_projects = Project.objects.all()
for p in all_projects:
    print(f"   - {p.name} (status: {p.status})")

print(f"\nTotal projects: {all_projects.count()}")

print("\n2. Testing filter: project_status='planning'")
planning_projects = Project.objects.filter(status='planning')
print(f"Projects with status 'planning': {planning_projects.count()}")
for p in planning_projects:
    print(f"   - {p.name}")

print("\n3. Testing CostTrackingService with no filters:")
report_no_filter = cost_service.get_cost_variance_report()
print(f"Service returns {len(report_no_filter)} projects")
total_budget_no_filter = sum(item['budget'] for item in report_no_filter if item['budget'])
print(f"Total budget (no filter): ${total_budget_no_filter}")

print("\n4. Testing CostTrackingService with project_status='planning':")
report_planning = cost_service.get_cost_variance_report(project_status='planning')
print(f"Service returns {len(report_planning)} projects")
total_budget_planning = sum(item['budget'] for item in report_planning if item['budget'])
print(f"Total budget (planning filter): ${total_budget_planning}")

print("\n5. Testing CostTrackingService with project_status='active':")
report_active = cost_service.get_cost_variance_report(project_status='active')
print(f"Service returns {len(report_active)} projects")
total_budget_active = sum(item['budget'] for item in report_active if item['budget'])
print(f"Total budget (active filter): ${total_budget_active}")

print("\n6. Testing CostTrackingService with project_status='nonexistent':")
report_none = cost_service.get_cost_variance_report(project_status='nonexistent')
print(f"Service returns {len(report_none)} projects")
total_budget_none = sum(item['budget'] for item in report_none if item['budget'])
print(f"Total budget (nonexistent filter): ${total_budget_none}")

print("\n=== EXPECTED RESULTS ===")
print("- No filter: Should show all 5 projects, $195,000 total budget")
print("- Planning filter: Should show 5 projects, $195,000 total budget")
print("- Active filter: Should show 0 projects, $0 total budget")
print("- Nonexistent filter: Should show 0 projects, $0 total budget")
