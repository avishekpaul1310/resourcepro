from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import Project, Task
from resources.models import Resource, Skill, TimeEntry
from allocation.models import Assignment


class ProjectModelTest(TestCase):
    """Test cases for Project model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name="E-commerce Platform",
            description="Online shopping platform development",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            manager=self.user,
            status='active',
            priority=4,
            budget=Decimal('100000.00')
        )
    
    def test_project_creation(self):
        """Test project creation and basic properties"""
        self.assertEqual(str(self.project), "E-commerce Platform")
        self.assertEqual(self.project.status, 'active')
        self.assertEqual(self.project.priority, 4)
        self.assertEqual(self.project.budget, Decimal('100000.00'))
        self.assertEqual(self.project.manager, self.user)
    
    def test_project_status_choices(self):
        """Test project status choices"""
        valid_statuses = ['planning', 'active', 'on_hold', 'completed', 'cancelled']
        
        for status in valid_statuses:
            project = Project.objects.create(
                name=f"Project {status}",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                status=status
            )
            self.assertEqual(project.status, status)
    
    def test_project_completion_percentage_no_tasks(self):
        """Test completion percentage with no tasks"""
        completion = self.project.get_completion_percentage()
        self.assertEqual(completion, 0)
    
    def test_project_completion_percentage_with_tasks(self):
        """Test completion percentage calculation with tasks"""
        # Create tasks with different completion levels
        Task.objects.create(
            project=self.project,
            name="Task 1",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20,
            completion_percentage=100
        )
        
        Task.objects.create(
            project=self.project,
            name="Task 2",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=30,
            completion_percentage=50
        )
        
        # Expected: (20*100 + 30*50) / (20+30) = 3500/50 = 70%
        completion = self.project.get_completion_percentage()
        self.assertEqual(completion, 70.0)
    
    def test_project_estimated_cost(self):
        """Test estimated cost calculation"""
        # Create resources and assignments
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer",
            cost_per_hour=Decimal('75.00')
        )
        
        task = Task.objects.create(
            project=self.project,
            name="Development Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        Assignment.objects.create(
            resource=resource,
            task=task,
            allocated_hours=20
        )
        
        estimated_cost = self.project.get_estimated_cost()
        expected_cost = 20 * Decimal('75.00')  # 1500.00
        self.assertEqual(estimated_cost, expected_cost)
    
    def test_project_actual_cost(self):
        """Test actual cost calculation based on time entries"""
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer",
            cost_per_hour=Decimal('75.00')
        )
        
        task = Task.objects.create(
            project=self.project,
            name="Development Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=task,
            date=date.today(),
            hours=8
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=task,
            date=date.today() + timedelta(days=1),
            hours=6
        )
        
        actual_cost = self.project.get_actual_cost()
        expected_cost = 14 * Decimal('75.00')  # 1050.00
        self.assertEqual(actual_cost, expected_cost)
    
    def test_budget_variance(self):
        """Test budget variance calculation"""
        # Set up a scenario with actual costs
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer",
            cost_per_hour=Decimal('75.00')
        )
        
        task = Task.objects.create(
            project=self.project,
            name="Development Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=task,
            date=date.today(),
            hours=10
        )
        
        variance = self.project.get_budget_variance()
        # Budget: 100000, Actual: 750 (10 * 75)
        expected_variance = Decimal('100000.00') - Decimal('750.00')
        self.assertEqual(variance, expected_variance)
    
    def test_budget_variance_no_budget(self):
        """Test budget variance when no budget is set"""
        project = Project.objects.create(
            name="No Budget Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        variance = project.get_budget_variance()
        self.assertIsNone(variance)


class TaskModelTest(TestCase):
    """Test cases for Task model"""
    
    def setUp(self):
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.skill = Skill.objects.create(name="Python")
        
        self.task = Task.objects.create(
            project=self.project,
            name="Development Task",
            description="Implement user authentication",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20,
            status='in_progress',
            completion_percentage=30,
            priority=4
        )
        
        self.task.skills_required.add(self.skill)
    
    def test_task_creation(self):
        """Test task creation and basic properties"""
        expected_str = f"{self.project.name} - {self.task.name}"
        self.assertEqual(str(self.task), expected_str)
        self.assertEqual(self.task.estimated_hours, 20)
        self.assertEqual(self.task.status, 'in_progress')
        self.assertEqual(self.task.completion_percentage, 30)
        self.assertEqual(self.task.priority, 4)
    
    def test_task_status_choices(self):
        """Test task status choices"""
        valid_statuses = ['not_started', 'in_progress', 'completed', 'blocked']
        
        for status in valid_statuses:
            task = Task.objects.create(
                project=self.project,
                name=f"Task {status}",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5),
                estimated_hours=10,
                status=status
            )
            self.assertEqual(task.status, status)
    
    def test_get_actual_hours(self):
        """Test actual hours calculation from time entries"""
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer"
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=self.task,
            date=date.today(),
            hours=8
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=self.task,
            date=date.today() + timedelta(days=1),
            hours=6
        )
        
        actual_hours = self.task.get_actual_hours()
        self.assertEqual(actual_hours, 14)
    
    def test_get_actual_hours_no_entries(self):
        """Test actual hours with no time entries"""
        actual_hours = self.task.get_actual_hours()
        self.assertEqual(actual_hours, 0)
    
    def test_estimated_vs_actual_variance(self):
        """Test variance calculation between estimated and actual hours"""
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer"
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=self.task,
            date=date.today(),
            hours=15
        )
        
        variance = self.task.get_estimated_vs_actual_variance()
        # Estimated: 20, Actual: 15, Variance: 20 - 15 = 5
        self.assertEqual(variance, 5)
    
    def test_time_tracking_efficiency(self):
        """Test efficiency calculation"""
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer"
        )
        
        TimeEntry.objects.create(
            resource=resource,
            task=self.task,
            date=date.today(),
            hours=25  # Over estimated
        )
        
        efficiency = self.task.get_time_tracking_efficiency()
        # Estimated: 20, Actual: 25, Efficiency: (20/25) * 100 = 80%
        self.assertEqual(efficiency, 80.0)
    
    def test_is_assigned_property(self):
        """Test is_assigned property"""
        # Initially not assigned
        self.assertFalse(self.task.is_assigned)
        
        # Add assignment
        resource = Resource.objects.create(
            name="Developer",
            role="Software Developer"
        )
        
        Assignment.objects.create(
            resource=resource,
            task=self.task,
            allocated_hours=20
        )
        
        # Refresh from database
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_assigned)
    
    def test_is_overdue_property(self):
        """Test is_overdue property"""
        # Task ending in the future - not overdue
        future_task = Task.objects.create(
            project=self.project,
            name="Future Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=10
        )
        self.assertFalse(future_task.is_overdue)
        
        # Task that ended yesterday and not completed - overdue
        past_task = Task.objects.create(
            project=self.project,
            name="Past Task",
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() - timedelta(days=1),
            estimated_hours=10,
            status='in_progress'
        )
        self.assertTrue(past_task.is_overdue)
        
        # Task that ended yesterday but completed - not overdue
        completed_task = Task.objects.create(
            project=self.project,
            name="Completed Task",
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() - timedelta(days=1),
            estimated_hours=10,
            status='completed'
        )
        self.assertFalse(completed_task.is_overdue)
    
    def test_task_dependencies(self):
        """Test task dependencies"""
        dependency_task = Task.objects.create(
            project=self.project,
            name="Dependency Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            estimated_hours=10
        )
        
        self.task.dependencies.add(dependency_task)
        
        # Test forward relationship
        dependencies = self.task.dependencies.all()
        self.assertIn(dependency_task, dependencies)
        
        # Test reverse relationship
        dependents = dependency_task.dependents.all()
        self.assertIn(self.task, dependents)


class ProjectViewsTest(TestCase):
    """Test cases for Project views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.user
        )
        
        self.client.force_login(self.user)
    
    def test_project_list_view(self):
        """Test project list view"""
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")
    
    def test_project_detail_view(self):
        """Test project detail view"""
        response = self.client.get(f'/projects/{self.project.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")
    
    def test_project_create_view_get(self):
        """Test project create view GET request"""
        response = self.client.get('/projects/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_project_create_view_post(self):
        """Test project create view POST request"""
        data = {
            'name': 'New Project',
            'description': 'A new test project',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 3
        }
        response = self.client.post('/projects/create/', data)
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if project was created
        self.assertTrue(Project.objects.filter(name='New Project').exists())


class TaskViewsTest(TestCase):
    """Test cases for Task views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Test Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        self.client.force_login(self.user)
    
    def test_task_list_view(self):
        """Test task list view"""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
    
    def test_task_detail_view(self):
        """Test task detail view"""
        response = self.client.get(f'/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
    
    def test_task_create_view_get(self):
        """Test task create view GET request"""
        response = self.client.get('/tasks/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_task_create_view_post(self):
        """Test task create view POST request"""
        data = {
            'project': self.project.id,
            'name': 'New Task',
            'description': 'A new test task',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 15,
            'status': 'not_started',
            'priority': 3
        }
        response = self.client.post('/tasks/create/', data)
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if task was created
        self.assertTrue(Task.objects.filter(name='New Task').exists())


class ProjectIntegrationTest(TestCase):
    """Integration tests for Project functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name="Full Project Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            manager=self.user,
            budget=Decimal('50000.00')
        )
        
        self.skill = Skill.objects.create(name="Python")
        
        self.resource = Resource.objects.create(
            name="Senior Developer",
            role="Software Developer",
            cost_per_hour=Decimal('85.00')
        )
    
    def test_complete_project_workflow(self):
        """Test complete project workflow from creation to completion"""
        # Create tasks
        task1 = Task.objects.create(
            project=self.project,
            name="Backend Development",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=20),
            estimated_hours=100,
            status='in_progress',
            completion_percentage=75
        )
        
        task2 = Task.objects.create(
            project=self.project,
            name="Frontend Development",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=40),
            estimated_hours=80,
            status='not_started',
            completion_percentage=0
        )
        
        # Add skill requirements
        task1.skills_required.add(self.skill)
        task2.skills_required.add(self.skill)
        
        # Create assignments
        Assignment.objects.create(
            resource=self.resource,
            task=task1,
            allocated_hours=100
        )
        
        Assignment.objects.create(
            resource=self.resource,
            task=task2,
            allocated_hours=80
        )
        
        # Add time entries
        TimeEntry.objects.create(
            resource=self.resource,
            task=task1,
            date=date.today(),
            hours=8
        )
        
        TimeEntry.objects.create(
            resource=self.resource,
            task=task1,
            date=date.today() + timedelta(days=1),
            hours=7.5
        )
        
        # Test project metrics
        completion = self.project.get_completion_percentage()
        # Expected: (100*75 + 80*0) / (100+80) = 7500/180 = 41.7%
        self.assertAlmostEqual(completion, 41.7, places=1)
        
        estimated_cost = self.project.get_estimated_cost()
        # Expected: (100 + 80) * 85 = 15300
        self.assertEqual(estimated_cost, Decimal('15300.00'))
        
        actual_cost = self.project.get_actual_cost()
        # Expected: (8 + 7.5) * 85 = 1317.5
        self.assertEqual(actual_cost, Decimal('1317.50'))
        
        budget_variance = self.project.get_budget_variance()
        # Expected: 50000 - 1317.5 = 48682.5
        self.assertEqual(budget_variance, Decimal('48682.50'))
    
    def test_task_dependency_management(self):
        """Test task dependency management"""
        # Create dependent tasks
        design_task = Task.objects.create(
            project=self.project,
            name="Design Phase",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=40
        )
        
        development_task = Task.objects.create(
            project=self.project,
            name="Development Phase",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=30),
            estimated_hours=120
        )
        
        testing_task = Task.objects.create(
            project=self.project,
            name="Testing Phase",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=40),
            estimated_hours=60
        )
        
        # Set up dependencies
        development_task.dependencies.add(design_task)
        testing_task.dependencies.add(development_task)
        
        # Test dependency relationships
        self.assertIn(design_task, development_task.dependencies.all())
        self.assertIn(development_task, testing_task.dependencies.all())
        
        # Test reverse relationships
        self.assertIn(development_task, design_task.dependents.all())
        self.assertIn(testing_task, development_task.dependents.all())
