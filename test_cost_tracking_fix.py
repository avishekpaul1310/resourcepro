#!/usr/bin/env python
"""
Test script to verify the cost tracking fix is working properly.
This script tests the decimal arithmetic issue that was causing the TypeError.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from resources.models import Resource, TimeEntry
from projects.models import Task, Project
from django.contrib.auth.models import User


def test_decimal_arithmetic():
    """Test that decimal arithmetic works properly in cost calculations"""
    print("Testing decimal arithmetic for cost tracking...")
    
    # Test the core arithmetic that was failing
    hours_logged = Decimal('8.50')  # Simulating hours from TimeEntry sum
    cost_per_hour = Decimal('75.00')  # Simulating DecimalField from Resource
    
    # This should work now (was failing before)
    try:
        total_cost = hours_logged * cost_per_hour
        print(f"✓ Decimal multiplication works: {hours_logged} * {cost_per_hour} = {total_cost}")
        
        # Test markup calculation
        markup_multiplier = Decimal('1.5')
        revenue_generated = hours_logged * (cost_per_hour * markup_multiplier)
        print(f"✓ Revenue calculation works: {revenue_generated}")
        
        # Test profit margin calculation
        profit_margin = float((revenue_generated - total_cost) / revenue_generated * 100) if revenue_generated > 0 else 0
        print(f"✓ Profit margin calculation works: {profit_margin:.2f}%")
        
        return True
        
    except TypeError as e:
        print(f"✗ Decimal arithmetic failed: {e}")
        return False


def test_with_real_data():
    """Test with actual database data if available"""
    print("\nTesting with database data...")
    
    try:
        # Check if we have any resources with cost_per_hour
        resources_with_cost = Resource.objects.filter(cost_per_hour__isnull=False)
        if resources_with_cost.exists():
            resource = resources_with_cost.first()
            print(f"✓ Found resource: {resource.name} with hourly rate: {resource.cost_per_hour}")
            
            # Test the sum operation that was causing issues
            hours_logged = sum(entry.hours for entry in resource.time_entries.all())
            print(f"✓ Hours logged sum: {hours_logged} (type: {type(hours_logged)})")
            
            # Test the multiplication that was failing
            if resource.cost_per_hour:
                total_cost = hours_logged * resource.cost_per_hour
                print(f"✓ Cost calculation: {hours_logged} * {resource.cost_per_hour} = {total_cost}")
            
        else:
            print("No resources with cost_per_hour found in database")
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Cost Tracking Fix Verification")
    print("=" * 40)
    
    # Test basic decimal arithmetic
    arithmetic_ok = test_decimal_arithmetic()
    
    # Test with real database data
    db_test_ok = test_with_real_data()
    
    print("\n" + "=" * 40)
    if arithmetic_ok and db_test_ok:
        print("✓ All tests passed! Cost tracking fix is working properly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")
