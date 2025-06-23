from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from datetime import date, timedelta
from decimal import Decimal

from .models import Assignment
from resources.models import Resource, Skill
from projects.models import Project, Task


class AssignmentModelTest(TestCase):
    """Test cases for Assignment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Developer",
            role="Software Developer",
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Development Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=40
        )
        
        self.assignment = Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=40,
            notes="Full-time assignment for development"
        )
    
    def test_assignment_creation(self):
        """Test assignment creation and basic properties"""
        self.assertEqual(self.assignment.resource, self.resource)
        self.assertEqual(self.assignment.task, self.task)
        self.assertEqual(self.assignment.allocated_hours, 40)
        self.assertEqual(self.assignment.notes, "Full-time assignment for development")
        
        expected_str = f"{self.resource.name} assigned to {self.task.name}"
        self.assertEqual(str(self.assignment), expected_str)
    
    def test_assignment_unique_constraint(self):
        """Test unique constraint on resource-task combination"""
        with self.assertRaises(IntegrityError):
            Assignment.objects.create(
                resource=self.resource,
                task=self.task,
                allocated_hours=20
            )
    
    def test_assignment_relationships(self):
        """Test assignment relationships with resource and task"""
        # Test forward relationships
        self.assertEqual(self.assignment.resource, self.resource)
        self.assertEqual(self.assignment.task, self.task)
        
        # Test reverse relationships
        resource_assignments = self.resource.assignments.all()
        self.assertIn(self.assignment, resource_assignments)
        
        task_assignments = self.task.assignments.all()
        self.assertIn(self.assignment, task_assignments)
    
    def test_assignment_with_null_notes(self):
        """Test assignment creation with null notes"""
        task2 = Task.objects.create(
            project=self.project,
            name="Another Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        assignment = Assignment.objects.create(
            resource=self.resource,
            task=task2,
            allocated_hours=20
        )
        
        self.assertIsNone(assignment.notes)
    
    def test_assignment_timestamps(self):
        """Test assignment created_at and updated_at timestamps"""
        self.assertIsNotNone(self.assignment.created_at)
        self.assertIsNotNone(self.assignment.updated_at)
        
        # Update assignment and check if updated_at changes
        original_updated_at = self.assignment.updated_at
        self.assignment.allocated_hours = 35
        self.assignment.save()
        
        self.assignment.refresh_from_db()
        self.assertGreater(self.assignment.updated_at, original_updated_at)


class AssignmentManagerTest(TestCase):
    """Test cases for Assignment model manager and queryset operations"""
    
    def setUp(self):
        # Create multiple resources
        self.developer1 = Resource.objects.create(
            name="Developer One",
            role="Senior Developer",
            cost_per_hour=Decimal('90.00')
        )
        
        self.developer2 = Resource.objects.create(
            name="Developer Two",
            role="Junior Developer",
            cost_per_hour=Decimal('60.00')
        )
        
        self.designer = Resource.objects.create(
            name="Designer",
            role="UI/UX Designer",
            cost_per_hour=Decimal('70.00')
        )
        
        # Create projects and tasks
        self.project1 = Project.objects.create(
            name="Project Alpha",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60)
        )
        
        self.project2 = Project.objects.create(
            name="Project Beta",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=90)
        )
        
        self.task1 = Task.objects.create(
            project=self.project1,
            name="Backend Development",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            estimated_hours=120
        )
        
        self.task2 = Task.objects.create(
            project=self.project1,
            name="Frontend Development",
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=45),
            estimated_hours=100
        )
        
        self.task3 = Task.objects.create(
            project=self.project2,
            name="UI Design",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=50),
            estimated_hours=80
        )
        
        # Create assignments
        Assignment.objects.create(
            resource=self.developer1,
            task=self.task1,
            allocated_hours=120
        )
        
        Assignment.objects.create(
            resource=self.developer2,
            task=self.task2,
            allocated_hours=100
        )
        
        Assignment.objects.create(
            resource=self.designer,
            task=self.task3,
            allocated_hours=80
        )
    
    def test_assignment_filtering_by_resource(self):
        """Test filtering assignments by resource"""
        developer1_assignments = Assignment.objects.filter(resource=self.developer1)
        self.assertEqual(developer1_assignments.count(), 1)
        self.assertEqual(developer1_assignments.first().task, self.task1)
        
        developer2_assignments = Assignment.objects.filter(resource=self.developer2)
        self.assertEqual(developer2_assignments.count(), 1)
        self.assertEqual(developer2_assignments.first().task, self.task2)
    
    def test_assignment_filtering_by_project(self):
        """Test filtering assignments by project"""
        project1_assignments = Assignment.objects.filter(task__project=self.project1)
        self.assertEqual(project1_assignments.count(), 2)
        
        project2_assignments = Assignment.objects.filter(task__project=self.project2)
        self.assertEqual(project2_assignments.count(), 1)
    
    def test_assignment_total_allocated_hours(self):
        """Test calculating total allocated hours"""
        total_hours = sum(
            assignment.allocated_hours 
            for assignment in Assignment.objects.all()
        )
        self.assertEqual(total_hours, 300)  # 120 + 100 + 80
    
    def test_assignment_by_role(self):
        """Test filtering assignments by resource role"""
        developer_assignments = Assignment.objects.filter(
            resource__role__icontains='Developer'
        )
        self.assertEqual(developer_assignments.count(), 2)
        
        designer_assignments = Assignment.objects.filter(
            resource__role__icontains='Designer'
        )
        self.assertEqual(designer_assignments.count(), 1)


class AssignmentValidationTest(TestCase):
    """Test cases for Assignment model validations and business rules"""
    
    def setUp(self):
        self.resource = Resource.objects.create(
            name="Test Resource",
            role="Developer",
            capacity=40  # 40 hours per week
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
            end_date=date.today() + timedelta(days=10),
            estimated_hours=80
        )
    
    def test_assignment_over_allocation_detection(self):
        """Test detecting over-allocation scenarios"""
        # Create an assignment with hours exceeding task estimate
        assignment = Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=100  # More than task's 80 estimated hours
        )
        
        # This should be allowed at model level, but can be caught by business logic
        self.assertEqual(assignment.allocated_hours, 100)
        self.assertGreater(assignment.allocated_hours, self.task.estimated_hours)
    
    def test_multiple_assignments_same_period(self):
        """Test resource assigned to multiple tasks in same period"""
        task2 = Task.objects.create(
            project=self.project,
            name="Concurrent Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=40
        )
        
        Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=40
        )
        
        Assignment.objects.create(
            resource=self.resource,
            task=task2,
            allocated_hours=40
        )
        
        # Resource now has 80 hours allocated during overlapping period
        total_allocated = sum(
            assignment.allocated_hours 
            for assignment in self.resource.assignments.all()
        )
        self.assertEqual(total_allocated, 80)
    
    def test_assignment_to_completed_task(self):
        """Test assignment to a completed task"""
        self.task.status = 'completed'
        self.task.save()
        
        # Model allows this, but business logic should prevent it
        assignment = Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=20
        )
        
        self.assertEqual(assignment.task.status, 'completed')


class AssignmentViewsTest(TestCase):
    """Test cases for Assignment views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Developer",
            role="Software Developer"
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
            end_date=date.today() + timedelta(days=10),
            estimated_hours=40
        )
        
        self.assignment = Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=40
        )
        
        self.client.force_login(self.user)
    
    def test_assignment_list_view(self):
        """Test assignment list view"""
        response = self.client.get('/allocation/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.resource.name)
        self.assertContains(response, self.task.name)
    
    def test_assignment_detail_view(self):
        """Test assignment detail view"""
        response = self.client.get(f'/allocation/{self.assignment.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.resource.name)
        self.assertContains(response, self.task.name)
    
    def test_assignment_create_view_get(self):
        """Test assignment create view GET request"""
        response = self.client.get('/allocation/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_assignment_create_view_post(self):
        """Test assignment create view POST request"""
        # Create another task for new assignment
        task2 = Task.objects.create(
            project=self.project,
            name="Another Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        data = {
            'resource': self.resource.id,
            'task': task2.id,
            'allocated_hours': 20,
            'notes': 'Test assignment creation'
        }
        
        response = self.client.post('/allocation/create/', data)
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if assignment was created
        new_assignment = Assignment.objects.filter(task=task2).first()
        self.assertIsNotNone(new_assignment)
        self.assertEqual(new_assignment.allocated_hours, 20)
    
    def test_assignment_update_view(self):
        """Test assignment update view"""
        update_data = {
            'resource': self.resource.id,
            'task': self.task.id,
            'allocated_hours': 30,
            'notes': 'Updated assignment'
        }
        
        response = self.client.post(f'/allocation/{self.assignment.id}/edit/', update_data)
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check if assignment was updated
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.allocated_hours, 30)
        self.assertEqual(self.assignment.notes, 'Updated assignment')
    
    def test_assignment_delete_view(self):
        """Test assignment delete view"""
        assignment_id = self.assignment.id
        
        response = self.client.post(f'/allocation/{assignment_id}/delete/')
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        
        # Check if assignment was deleted
        with self.assertRaises(Assignment.DoesNotExist):
            Assignment.objects.get(id=assignment_id)


class AssignmentIntegrationTest(TestCase):
    """Integration tests for Assignment functionality"""
    
    def setUp(self):
        # Create users
        self.manager = User.objects.create_user(
            username='manager',
            password='testpass123'
        )
        
        self.dev_user = User.objects.create_user(
            username='developer',
            password='testpass123'
        )
        
        # Create skills
        self.python_skill = Skill.objects.create(name="Python")
        self.react_skill = Skill.objects.create(name="React")
        
        # Create resources
        self.developer = Resource.objects.create(
            user=self.dev_user,
            name="Senior Developer",
            role="Software Developer",
            capacity=40,
            cost_per_hour=Decimal('85.00')
        )
        
        self.frontend_dev = Resource.objects.create(
            name="Frontend Developer",
            role="Frontend Developer",
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        # Create project
        self.project = Project.objects.create(
            name="E-commerce Platform",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            manager=self.manager,
            budget=Decimal('50000.00')
        )
    
    def test_complete_allocation_workflow(self):
        """Test complete allocation workflow"""
        # Create tasks with skill requirements
        backend_task = Task.objects.create(
            project=self.project,
            name="Backend API Development",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            estimated_hours=120
        )
        backend_task.skills_required.add(self.python_skill)
        
        frontend_task = Task.objects.create(
            project=self.project,
            name="Frontend Development",
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=60),
            estimated_hours=100
        )
        frontend_task.skills_required.add(self.react_skill)
        
        # Create assignments
        backend_assignment = Assignment.objects.create(
            resource=self.developer,
            task=backend_task,
            allocated_hours=120,
            notes="Backend development with Python/Django"
        )
        
        frontend_assignment = Assignment.objects.create(
            resource=self.frontend_dev,
            task=frontend_task,
            allocated_hours=100,
            notes="React frontend development"
        )
        
        # Test assignment relationships
        self.assertEqual(self.project.get_all_assignments().count(), 2)
        self.assertIn(backend_assignment, self.project.get_all_assignments())
        self.assertIn(frontend_assignment, self.project.get_all_assignments())
        
        # Test resource allocation
        dev_assignments = self.developer.assignments.all()
        self.assertEqual(dev_assignments.count(), 1)
        self.assertEqual(dev_assignments.first().task, backend_task)
        
        # Test task assignment status
        self.assertTrue(backend_task.is_assigned)
        self.assertTrue(frontend_task.is_assigned)
        
        # Test cost calculations
        estimated_cost = self.project.get_estimated_cost()
        expected_cost = (120 * Decimal('85.00')) + (100 * Decimal('75.00'))
        self.assertEqual(estimated_cost, expected_cost)
    
    def test_resource_capacity_tracking(self):
        """Test resource capacity and allocation tracking"""
        # Create multiple tasks for same resource
        task1 = Task.objects.create(
            project=self.project,
            name="Task 1",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=60
        )
        
        task2 = Task.objects.create(
            project=self.project,
            name="Task 2",
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=15),
            estimated_hours=40
        )
        
        # Assign both tasks to same resource
        Assignment.objects.create(
            resource=self.developer,
            task=task1,
            allocated_hours=60
        )
        
        Assignment.objects.create(
            resource=self.developer,
            task=task2,
            allocated_hours=40
        )
        
        # Calculate total allocation for resource
        total_allocated = sum(
            assignment.allocated_hours 
            for assignment in self.developer.assignments.all()
        )
        self.assertEqual(total_allocated, 100)
        
        # Check if resource is over-allocated (assuming 2 weeks = 80 hours capacity)
        # This is a business logic check that would be implemented in views/services
        weekly_capacity = self.developer.capacity  # 40 hours per week
        two_week_capacity = weekly_capacity * 2  # 80 hours
        self.assertGreater(total_allocated, two_week_capacity)
    
    def test_assignment_modification_tracking(self):
        """Test tracking of assignment modifications"""
        task = Task.objects.create(
            project=self.project,
            name="Modifiable Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=40
        )
        
        assignment = Assignment.objects.create(
            resource=self.developer,
            task=task,
            allocated_hours=40
        )
        
        original_created_at = assignment.created_at
        original_updated_at = assignment.updated_at
        
        # Modify assignment
        assignment.allocated_hours = 50
        assignment.notes = "Increased scope"
        assignment.save()
        
        assignment.refresh_from_db()
        
        # Check timestamps
        self.assertEqual(assignment.created_at, original_created_at)
        self.assertGreater(assignment.updated_at, original_updated_at)
        self.assertEqual(assignment.allocated_hours, 50)
        self.assertEqual(assignment.notes, "Increased scope")
