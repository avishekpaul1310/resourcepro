#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from projects.models import Project
from datetime import datetime

print("=== DATE RANGE FILTER TEST SUGGESTIONS ===")

projects = Project.objects.all()
print("\nAll project dates:")
for p in projects:
    print(f"  {p.name}: {p.start_date} to {p.end_date}")

print("\n=== SUGGESTED DATE RANGE TESTS ===")

print("\n1. Test: All projects (no date filter)")
print("   Start Date: (empty)")
print("   End Date: (empty)")
print("   Expected: 5 projects")

print("\n2. Test: Projects that END after May 1, 2025")
print("   Start Date: 2025-05-01")
print("   End Date: (empty)")
print("   Expected: All projects (since all end after May 1)")

print("\n3. Test: Projects that START before June 1, 2025")
print("   Start Date: (empty)")  
print("   End Date: 2025-06-01")
print("   Expected: All projects (since all start before June 1)")

print("\n4. Test: Projects active in May 2025")
print("   Start Date: 2025-05-01")
print("   End Date: 2025-05-31")
print("   Expected: Projects that overlap with May 2025")

print("\n5. Test: Projects that END after September 1, 2025")
print("   Start Date: 2025-09-01")
print("   End Date: (empty)")
print("   Expected: Some projects (those ending after Sept 1)")

print("\n6. Test: Projects that START before April 15, 2025")
print("   Start Date: (empty)")
print("   End Date: 2025-04-15")
print("   Expected: Some projects (those starting before April 15)")

print("\n7. Test: Very narrow range (should return 0)")
print("   Start Date: 2025-12-01")
print("   End Date: 2025-12-31")
print("   Expected: 0 projects")

# Let's calculate some exact examples
earliest_start = min(p.start_date for p in projects)
latest_end = max(p.end_date for p in projects)

print(f"\n=== PROJECT DATE RANGE ===")
print(f"Earliest project start: {earliest_start}")
print(f"Latest project end: {latest_end}")

print(f"\n=== SPECIFIC TEST EXAMPLES ===")
print(f"1. To see ALL projects: Leave both dates empty")
print(f"2. To see SOME projects: Start Date: 2025-08-01 (should exclude early-ending projects)")
print(f"3. To see NO projects: Start Date: 2025-12-01, End Date: 2025-12-31")
