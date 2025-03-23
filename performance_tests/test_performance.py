from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.auth.models import User
from resources.models import Resource
from projects.models import Project, Task
import time
from django.utils import timezone
from datetime import timedelta

class PerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        # Create test data - lots of resources and projects
        self.create_bulk_data()
    
    def create_bulk_data(self):
        # Create 50 resources
        resources = []
        for i in range(50):
            resources.append(Resource(
                name=f'Resource {i}',
                role=f'Role {i % 5}',
                capacity=40
            ))
        Resource.objects.bulk_create(resources)
        
        # Create 20 projects
        projects = []
        for i in range(20):
            projects.append(Project(
                name=f'Project {i}',
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=90),
                status='active'
            ))
        Project.objects.bulk_create(projects)
        
        # Create 200 tasks (10 per project)
        tasks = []
        for project in Project.objects.all():
            for i in range(10):
                tasks.append(Task(
                    project=project,
                    name=f'Task {i} for {project.name}',
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=30),
                    estimated_hours=20,
                    status='not_started'
                ))
        Task.objects.bulk_create(tasks)
    
    def test_dashboard_performance(self):
        """Test dashboard page performance"""
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('dashboard'))
            end_time = time.time()
            
        # Check response time - should be under 1 second
        self.assertLess(end_time - start_time, 1.0)
        
        # Check query count - aim for efficient querying
        self.assertLess(len(context), 100)
    
    def test_allocation_board_performance(self):
        """Test allocation board performance with many resources and tasks"""
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('allocation_board'))
            end_time = time.time()
            
        # Check response time - should be under a more lenient 2 seconds 
        # for the complex allocation page
        self.assertLess(end_time - start_time, 2.0)
        
        # Check query count
        self.assertLess(len(context), 310)