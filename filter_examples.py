#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from projects.models import Project
from analytics.services import CostTrackingService
from datetime import datetime

print("=== EXACT FILTER EXAMPLES FOR YOUR DATA ===")

# Check what data exists
projects = Project.objects.all()
print(f"\nTotal projects in database: {projects.count()}")

print("\n=== PROJECT DETAILS ===")
for p in projects:
    manager = p.manager.username if p.manager else "No manager"
    print(f"Project: {p.name}")
    print(f"  Status: {p.status}")
    print(f"  Start Date: {p.start_date}")
    print(f"  End Date: {p.end_date}")
    print(f"  Manager: {manager}")
    print(f"  Budget: ${p.budget}")
    print()

print("=== FILTER EXAMPLES THAT WILL SHOW DATA ===")

print("\n1. TO SEE ALL DATA:")
print("   - Start Date: (leave empty)")
print("   - End Date: (leave empty)")
print("   - Project Status: All Projects")
print("   - Client: All Clients")

print("\n2. TO FILTER BY STATUS:")
statuses = list(set([p.status for p in projects]))
print(f"   Available statuses: {statuses}")
for status in statuses:
    count = projects.filter(status=status).count()
    print(f"   - Select '{status}' to see {count} project(s)")

print("\n3. TO FILTER BY CLIENT:")
managers = list(set([p.manager.username for p in projects if p.manager]))
print(f"   Available clients: {managers}")
for manager in managers:
    count = projects.filter(manager__username=manager).count()
    print(f"   - Select '{manager}' to see {count} project(s)")

print("\n4. TO FILTER BY DATE RANGE:")
earliest_start = min([p.start_date for p in projects])
latest_end = max([p.end_date for p in projects])
print(f"   Project dates range from {earliest_start} to {latest_end}")
print(f"   - Start Date: {earliest_start} (to include all projects)")
print(f"   - End Date: {latest_end} (to include all projects)")
print(f"   - Start Date: 2025-05-01 (to see projects ending after this date)")
print(f"   - End Date: 2025-08-01 (to see projects starting before this date)")

print("\n=== TEST SPECIFIC FILTER COMBINATIONS ===")

cost_service = CostTrackingService()

print("\n1. All projects (no filters):")
all_data = cost_service.get_cost_variance_report()
print(f"   Returns {len(all_data)} projects")
if all_data:
    total_budget = sum(item['budget'] for item in all_data if item['budget'])
    total_actual = sum(item['actual_cost'] for item in all_data)
    print(f"   Total Budget: ${total_budget}")
    print(f"   Total Actual: ${total_actual}")

if statuses:
    print(f"\n2. Filter by status '{statuses[0]}':")
    status_data = cost_service.get_cost_variance_report(project_status=statuses[0])
    print(f"   Returns {len(status_data)} projects")
    if status_data:
        total_budget = sum(item['budget'] for item in status_data if item['budget'])
        total_actual = sum(item['actual_cost'] for item in status_data)
        print(f"   Total Budget: ${total_budget}")
        print(f"   Total Actual: ${total_actual}")

if managers:
    print(f"\n3. Filter by client '{managers[0]}':")
    client_data = cost_service.get_cost_variance_report(client=managers[0])
    print(f"   Returns {len(client_data)} projects")
    if client_data:
        total_budget = sum(item['budget'] for item in client_data if item['budget'])
        total_actual = sum(item['actual_cost'] for item in client_data)
        print(f"   Total Budget: ${total_budget}")
        print(f"   Total Actual: ${total_actual}")

print(f"\n4. Filter by date range (2025-04-01 to 2025-12-31):")
date_data = cost_service.get_cost_variance_report(
    start_date=datetime(2025, 4, 1).date(),
    end_date=datetime(2025, 12, 31).date()
)
print(f"   Returns {len(date_data)} projects")
if date_data:
    total_budget = sum(item['budget'] for item in date_data if item['budget'])
    total_actual = sum(item['actual_cost'] for item in date_data)
    print(f"   Total Budget: ${total_budget}")
    print(f"   Total Actual: ${total_actual}")

print("\n=== RECOMMENDED FILTER SETTINGS ===")
print("To see your actual data, use these exact settings:")
print("1. Start Date: (leave empty)")
print("2. End Date: (leave empty)")
print("3. Project Status: 'All Projects' OR 'planning'")
print("4. Client: 'All Clients'")
print("5. Click 'Generate Report'")
