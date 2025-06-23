"""
Edge case and boundary condition tests for ResourcePro
Tests unusual scenarios and error conditions
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta, date
from decimal import Decimal, InvalidOperation
import uuid

from resources.models import Resource, Skill, TimeEntry, Availability
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import (
    ResourceDemandForecast, HistoricalUtilization, 
    SkillDemandAnalysis, ProjectCostTracking
)


class DataValidationEdgeCases(TestCase):
    """Test edge cases in data validation"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='edgetest',
            email='edge@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_extreme_date_ranges(self):
        """Test with extreme date ranges"""
        print("Testing extreme date ranges...")
        
        # Test far future dates
        far_future_project_data = {
            'name': 'Far Future Project',
            'description': 'Project scheduled for far in the future',
            'start_date': '2050-01-01',
            'end_date': '2051-12-31',
            'status': 'planning',
            'priority': 3,
            'budget': '100000.00'
        }
        
        response = self.client.post(reverse('project_create'), far_future_project_data)
        self.assertEqual(response.status_code, 302)  # Should succeed
        
        project = Project.objects.get(name='Far Future Project')
        self.assertEqual(project.start_date.year, 2050)
        
        # Test very short duration
        same_day_project_data = {
            'name': 'Same Day Project',
            'description': 'Project that starts and ends on the same day',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': date.today().strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 3,
            'budget': '1000.00'
        }
        
        response = self.client.post(reverse('project_create'), same_day_project_data)
        self.assertEqual(response.status_code, 302)
        
        # Test historical dates
        historical_project_data = {
            'name': 'Historical Project',
            'description': 'Project from the past',
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'status': 'completed',
            'priority': 3,
            'budget': '75000.00'
        }
        
        response = self.client.post(reverse('project_create'), historical_project_data)
        self.assertEqual(response.status_code, 302)
        
    def test_extreme_numeric_values(self):
        """Test with extreme numeric values"""
        print("Testing extreme numeric values...")
        
        # Test very high budget
        high_budget_project_data = {
            'name': 'Billion Dollar Project',
            'description': 'Project with extremely high budget',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 5,
            'budget': '999999999.99'  # Near maximum decimal value
        }
        
        response = self.client.post(reverse('project_create'), high_budget_project_data)
        self.assertEqual(response.status_code, 302)
        
        # Test zero budget
        zero_budget_project_data = {
            'name': 'Zero Budget Project',
            'description': 'Project with no budget',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 1,
            'budget': '0.00'
        }
        
        response = self.client.post(reverse('project_create'), zero_budget_project_data)
        self.assertEqual(response.status_code, 302)
        
        # Test very high capacity resource
        high_capacity_resource_data = {
            'name': 'Workaholic Resource',
            'role': 'Overtime Champion',
            'department': 'Extreme',
            'capacity': 168,  # 24 hours * 7 days
            'cost_per_hour': '999.99',
            'email': 'workaholic@company.com'
        }
        
        response = self.client.post(reverse('resources:resource_create'), high_capacity_resource_data)
        self.assertEqual(response.status_code, 302)
        
        # Test zero capacity resource
        zero_capacity_resource_data = {
            'name': 'Inactive Resource',
            'role': 'Consultant',
            'department': 'External',
            'capacity': 0,
            'cost_per_hour': '100.00',
            'email': 'inactive@company.com'
        }
        
        response = self.client.post(reverse('resources:resource_create'), zero_capacity_resource_data)
        self.assertEqual(response.status_code, 302)
        
    def test_unicode_and_special_characters(self):
        """Test with Unicode and special characters"""
        print("Testing Unicode and special characters...")
        
        # Test Unicode characters
        unicode_project_data = {
            'name': 'Проект Юникод 测试项目 🚀',
            'description': 'Project with Unicode: αβγ δε ζη θι κλ μν ξο πρ στ υφ χψ ω',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 3,
            'budget': '50000.00'
        }
        
        response = self.client.post(reverse('project_create'), unicode_project_data)
        self.assertEqual(response.status_code, 302)
        
        project = Project.objects.get(name__contains='Проект')
        self.assertIn('🚀', project.name)
        
        # Test special characters in resource names
        special_char_resource_data = {
            'name': "O'Connor-Smith, Jr. & Co.",
            'role': 'Special Characters Expert',
            'department': 'R&D',
            'capacity': 40,
            'cost_per_hour': '75.00',
            'email': 'special.chars+test@company.com'
        }
        
        response = self.client.post(reverse('resources:resource_create'), special_char_resource_data)
        self.assertEqual(response.status_code, 302)
        
    def test_extremely_long_text_fields(self):
        """Test with extremely long text inputs"""
        print("Testing extremely long text fields...")
        
        # Create very long description
        long_description = "A" * 5000  # 5000 character description
        
        long_text_project_data = {
            'name': 'Long Description Project',
            'description': long_description,
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 3,
            'budget': '50000.00'
        }
        
        response = self.client.post(reverse('project_create'), long_text_project_data)
        # Should either succeed or gracefully handle the long text
        self.assertIn(response.status_code, [200, 302])
        
        # Test very long task name (near database limit)
        if response.status_code == 302:
            project = Project.objects.get(name='Long Description Project')
            
            long_task_name = "B" * 200  # 200 character task name
            long_task_data = {
                'project': project.id,
                'name': long_task_name,
                'description': 'Task with very long name',
                'start_date': date.today().strftime('%Y-%m-%d'),
                'end_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'estimated_hours': 40,
                'status': 'not_started',
                'priority': 3
            }
            
            response = self.client.post(reverse('task_create'), long_task_data)
            self.assertIn(response.status_code, [200, 302])


