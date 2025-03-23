#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.core import management

def run_tests():
    """Run all test modules separately to avoid import issues"""
    test_modules = [
        'accounts.tests',
        'resources.tests',
        'integration_tests',
        'e2e_tests',
        'performance_tests'
    ]
    
    failed = False
    for module in test_modules:
        print(f"\n=== Running tests for {module} ===")
        try:
            # Use management command to run tests for each module separately
            result = management.call_command('test', module, interactive=False)
            if result:
                failed = True
        except Exception as e:
            print(f"Error running tests for {module}: {e}")
            failed = True
    
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(run_tests())