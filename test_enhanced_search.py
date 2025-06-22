#!/usr/bin/env python
"""
Test script to verify enhanced search data collection
Run this to test if the search can access all project information
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.ai_services import NaturalLanguageInterfaceService
from resources.models import Resource, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment

def test_comprehensive_data_access():
    """Test if we can access comprehensive project data"""
    
    print("=== Testing Comprehensive Data Access ===\n")
    
    # Test 1: Check available models and fields
    print("1. Available Models and Key Fields:")
    
    # Resources
    if Resource.objects.exists():
        sample_resource = Resource.objects.first()
        print(f"   Resource fields: {[f.name for f in sample_resource._meta.fields]}")
        
        # Check for time entries
        time_entries_exist = hasattr(sample_resource, 'time_entries') or hasattr(sample_resource, 'timeentry_set')
        print(f"   Time entries available: {time_entries_exist}")
        
        if time_entries_exist:
            try:
                time_entries = getattr(sample_resource, 'time_entries', sample_resource.timeentry_set)
                time_entry_count = time_entries.count() if hasattr(time_entries, 'count') else 0
                print(f"   Time entries count: {time_entry_count}")
                
                if time_entry_count > 0:
                    sample_entry = time_entries.first()
                    print(f"   Time entry fields: {[f.name for f in sample_entry._meta.fields]}")
            except Exception as e:
                print(f"   Error accessing time entries: {e}")
    
    # Projects
    if Project.objects.exists():
        sample_project = Project.objects.first()
        print(f"   Project fields: {[f.name for f in sample_project._meta.fields]}")
        
        # Test project methods
        methods_to_test = ['get_completion_percentage', 'get_estimated_cost', 'get_actual_cost', 'get_budget_variance']
        for method_name in methods_to_test:
            if hasattr(sample_project, method_name):
                try:
                    result = getattr(sample_project, method_name)()
                    print(f"   {method_name}: {result}")
                except Exception as e:
                    print(f"   {method_name}: Error - {e}")
    
    # Tasks
    if Task.objects.exists():
        sample_task = Task.objects.first()
        print(f"   Task fields: {[f.name for f in sample_task._meta.fields]}")
        
        # Test task methods
        methods_to_test = ['get_actual_hours', 'get_time_tracking_efficiency', 'is_assigned', 'is_overdue']
        for method_name in methods_to_test:
            if hasattr(sample_task, method_name):
                try:
                    result = getattr(sample_task, method_name)() if callable(getattr(sample_task, method_name)) else getattr(sample_task, method_name)
                    print(f"   {method_name}: {result}")
                except Exception as e:
                    print(f"   {method_name}: Error - {e}")
    
    # Assignments
    if Assignment.objects.exists():
        sample_assignment = Assignment.objects.first()
        print(f"   Assignment fields: {[f.name for f in sample_assignment._meta.fields]}")
    
    print("\n" + "="*50)
    
    # Test 2: NLI Service data gathering
    print("2. Testing NLI Service Data Gathering:")
    
    nli = NaturalLanguageInterfaceService()
    try:
        context = nli._gather_comprehensive_context()
        
        print(f"   Summary keys: {list(context.get('summary', {}).keys())}")
        print(f"   Resources count: {len(context.get('resources', []))}")
        print(f"   Projects count: {len(context.get('projects', []))}")
        print(f"   Tasks count: {len(context.get('tasks', []))}")
        print(f"   Assignments count: {len(context.get('assignments', []))}")
        
        # Check resource data completeness
        if context.get('resources'):
            sample_resource = context['resources'][0]
            print(f"   Sample resource keys: {list(sample_resource.keys())}")
            
        # Check project data completeness
        if context.get('projects'):
            sample_project = context['projects'][0]
            print(f"   Sample project keys: {list(sample_project.keys())}")
            
        # Check conflicts data
        conflicts = context.get('conflicts', {})
        print(f"   Conflicts detected: {list(conflicts.keys())}")
        for conflict_type, conflict_list in conflicts.items():
            print(f"     {conflict_type}: {len(conflict_list) if isinstance(conflict_list, list) else conflict_list}")
            
    except Exception as e:
        print(f"   Error gathering context: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    
    # Test 3: Sample queries
    print("3. Testing Sample Queries:")
    
    test_queries = [
        "which resource has the most billable working hours?",
        "show me project budget status",
        "what tasks are overdue?", 
        "which projects are over budget?",
        "show resource utilization breakdown",
        "what are the skill requirements for unassigned tasks?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            result = nli.process_query(query)
            response = result.get('response', {})
            answer = response.get('answer', 'No answer provided')
            print(f"Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_comprehensive_data_access()
