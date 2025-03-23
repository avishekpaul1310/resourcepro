# run_tests.py
import os
import sys
import django
import datetime
import unittest
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.core import management

def run_tests():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
    django.setup()
    
    # Run migrations
    management.call_command('migrate')
    
    # Run tests with coverage
    management.call_command('test', 
                          '--settings=resourcepro.settings',
                          '--exclude-tag=selenium')
    
    # Run Selenium tests separately if SELENIUM_TESTS env variable is set
    if os.environ.get('SELENIUM_TESTS', 'false').lower() == 'true':
        management.call_command('test', 
                              '--settings=resourcepro.settings',
                              '--tag=selenium')
    
    # Generate test coverage report
    try:
        from coverage import Coverage
        cov = Coverage()
        cov.start()
        
        runner = DiscoverRunner(interactive=False)
        failures = runner.run_tests(['accounts', 'allocation', 'api', 
                                    'core', 'dashboard', 'projects', 'resources'])
        
        cov.stop()
        cov.save()
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print(f"Coverage report generated in htmlcov/ directory")
        
        sys.exit(bool(failures))
    except ImportError:
        print("Coverage.py not installed. Skipping coverage report.")
    
if __name__ == '__main__':
    run_tests()