class BoundaryConditionTests(TestCase):
    """Test boundary conditions and limits"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='boundarytest',
            email='boundary@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create base test data
        self.resource = Resource.objects.create(
            name='Boundary Test Resource',
            role='Tester',
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        self.project = Project.objects.create(
            name='Boundary Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active',
            budget=Decimal('50000.00')
        )
        
    def test_over_allocation_boundaries(self):
        """Test resource over-allocation boundary conditions"""
        print("Testing over-allocation boundaries...")
        
        # Create task requiring more hours than resource capacity
        over_allocated_task = Task.objects.create(
            project=self.project,
            name='Over-allocation Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=400,  # 10x normal capacity
            status='not_started'
        )
        
        # Try to assign over-allocated task
        assignment_data = {
            'task_id': over_allocated_task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 400
        }
        
        response = self.client.post(
            reverse('assign_task'),
            assignment_data,
            content_type='application/json'
        )
        
        # System should handle over-allocation gracefully
        self.assertIn(response.status_code, [200, 400])
        
        if response.status_code == 200:
            # If assignment succeeds, check utilization calculation
            utilization = self.resource.current_utilization()
            self.assertGreater(utilization, 100)  # Should show over-allocation
            
    def test_time_entry_boundaries(self):
        """Test time entry boundary conditions"""
        print("Testing time entry boundaries...")
        
        # Test negative hours (should fail)
        negative_hours_data = {
            'resource': self.resource.id,
            'date': date.today().strftime('%Y-%m-%d'),
            'hours': -8,
            'description': 'Negative hours test',
            'billable': True
        }
        
        response = self.client.post(reverse('resources:time_entry_create'), negative_hours_data)
        self.assertEqual(response.status_code, 200)  # Should return form with errors
        
        # Test extremely high hours (24+ hours in a day)
        extreme_hours_data = {
            'resource': self.resource.id,
            'date': date.today().strftime('%Y-%m-%d'),
            'hours': 48,  # 48 hours in one day
            'description': 'Extreme hours test',
            'billable': True
        }
        
        response = self.client.post(reverse('resources:time_entry_create'), extreme_hours_data)
        # Should either succeed with warning or gracefully handle
        self.assertIn(response.status_code, [200, 302])
        
        # Test zero hours
        zero_hours_data = {
            'resource': self.resource.id,
            'date': date.today().strftime('%Y-%m-%d'),
            'hours': 0,
            'description': 'Zero hours test',
            'billable': False
        }
        
        response = self.client.post(reverse('resources:time_entry_create'), zero_hours_data)
        self.assertIn(response.status_code, [200, 302])
        
    def test_priority_boundaries(self):
        """Test priority value boundaries"""
        print("Testing priority boundaries...")
        
        # Test maximum priority
        max_priority_task_data = {
            'project': self.project.id,
            'name': 'Maximum Priority Task',
            'description': 'Task with highest priority',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estimated_hours': 40,
            'status': 'not_started',
            'priority': 10  # Assuming 1-10 scale
        }
        
        response = self.client.post(reverse('task_create'), max_priority_task_data)
        self.assertIn(response.status_code, [200, 302])
        
        # Test minimum priority
        min_priority_task_data = {
            'project': self.project.id,
            'name': 'Minimum Priority Task',
            'description': 'Task with lowest priority',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estimated_hours': 40,
            'status': 'not_started',
            'priority': 1
        }
        
        response = self.client.post(reverse('task_create'), min_priority_task_data)
        self.assertIn(response.status_code, [200, 302])
        
    def test_date_boundary_conditions(self):
        """Test date boundary conditions"""
        print("Testing date boundary conditions...")
        
        # Test task ending before it starts
        invalid_date_task_data = {
            'project': self.project.id,
            'name': 'Invalid Date Task',
            'description': 'Task ending before it starts',
            'start_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'end_date': date.today().strftime('%Y-%m-%d'),
            'estimated_hours': 40,
            'status': 'not_started',
            'priority': 3
        }
        
        response = self.client.post(reverse('task_create'), invalid_date_task_data)
        self.assertEqual(response.status_code, 200)  # Should return form with errors
        
        # Test weekend dates
        # Find next Saturday
        next_saturday = date.today()
        while next_saturday.weekday() != 5:  # Saturday is 5
            next_saturday += timedelta(days=1)
            
        weekend_task_data = {
            'project': self.project.id,
            'name': 'Weekend Task',
            'description': 'Task scheduled on weekend',
            'start_date': next_saturday.strftime('%Y-%m-%d'),
            'end_date': (next_saturday + timedelta(days=2)).strftime('%Y-%m-%d'),
            'estimated_hours': 16,
            'status': 'not_started',
            'priority': 3
        }
        
        response = self.client.post(reverse('task_create'), weekend_task_data)
        self.assertEqual(response.status_code, 302)  # Should succeed


class ConcurrencyEdgeCases(TestCase):
    """Test edge cases related to concurrent operations"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='concurrencytest',
            email='concurrency@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.resource = Resource.objects.create(
            name='Concurrency Test Resource',
            role='Tester',
            capacity=40
        )
        
        self.project = Project.objects.create(
            name='Concurrency Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active'
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Concurrency Test Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=40,
            status='not_started'
        )
        
    def test_duplicate_assignment_prevention(self):
        """Test prevention of duplicate assignments"""
        print("Testing duplicate assignment prevention...")
        
        # Create first assignment
        assignment_data = {
            'task_id': self.task.id,
            'resource_id': self.resource.id,
            'allocated_hours': 40
        }
        
        response1 = self.client.post(
            reverse('assign_task'),
            assignment_data,
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # Try to create duplicate assignment
        response2 = self.client.post(
            reverse('assign_task'),
            assignment_data,
            content_type='application/json'
        )
        
        # Should either prevent duplicate or handle gracefully
        self.assertIn(response2.status_code, [200, 400])
        
        # Verify only one assignment exists
        assignment_count = Assignment.objects.filter(
            task=self.task,
            resource=self.resource
        ).count()
        
        self.assertLessEqual(assignment_count, 1, "Should not create duplicate assignments")
        
    def test_deleted_object_references(self):
        """Test handling of references to deleted objects"""
        print("Testing deleted object references...")
        
        # Create assignment
        assignment = Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=40
        )
        
        # Delete the task
        task_id = self.task.id
        self.task.delete()
        
        # Try to access assignment (should handle gracefully)
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        
        # Try to unassign non-existent task
        unassign_data = {'assignment_id': assignment.id}
        response = self.client.post(
            reverse('unassign_task'),
            unassign_data,
            content_type='application/json'
        )
        
        # Should handle missing task gracefully
        self.assertIn(response.status_code, [200, 404])


