from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from resources.models import Resource, Skill
from projects.models import Project, Task
from allocation.models import Assignment
from django.contrib.auth.models import User
import json

class AllocationViewTests(TestCase):
    def setUp(self):
        # Create test user and log in
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        # Create resources
        self.resource = Resource.objects.create(
            name='Test Resource',
            role='Developer',
            capacity=40
        )
        
        # Create projects and tasks
        self.project = Project.objects.create(
            name='Test Project',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            status='active'
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=10),
            estimated_hours=20,
            status='not_started'
        )

    def test_allocation_board_view(self):
        """Test the allocation board view loads with resources and tasks"""
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resource')
        self.assertContains(response, 'Test Task')

    def test_assign_resource_api(self):
        """Test the API for assigning resources"""
        data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 20
        }
        
        response = self.client.post(
            reverse('api_assign_resource'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify assignment was created
        assignment = Assignment.objects.get(task=self.task, resource=self.resource)
        self.assertEqual(assignment.allocated_hours, 20)

    def test_remove_assignment_api(self):
        """Test the API for removing assignments"""
        # First create an assignment
        assignment = Assignment.objects.create(
            task=self.task, 
            resource=self.resource,
            allocated_hours=20
        )
        
        data = {
            'assignment_id': assignment.id
        }
        
        response = self.client.post(
            reverse('api_remove_assignment'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify assignment was deleted
        self.assertEqual(Assignment.objects.filter(id=assignment.id).count(), 0)

    def test_check_conflicts_api(self):
        """Test the API for checking conflicts"""
        # Create a skill
        skill = Skill.objects.create(name='Python')
        
        # Add skill requirement to task
        self.task.skills_required.add(skill)
        
        # Check for conflicts (skill mismatch)
        response = self.client.get(
            reverse('api_check_conflicts') + f'?task_id={self.task.id}&resource_id={self.resource.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(any(c['type'] == 'skill_mismatch' for c in response_data['conflicts']))