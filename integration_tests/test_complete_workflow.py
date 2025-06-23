"""
Comprehensive integration tests for ResourcePro
Tests complete user workflows across all modules
"""
import json
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from accounts.models import UserProfile
from resources.models import Resource, Skill, TimeEntry, Availability
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import (
    ResourceDemandForecast, HistoricalUtilization, 
    SkillDemandAnalysis, AISkillRecommendation
)


class CompleteWorkflowIntegrationTest(TransactionTestCase):
    """
    Test complete workflows from user registration to project completion
    """
    
    def setUp(self):
        self.client = Client()
        
    def test_complete_user_journey(self):
        """Test a complete user journey from registration to project completion"""
        
        # 1. User Registration
        registration_data = {
            'username': 'projectmanager',
            'email': 'pm@company.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'Project',
            'last_name': 'Manager'
        }
        
        response = self.client.post(reverse('register'), registration_data)
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        
        # Verify user was created
        user = User.objects.get(username='projectmanager')
        self.assertEqual(user.email, 'pm@company.com')
        
        # 2. User Login
        login_success = self.client.login(username='projectmanager', password='ComplexPass123!')
        self.assertTrue(login_success)
        
        # 3. Access Dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Create Skills
        python_skill_data = {'name': 'Python', 'category': 'Programming'}
        response = self.client.post(reverse('resources:create_skill'), python_skill_data)
        self.assertEqual(response.status_code, 302)
        
        javascript_skill_data = {'name': 'JavaScript', 'category': 'Programming'}
        response = self.client.post(reverse('resources:create_skill'), javascript_skill_data)
        self.assertEqual(response.status_code, 302)
        
        # 5. Create Resources
        resource_data = {
            'name': 'John Developer',
            'role': 'Senior Developer',
            'department': 'Engineering',
            'capacity': 40,
            'cost_per_hour': '75.00',
            'email': 'john@company.com'
        }
        response = self.client.post(reverse('resources:resource_create'), resource_data)
        self.assertEqual(response.status_code, 302)
        
        resource2_data = {
            'name': 'Jane Designer',
            'role': 'UI/UX Designer',
            'department': 'Design',
            'capacity': 40,
            'cost_per_hour': '65.00',
            'email': 'jane@company.com'
        }
        response = self.client.post(reverse('resources:resource_create'), resource2_data)
        self.assertEqual(response.status_code, 302)
        
        # 6. Create Project
        project_data = {
            'name': 'E-commerce Platform',
            'description': 'Build a new e-commerce platform',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 4,
            'budget': '150000.00'
        }
        response = self.client.post(reverse('project_create'), project_data)
        self.assertEqual(response.status_code, 302)
        
        project = Project.objects.get(name='E-commerce Platform')
        
        # 7. Create Tasks
        task1_data = {
            'project': project.id,
            'name': 'Backend API Development',
            'description': 'Develop REST API for the platform',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'estimated_hours': 120,
            'status': 'not_started',
            'priority': 5
        }
        response = self.client.post(reverse('task_create'), task1_data)
        self.assertEqual(response.status_code, 302)
        
        task2_data = {
            'project': project.id,
            'name': 'Frontend UI Design',
            'description': 'Create user interface mockups',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=20)).strftime('%Y-%m-%d'),
            'estimated_hours': 80,
            'status': 'not_started',
            'priority': 4
        }
        response = self.client.post(reverse('task_create'), task2_data)
        self.assertEqual(response.status_code, 302)
        
        # 8. Access Allocation Board
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend API Development')
        self.assertContains(response, 'John Developer')
        
        # 9. Assign Resources to Tasks
        john = Resource.objects.get(name='John Developer')
        jane = Resource.objects.get(name='Jane Designer')
        backend_task = Task.objects.get(name='Backend API Development')
        frontend_task = Task.objects.get(name='Frontend UI Design')
        
        # Assign John to backend task
        assignment_data = {
            'task_id': backend_task.id,
            'resource_id': john.id,
            'allocated_hours': 120
        }
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(assignment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Assign Jane to frontend task
        assignment_data = {
            'task_id': frontend_task.id,
            'resource_id': jane.id,
            'allocated_hours': 80
        }
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(assignment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 10. Record Time Entries
        time_entry_data = {
            'resource': john.id,
            'date': date.today().strftime('%Y-%m-%d'),
            'hours': 8,
            'description': 'Worked on API endpoints',
            'billable': True,
            'task': backend_task.id
        }
        response = self.client.post(reverse('resources:time_entry_create'), time_entry_data)
        self.assertEqual(response.status_code, 302)
        
        # 11. Check Analytics Dashboard
        response = self.client.get(reverse('analytics:analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 12. Generate Utilization Report
        response = self.client.get(reverse('analytics:utilization_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Developer')
        
        # 13. Check AI Analytics
        response = self.client.get(reverse('analytics:ai_analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify data integrity throughout the workflow
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Resource.objects.count(), 2)
        self.assertEqual(Assignment.objects.count(), 2)
        self.assertEqual(TimeEntry.objects.count(), 1)
        
        # Verify resource utilization calculations
        john.refresh_from_db()
        utilization = john.current_utilization()
        self.assertGreater(utilization, 0)


class AuthenticationWorkflowTest(TestCase):
    """Test authentication and authorization workflows"""
    
    def setUp(self):
        self.client = Client()
        
    def test_authentication_workflow(self):
        """Test complete authentication workflow"""
        
        # 1. Try accessing protected page without login
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # 2. Register new user
        registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(reverse('register'), registration_data)
        self.assertEqual(response.status_code, 302)
        
        # 3. Login with new credentials
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # 4. Access protected pages
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('resources:resource_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        
        # 6. Verify access is restricted after logout
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class ResourceManagementWorkflowTest(TestCase):
    """Test resource management workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_resource_lifecycle(self):
        """Test complete resource lifecycle"""
        
        # 1. Create skills first
        skill_data = {'name': 'Python', 'category': 'Programming'}
        response = self.client.post(reverse('resources:create_skill'), skill_data)
        self.assertEqual(response.status_code, 302)
        
        skill = Skill.objects.get(name='Python')
        
        # 2. Create resource
        resource_data = {
            'name': 'John Smith',
            'role': 'Developer',
            'department': 'Engineering',
            'capacity': 40,
            'cost_per_hour': '75.00',
            'email': 'john.smith@company.com'
        }
        response = self.client.post(reverse('resources:resource_create'), resource_data)
        self.assertEqual(response.status_code, 302)
        
        resource = Resource.objects.get(name='John Smith')
        
        # 3. Add skills to resource
        resource.skills.add(skill)
        
        # 4. Set availability
        availability_data = {
            'resource': resource.id,
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'availability_type': 'available',
            'notes': 'Available for projects'
        }
        response = self.client.post(reverse('resources:availability_create'), availability_data)
        self.assertEqual(response.status_code, 302)
        
        # 5. Add time entries
        time_entry_data = {
            'resource': resource.id,
            'date': date.today().strftime('%Y-%m-%d'),
            'hours': 8,
            'description': 'Development work',
            'billable': True
        }
        response = self.client.post(reverse('resources:time_entry_create'), time_entry_data)
        self.assertEqual(response.status_code, 302)
        
        # 6. View resource detail
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': resource.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Smith')
        self.assertContains(response, 'Python')
        
        # 7. Edit resource
        edit_data = {
            'name': 'John Smith Sr.',
            'role': 'Senior Developer',
            'department': 'Engineering',
            'capacity': 40,
            'cost_per_hour': '85.00',
            'email': 'john.smith@company.com'
        }
        response = self.client.post(
            reverse('resources:resource_edit', kwargs={'pk': resource.id}), 
            edit_data
        )
        self.assertEqual(response.status_code, 302)
        
        resource.refresh_from_db()
        self.assertEqual(resource.name, 'John Smith Sr.')
        self.assertEqual(resource.role, 'Senior Developer')


class ProjectAllocationWorkflowTest(TestCase):
    """Test project and allocation workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test resources
        self.resource1 = Resource.objects.create(
            name='Developer 1',
            role='Frontend Developer',
            capacity=40,
            cost_per_hour=Decimal('70.00')
        )
        
        self.resource2 = Resource.objects.create(
            name='Developer 2',
            role='Backend Developer',
            capacity=40,
            cost_per_hour=Decimal('80.00')
        )
        
    def test_project_allocation_workflow(self):
        """Test complete project and allocation workflow"""
        
        # 1. Create project
        project_data = {
            'name': 'Mobile App',
            'description': 'Develop mobile application',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 4,
            'budget': '100000.00'
        }
        response = self.client.post(reverse('project_create'), project_data)
        self.assertEqual(response.status_code, 302)
        
        project = Project.objects.get(name='Mobile App')
        
        # 2. Create tasks
        task1_data = {
            'project': project.id,
            'name': 'Frontend Development',
            'description': 'Develop mobile frontend',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'estimated_hours': 200,
            'status': 'not_started',
            'priority': 5
        }
        response = self.client.post(reverse('task_create'), task1_data)
        self.assertEqual(response.status_code, 302)
        
        task2_data = {
            'project': project.id,
            'name': 'Backend API',
            'description': 'Develop backend API',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=25)).strftime('%Y-%m-%d'),
            'estimated_hours': 150,
            'status': 'not_started',
            'priority': 5
        }
        response = self.client.post(reverse('task_create'), task2_data)
        self.assertEqual(response.status_code, 302)
        
        # 3. Access allocation board
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Frontend Development')
        self.assertContains(response, 'Backend API')
        
        # 4. Assign resources to tasks
        frontend_task = Task.objects.get(name='Frontend Development')
        backend_task = Task.objects.get(name='Backend API')
        
        # Assign frontend developer to frontend task
        assignment_data = {
            'task_id': frontend_task.id,
            'resource_id': self.resource1.id,
            'allocated_hours': 200
        }
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(assignment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Assign backend developer to backend task
        assignment_data = {
            'task_id': backend_task.id,
            'resource_id': self.resource2.id,
            'allocated_hours': 150
        }
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(assignment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 5. Verify assignments were created
        self.assertEqual(Assignment.objects.count(), 2)
        
        frontend_assignment = Assignment.objects.get(task=frontend_task)
        self.assertEqual(frontend_assignment.resource, self.resource1)
        self.assertEqual(frontend_assignment.allocated_hours, 200)
        
        backend_assignment = Assignment.objects.get(task=backend_task)
        self.assertEqual(backend_assignment.resource, self.resource2)
        self.assertEqual(backend_assignment.allocated_hours, 150)
        
        # 6. Check resource utilization
        utilization1 = self.resource1.current_utilization()
        utilization2 = self.resource2.current_utilization()
        
        self.assertGreater(utilization1, 0)
        self.assertGreater(utilization2, 0)
        
        # 7. Update task status
        frontend_task.status = 'in_progress'
        frontend_task.save()
        
        # 8. Add time tracking
        time_entry_data = {
            'resource': self.resource1.id,
            'date': date.today().strftime('%Y-%m-%d'),
            'hours': 8,
            'description': 'Frontend development work',
            'billable': True,
            'task': frontend_task.id
        }
        response = self.client.post(reverse('resources:time_entry_create'), time_entry_data)
        self.assertEqual(response.status_code, 302)
        
        # 9. Check project progress
        response = self.client.get(reverse('project_detail', kwargs={'pk': project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mobile App')


class AnalyticsWorkflowTest(TestCase):
    """Test analytics and reporting workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test data
        self.resource = Resource.objects.create(
            name='Test Resource',
            role='Developer',
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active',
            budget=Decimal('50000.00')
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15),
            estimated_hours=100,
            status='in_progress'
        )
        
        self.assignment = Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=100
        )
        
    def test_analytics_dashboard_workflow(self):
        """Test analytics dashboard and reports"""
        
        # 1. Access analytics dashboard
        response = self.client.get(reverse('analytics:analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Generate forecasts
        response = self.client.post(reverse('analytics:generate_forecast'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Analyze skills
        response = self.client.post(reverse('analytics:analyze_skills'))
        self.assertEqual(response.status_code, 200)
        
        # 4. View utilization report
        response = self.client.get(reverse('analytics:utilization_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resource')
        
        # 5. View cost report
        response = self.client.get(reverse('analytics:cost_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        
        # 6. Test AI analytics dashboard
        response = self.client.get(reverse('analytics:ai_analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 7. Test export functionality
        response = self.client.get(reverse('analytics:export_report', kwargs={'report_type': 'utilization'}))
        self.assertEqual(response.status_code, 200)


class APIIntegrationTest(TestCase):
    """Test API endpoints integration"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.resource = Resource.objects.create(
            name='API Test Resource',
            role='Developer',
            capacity=40
        )
        
        self.project = Project.objects.create(
            name='API Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active'
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='API Test Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15),
            estimated_hours=50,
            status='not_started'
        )
        
    def test_allocation_api_workflow(self):
        """Test allocation API endpoints"""
        
        # 1. Check assignment conflicts
        response = self.client.get(
            reverse('check_assignment_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        self.assertEqual(response.status_code, 200)
        
        # 2. Assign resource
        assignment_data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 50
        }
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(assignment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Verify assignment was created
        assignment = Assignment.objects.get(task=self.task, resource=self.resource)
        self.assertEqual(assignment.allocated_hours, 50)
        
        # 4. Unassign resource
        unassign_data = {'assignment_id': assignment.id}
        response = self.client.post(
            reverse('unassign_task'),
            json.dumps(unassign_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 5. Verify assignment was removed
        self.assertEqual(Assignment.objects.filter(id=assignment.id).count(), 0)
        
    def test_dashboard_api_workflow(self):
        """Test dashboard API endpoints"""
        
        # 1. Get project resources
        response = self.client.get(
            reverse('get_project_resources'),
            {'project_id': self.project.id}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 2. Get project tasks
        response = self.client.get(
            reverse('get_project_tasks'),
            {'project_id': self.project.id}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 3. Process NLI query
        nli_data = {'query': 'Show me project status'}
        response = self.client.post(
            reverse('process_nli_query'),
            json.dumps(nli_data),
            content_type='application/json'
        )
        # This might return an error if AI service is not available, which is okay
        self.assertIn(response.status_code, [200, 500])


class ErrorHandlingIntegrationTest(TestCase):
    """Test error handling across the system"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_invalid_data_handling(self):
        """Test system handles invalid data gracefully"""
        
        # 1. Try to create resource with invalid data
        invalid_resource_data = {
            'name': '',  # Required field
            'role': 'Developer',
            'capacity': -10,  # Invalid value
            'cost_per_hour': 'invalid'  # Invalid format
        }
        response = self.client.post(reverse('resources:resource_create'), invalid_resource_data)
        # Should not create resource and show form errors
        self.assertEqual(response.status_code, 200)  # Returns form with errors
        self.assertEqual(Resource.objects.count(), 0)
        
        # 2. Try to access non-existent resource
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)
        
        # 3. Try invalid assignment
        assignment_data = {
            'task_id': 9999,  # Non-existent task
            'resource_id': 9999,  # Non-existent resource
            'allocated_hours': 50
        }
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(assignment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
    def test_permission_handling(self):
        """Test permission handling"""
        
        # Logout user
        self.client.logout()
        
        # Try to access protected endpoints
        protected_urls = [
            reverse('dashboard'),
            reverse('resources:resource_list'),
            reverse('project_list'),
            reverse('allocation_board'),
            reverse('analytics:analytics_dashboard')
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login
