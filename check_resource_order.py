#!/usr/bin/env python
"""
Check the order of resources and their utilization
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

from resources.models import Resource

def check_resource_order():
    """Check the order and utilization of all resources"""
    
    print("=== All Resources (Database Order) ===")
    
    for i, resource in enumerate(Resource.objects.all(), 1):
        current_util = resource.current_utilization()
        print(f"{i:2d}. {resource.name}: {current_util:.1f}%")
    
    print("\n=== Resources shown in Analytics (first 10) ===")
    for i, resource in enumerate(Resource.objects.all()[:10], 1):
        current_util = resource.current_utilization()
        print(f"{i:2d}. {resource.name}: {current_util:.1f}%")
    
    print("\n=== Resources with >0% utilization ===")
    for resource in Resource.objects.all():
        current_util = resource.current_utilization()
        if current_util > 0:
            print(f"    {resource.name}: {current_util:.1f}%")

if __name__ == "__main__":
    check_resource_order()
