#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from analytics.services import CostTrackingService
from projects.models import Project

print("=== ANALYTICS DASHBOARD COST VALUES ===")

# Test what the analytics dashboard should show
cost_service = CostTrackingService()
cost_report = cost_service.get_cost_variance_report()

# Calculate the same values as the dashboard
total_budget = sum(item.get('budget', 0) for item in cost_report if item.get('budget'))
actual_costs = sum(item.get('actual_cost', 0) for item in cost_report)
budget_variance = total_budget - actual_costs

print(f"Total Budget (dashboard): ${total_budget:,.2f}")
print(f"Actual Costs (dashboard): ${actual_costs:,.2f}")
print(f"Budget Variance (dashboard): ${budget_variance:,.2f}")

print("\n=== INDIVIDUAL PROJECT DETAILS ===")
for item in cost_report:
    project = item['project']
    print(f"\nProject: {project.name}")
    print(f"  Budget: ${item.get('budget', 0):,.2f}")
    print(f"  Estimated Cost: ${item.get('estimated_cost', 0):,.2f}")
    print(f"  Actual Cost: ${item.get('actual_cost', 0):,.2f}")
    print(f"  Variance: ${item.get('variance', 0):,.2f}")
    print(f"  Budget Utilization: {item.get('budget_utilization', 0):.1f}%")

print(f"\n=== SUMMARY ===")
print(f"Projects over budget: {len([item for item in cost_report if item['variance'] < 0])}")
print(f"Total projects: {len(cost_report)}")
