#!/usr/bin/env python
"""
Demonstrate pagination with different scenarios
"""

import os
import django
import sys

# Add the project root to the Python path
project_root = r'c:\Users\Avishek Paul\resourcepro'
sys.path.append(project_root)
os.chdir(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.core.paginator import Paginator
from resources.models import Resource

def demonstrate_pagination():
    """Demonstrate how pagination works with different scenarios"""
    
    print("=== Pagination Demonstration ===")
    
    # Get all resources with utilization
    utilization_data = []
    for resource in Resource.objects.all():
        current_util = resource.current_utilization()
        utilization_data.append({
            'resource': resource,
            'utilization_rate': round(current_util, 1)
        })
    
    # Sort by utilization (highest first)
    utilization_data.sort(key=lambda x: x['utilization_rate'], reverse=True)
    
    total_resources = len(utilization_data)
    active_resources = len([d for d in utilization_data if d['utilization_rate'] > 0])
    
    print(f"Total resources: {total_resources}")
    print(f"Active resources: {active_resources}")
    print()
    
    # Test different pagination scenarios
    scenarios = [
        {'per_page': 5, 'description': 'Small pages (5 per page)'},
        {'per_page': 10, 'description': 'Default pages (10 per page)'},
        {'per_page': 15, 'description': 'Large pages (15 per page)'},
    ]
    
    for scenario in scenarios:
        per_page = scenario['per_page']
        paginator = Paginator(utilization_data, per_page)
        
        print(f"--- {scenario['description']} ---")
        print(f"Total pages: {paginator.num_pages}")
        
        # Show first page
        page1 = paginator.page(1)
        print(f"Page 1 shows resources {page1.start_index()}-{page1.end_index()}:")
        
        for i, data in enumerate(page1.object_list[:3], 1):  # Show first 3
            resource = data['resource']
            util = data['utilization_rate']
            print(f"  {i}. {resource.name}: {util}%")
        
        if len(page1.object_list) > 3:
            print(f"  ... and {len(page1.object_list) - 3} more")
        print()
    
    print("✅ Pagination Benefits:")
    print("  - Keeps page load fast even with many resources")
    print("  - Maintains clean, organized view")
    print("  - Preserves utilization-based sorting")
    print("  - Shows most important resources first")
    print("  - Flexible per-page options (5-50 resources)")

if __name__ == "__main__":
    demonstrate_pagination()