class DataConsistencyEdgeCases(TestCase):
    """Test data consistency edge cases"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='consistencytest',
            email='consistency@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_orphaned_assignments(self):
        """Test handling of orphaned assignments"""
        print("Testing orphaned assignments...")
        
        # Create complete setup
        resource = Resource.objects.create(
            name='Consistency Resource',
            role='Tester',
            capacity=40
        )
        
        project = Project.objects.create(
            name='Consistency Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active'
        )
        
        task = Task.objects.create(
            project=project,
            name='Consistency Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=40,
            status='not_started'
        )
        
        assignment = Assignment.objects.create(
            task=task,
            resource=resource,
            allocated_hours=40
        )
        
        # Delete project (should cascade to task and assignment)
        project.delete()
        
        # Verify assignment was also deleted (cascaded)
        self.assertEqual(
            Assignment.objects.filter(id=assignment.id).count(),
            0,
            "Assignment should be deleted when project is deleted"
        )
        
        # Verify resource still exists
        self.assertTrue(
            Resource.objects.filter(id=resource.id).exists(),
            "Resource should not be deleted when project is deleted"
        )
        
    def test_circular_dependencies(self):
        """Test handling of potential circular dependencies"""
        print("Testing circular dependencies...")
        
        # Create skills that could potentially have circular references
        skill1 = Skill.objects.create(name='Skill A', category='Category 1')
        skill2 = Skill.objects.create(name='Skill B', category='Category 2')
        
        # Create resource with both skills
        resource = Resource.objects.create(
            name='Multi-skilled Resource',
            role='Generalist',
            capacity=40
        )
        resource.skills.add(skill1, skill2)
        
        # Create tasks requiring different combinations of skills
        project = Project.objects.create(
            name='Multi-skill Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active'
        )
        
        task1 = Task.objects.create(
            project=project,
            name='Task requiring Skill A',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=40,
            status='not_started'
        )
        task1.skills_required.add(skill1)
        
        task2 = Task.objects.create(
            project=project,
            name='Task requiring Skill B',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            estimated_hours=40,
            status='not_started'
        )
        task2.skills_required.add(skill2)
        
        # Assign both tasks to same resource
        Assignment.objects.create(task=task1, resource=resource, allocated_hours=40)
        Assignment.objects.create(task=task2, resource=resource, allocated_hours=40)
        
        # Test that utilization calculation handles this correctly
        utilization = resource.current_utilization()
        self.assertGreater(utilization, 0)
        self.assertIsInstance(utilization, (int, float))
        
    def test_data_integrity_after_bulk_operations(self):
        """Test data integrity after bulk operations"""
        print("Testing data integrity after bulk operations...")
        
        # Create test data
        resources = []
        for i in range(10):
            resources.append(Resource(
                name=f'Bulk Resource {i}',
                role='Bulk Tester',
                capacity=40,
                cost_per_hour=Decimal('75.00')
            ))
        Resource.objects.bulk_create(resources)
        
        projects = []
        for i in range(5):
            projects.append(Project(
                name=f'Bulk Project {i}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                status='active',
                budget=Decimal('50000.00')
            ))
        Project.objects.bulk_create(projects)
        
        # Create tasks for each project
        tasks = []
        for project in Project.objects.filter(name__startswith='Bulk Project'):
            for j in range(3):
                tasks.append(Task(
                    project=project,
                    name=f'Bulk Task {j} - {project.name}',
                    start_date=project.start_date,
                    end_date=project.end_date,
                    estimated_hours=40,
                    status='not_started'
                ))
        Task.objects.bulk_create(tasks)
        
        # Verify data integrity
        total_projects = Project.objects.filter(name__startswith='Bulk Project').count()
        total_tasks = Task.objects.filter(name__startswith='Bulk Task').count()
        total_resources = Resource.objects.filter(name__startswith='Bulk Resource').count()
        
        self.assertEqual(total_projects, 5)
        self.assertEqual(total_tasks, 15)  # 5 projects * 3 tasks each
        self.assertEqual(total_resources, 10)
        
        # Test that all relationships are properly established
        for project in Project.objects.filter(name__startswith='Bulk Project'):
            self.assertEqual(project.tasks.count(), 3)
            
        # Test bulk deletion
        Project.objects.filter(name__startswith='Bulk Project').delete()
        
        # Verify cascaded deletion
        remaining_tasks = Task.objects.filter(name__startswith='Bulk Task').count()
        self.assertEqual(remaining_tasks, 0, "Tasks should be deleted when projects are deleted")
        
        # Verify resources are not affected
        remaining_resources = Resource.objects.filter(name__startswith='Bulk Resource').count()
        self.assertEqual(remaining_resources, 10, "Resources should not be affected by project deletion")


class APIEdgeCases(TestCase):
    """Test API edge cases and malformed requests"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='apitest',
            email='api@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.resource = Resource.objects.create(
            name='API Test Resource',
            role='Tester',
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
            end_date=date.today() + timedelta(days=7),
            estimated_hours=40,
            status='not_started'
        )
        
    def test_malformed_json_requests(self):
        """Test handling of malformed JSON requests"""
        print("Testing malformed JSON requests...")
        
        # Test invalid JSON
        response = self.client.post(
            reverse('assign_task'),
            'invalid json data',
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 500])
        
        # Test empty JSON
        response = self.client.post(
            reverse('assign_task'),
            '{}',
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 404])
        
        # Test JSON with wrong data types
        invalid_data = {
            'task_id': 'not_a_number',
            'resource_id': self.resource.id,
            'allocated_hours': 'not_a_number'
        }
        
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 404, 500])
        
    def test_missing_required_fields(self):
        """Test handling of requests with missing required fields"""
        print("Testing missing required fields...")
        
        # Test assignment with missing task_id
        incomplete_data = {
            'resource_id': self.resource.id,
            'allocated_hours': 40
        }
        
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(incomplete_data),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 404])
        
        # Test assignment with missing resource_id
        incomplete_data = {
            'task_id': self.task.id,
            'allocated_hours': 40
        }
        
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(incomplete_data),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 404])
        
    def test_non_existent_ids(self):
        """Test handling of requests with non-existent IDs"""
        print("Testing non-existent IDs...")
        
        # Test assignment with non-existent task ID
        invalid_data = {
            'task_id': 99999,
            'resource_id': self.resource.id,
            'allocated_hours': 40
        }
        
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # Test assignment with non-existent resource ID
        invalid_data = {
            'task_id': self.task.id,
            'resource_id': 99999,
            'allocated_hours': 40
        }
        
        response = self.client.post(
            reverse('assign_task'),
            json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
    def test_sql_injection_attempts(self):
        """Test protection against SQL injection attempts"""
        print("Testing SQL injection protection...")
        
        # Test SQL injection in search parameters
        malicious_queries = [
            "'; DROP TABLE resources_resource; --",
            "1' OR '1'='1",
            "1; DELETE FROM resources_resource WHERE 1=1; --",
            "<script>alert('xss')</script>",
            "1 UNION SELECT * FROM auth_user --"
        ]
        
        for malicious_query in malicious_queries:
            # Test in various endpoints that might accept search parameters
            response = self.client.get(
                reverse('resources:resource_list'),
                {'search': malicious_query}
            )
            # Should not crash or expose data
            self.assertEqual(response.status_code, 200)
            
            response = self.client.get(
                reverse('project_list'),
                {'search': malicious_query}
            )
            self.assertEqual(response.status_code, 200)
            
        # Verify that resources still exist (not deleted by injection)
        self.assertTrue(
            Resource.objects.filter(id=self.resource.id).exists(),
            "Resources should not be affected by SQL injection attempts"
        )
