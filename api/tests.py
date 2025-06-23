from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import json
from decimal import Decimal

from resources.models import Resource, Skill, ResourceSkill
from projects.models import Project, Task
from allocation.models import Assignment


class APIAssignResourceTest(TestCase):
    """Test cases for assign_resource API endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a project manager user
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        
        # Create skills
        self.python_skill = Skill.objects.create(name="Python")
        self.django_skill = Skill.objects.create(name="Django")
        
        # Create a resource
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Software Developer",
            department="Engineering",
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        # Add skills to resource
        ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.python_skill,
            proficiency_level=8
        )
        
        # Create a project
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            manager=self.manager
        )
        
        # Create a task
        self.task = Task.objects.create(
            project=self.project,
            name="Test Task",
            description="A test task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=20,
            status='pending'
        )
        
        self.task.skills_required.add(self.python_skill)
    
    def test_assign_resource_success(self):
        """Test successful resource assignment"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 20
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['assignment']['task_id'], self.task.id)
        self.assertEqual(response_data['assignment']['resource_id'], self.resource.id)
        self.assertEqual(response_data['assignment']['allocated_hours'], 20)
        
        # Verify assignment was created
        assignment = Assignment.objects.get(task=self.task, resource=self.resource)
        self.assertEqual(assignment.allocated_hours, 20)
    
    def test_assign_resource_without_hours(self):
        """Test resource assignment without specifying hours (should use task's estimated hours)"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['assignment']['allocated_hours'], self.task.estimated_hours)
        
        # Verify assignment was created with task's estimated hours
        assignment = Assignment.objects.get(task=self.task, resource=self.resource)
        self.assertEqual(assignment.allocated_hours, self.task.estimated_hours)
    
    def test_assign_resource_update_existing(self):
        """Test updating an existing assignment"""
        # Create an initial assignment
        Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=10
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 25
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['assignment']['allocated_hours'], 25)
        
        # Verify assignment was updated (not duplicated)
        assignments = Assignment.objects.filter(task=self.task, resource=self.resource)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().allocated_hours, 25)
    
    def test_assign_resource_nonexistent_task(self):
        """Test assignment with nonexistent task"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'task_id': 99999,
            'resource_id': self.resource.id,
            'allocated_hours': 20
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_assign_resource_nonexistent_resource(self):
        """Test assignment with nonexistent resource"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'task_id': self.task.id,
            'resource_id': 99999,
            'allocated_hours': 20
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_assign_resource_unauthenticated(self):
        """Test that unauthenticated users cannot assign resources"""
        data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 20
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_assign_resource_get_method_not_allowed(self):
        """Test that GET method is not allowed for assign_resource"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('api_assign_resource'))
        self.assertEqual(response.status_code, 405)  # Method not allowed


