#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.services import CostTrackingService
from projects.models import Project
from datetime import datetime

print("=== TESTING COST TRACKING FILTERS ===")

cost_service = CostTrackingService()

print("\n1. All projects (no filters):")
all_projects = cost_service.get_cost_variance_report()
print(f"   Found {len(all_projects)} projects")
for p in all_projects:
    print(f"   - {p['project'].name} ({p['project'].status})")

print("\n2. Filter by status = 'planning':")
planning_projects = cost_service.get_cost_variance_report(project_status='planning')
print(f"   Found {len(planning_projects)} projects")
for p in planning_projects:
    print(f"   - {p['project'].name} ({p['project'].status})")

print("\n3. Filter by status = 'active':")
active_projects = cost_service.get_cost_variance_report(project_status='active')
print(f"   Found {len(active_projects)} projects")
for p in active_projects:
    print(f"   - {p['project'].name} ({p['project'].status})")

print("\n4. Available project managers:")
managers = Project.objects.filter(manager__isnull=False).values_list('manager__username', flat=True).distinct()
print(f"   Managers: {list(managers)}")

if managers:
    first_manager = list(managers)[0]
    print(f"\n5. Filter by client = '{first_manager}':")
    client_projects = cost_service.get_cost_variance_report(client=first_manager)
    print(f"   Found {len(client_projects)} projects")
    for p in client_projects:
        manager_name = p['project'].manager.username if p['project'].manager else 'No manager'
        print(f"   - {p['project'].name} (Manager: {manager_name})")

print("\n6. Filter by date range (start_date = 2025-05-01):")
start_date = datetime(2025, 5, 1).date()
date_filtered = cost_service.get_cost_variance_report(start_date=start_date)
print(f"   Found {len(date_filtered)} projects starting after {start_date}")
for p in date_filtered:
    print(f"   - {p['project'].name} (Start: {p['project'].start_date}, End: {p['project'].end_date})")
