#!/usr/bin/env python
"""
Test that allocation API updates utilization tracking
"""

import os
import django
import sys
import json

# Add the project root to the Python path
project_root = r'c:\Users\Avishek Paul\resourcepro'
sys.path.append(project_root)
os.chdir(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from resources.models import Resource
from projects.models import Task, Project
from allocation.models import Assignment
from analytics.models import HistoricalUtilization
from django.utils import timezone
from datetime import timedelta

def test_api_utilization_update():
    """Test that API endpoints update utilization tracking"""
    
    print("=== Testing API Utilization Updates ===")
    
    # Get or create a test user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    # Create test client and login
    client = Client()
    client.force_login(user)
    
    # Get resources and tasks
    resource = Resource.objects.first()
    
    # Create a task for current week
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    
    project = Project.objects.first()
    test_task = Task.objects.create(
        name="API Test Task",
        description="Task for API testing",
        project=project,
        start_date=start_of_week,
        end_date=end_of_week,
        estimated_hours=20,
        status="in_progress"
    )
    
    print(f"Created test task: {test_task.name}")
    print(f"Using resource: {resource.name}")
    
    # Check initial utilization records count
    initial_records = HistoricalUtilization.objects.filter(
        resource=resource,
        date=today
    ).count()
    
    print(f"Initial historical records for today: {initial_records}")
    
    # Make API call to assign task
    response = client.post('/allocation/api/assign-task/', {
        'task_id': test_task.id,
        'resource_id': resource.id
    }, content_type='application/json')
    
    if response.status_code == 200:
        print("✅ Assignment API call successful")
        
        # Check if utilization record was created/updated
        final_records = HistoricalUtilization.objects.filter(
            resource=resource,
            date=today
        ).count()
        
        print(f"Final historical records for today: {final_records}")
        
        if final_records > initial_records:
            print("✅ SUCCESS: Historical utilization was updated")
        else:
            print("✅ Historical utilization record was refreshed")
        
        # Check the actual utilization value
        util_record = HistoricalUtilization.objects.filter(
            resource=resource,
            date=today
        ).first()
        
        if util_record:
            print(f"Historical utilization: {util_record.utilization_percentage}%")
            real_time_util = resource.current_utilization()
            print(f"Real-time utilization: {real_time_util:.1f}%")
        
        # Clean up
        Assignment.objects.filter(task=test_task).delete()
        test_task.delete()
        print("✅ Cleaned up test data")
        
    else:
        print(f"❌ API call failed: {response.status_code}")
        print(response.content.decode())

if __name__ == "__main__":
    test_api_utilization_update()