class APIRemoveAssignmentTest(TestCase):
    """Test cases for remove_assignment API endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Software Developer",
            department="Engineering",
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            manager=self.manager
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Test Task",
            description="A test task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=20,
            status='pending'
        )
        
        self.assignment = Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=20
        )
    
    def test_remove_assignment_success(self):
        """Test successful assignment removal"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'assignment_id': self.assignment.id
        }
        
        response = self.client.post(
            reverse('api_remove_assignment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['resource_id'], self.resource.id)
        self.assertIn('utilization', response_data)
        
        # Verify assignment was deleted
        self.assertFalse(Assignment.objects.filter(id=self.assignment.id).exists())
    
    def test_remove_assignment_nonexistent(self):
        """Test removal of nonexistent assignment"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'assignment_id': 99999
        }
        
        response = self.client.post(
            reverse('api_remove_assignment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_remove_assignment_unauthenticated(self):
        """Test that unauthenticated users cannot remove assignments"""
        data = {
            'assignment_id': self.assignment.id
        }
        
        response = self.client.post(
            reverse('api_remove_assignment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login


class APICheckConflictsTest(TestCase):
    """Test cases for check_conflicts API endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        
        # Create skills
        self.python_skill = Skill.objects.create(name="Python")
        self.java_skill = Skill.objects.create(name="Java")
        
        # Create a resource with Python skill
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Software Developer",
            department="Engineering",
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.python_skill,
            proficiency_level=8
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            manager=self.manager
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Test Task",
            description="A test task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=20,
            status='pending'
        )
    
    def test_check_conflicts_no_conflicts(self):
        """Test conflict check with no conflicts"""
        self.client.login(username='testuser', password='testpass123')
        self.task.skills_required.add(self.python_skill)
        
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['conflicts']), 0)
        self.assertEqual(response_data['task_name'], self.task.name)
        self.assertEqual(response_data['resource_name'], self.resource.name)
    
    def test_check_conflicts_skill_mismatch(self):
        """Test conflict check with skill mismatch"""
        self.client.login(username='testuser', password='testpass123')
        self.task.skills_required.add(self.java_skill)  # Resource doesn't have Java
        
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['conflicts']), 1)
        
        conflict = response_data['conflicts'][0]
        self.assertEqual(conflict['type'], 'skill_mismatch')
        self.assertIn('Java', conflict['message'])
    
    def test_check_conflicts_multiple_missing_skills(self):
        """Test conflict check with multiple missing skills"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add another skill that resource doesn't have
        go_skill = Skill.objects.create(name="Go")
        self.task.skills_required.add(self.java_skill, go_skill)
        
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['conflicts']), 1)
        
        conflict = response_data['conflicts'][0]
        self.assertEqual(conflict['type'], 'skill_mismatch')
        self.assertIn('Java', conflict['message'])
        self.assertIn('Go', conflict['message'])
    
    def test_check_conflicts_dependency_conflict(self):
        """Test conflict check with dependency conflicts"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a dependency task that's not completed
        dependency_task = Task.objects.create(
            project=self.project,
            name="Dependency Task",
            description="A dependency task",
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=2),  # Ends after main task starts
            estimated_hours=10,
            status='in_progress'
        )
        
        self.task.dependencies.add(dependency_task)
        
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        conflicts = [c for c in response_data['conflicts'] if c['type'] == 'dependency_conflict']
        self.assertEqual(len(conflicts), 1)
        
        conflict = conflicts[0]
        self.assertEqual(conflict['type'], 'dependency_conflict')
        self.assertIn('Dependency Task', conflict['message'])
    
    def test_check_conflicts_nonexistent_task(self):
        """Test conflict check with nonexistent task"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': 99999, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_check_conflicts_nonexistent_resource(self):
        """Test conflict check with nonexistent resource"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': 99999}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_check_conflicts_unauthenticated(self):
        """Test that unauthenticated users cannot check conflicts"""
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login


class APIURLsTest(TestCase):
    """Test cases for API URL routing"""
    
    def test_assign_resource_url_resolves(self):
        """Test that assign resource URL resolves correctly"""
        url = reverse('api_assign_resource')
        self.assertEqual(url, '/api/assign-resource/')
    
    def test_remove_assignment_url_resolves(self):
        """Test that remove assignment URL resolves correctly"""
        url = reverse('api_remove_assignment')
        self.assertEqual(url, '/api/remove-assignment/')
    
    def test_check_conflicts_url_resolves(self):
        """Test that check conflicts URL resolves correctly"""
        url = reverse('api_check_conflicts')
        self.assertEqual(url, '/api/check-conflicts/')


class APIIntegrationTest(TestCase):
    """Integration tests for API functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        
        self.skill = Skill.objects.create(name="Python")
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Software Developer",
            department="Engineering",
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.skill,
            proficiency_level=8
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            manager=self.manager
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Test Task",
            description="A test task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=20,
            status='pending'
        )
        
        self.task.skills_required.add(self.skill)
    
    def test_full_assignment_workflow(self):
        """Test complete assignment workflow: check conflicts -> assign -> remove"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Check for conflicts first
        response = self.client.get(
            reverse('api_check_conflicts'),
            {'task_id': self.task.id, 'resource_id': self.resource.id}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['conflicts']), 0)  # No conflicts
        
        # 2. Assign the resource
        assign_data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 20
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            data=json.dumps(assign_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        assignment_id = response_data['assignment']['id']
        
        # Verify assignment exists
        self.assertTrue(Assignment.objects.filter(id=assignment_id).exists())
        
        # 3. Remove the assignment
        remove_data = {
            'assignment_id': assignment_id
        }
        
        response = self.client.post(
            reverse('api_remove_assignment'),
            data=json.dumps(remove_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify assignment was removed
        self.assertFalse(Assignment.objects.filter(id=assignment_id).exists())
