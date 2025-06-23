"""
Comprehensive performance tests for ResourcePro
Tests application performance under various load conditions
"""
import time
import json
from django.test import TestCase, TransactionTestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import connection
from django.test.utils import CaptureQueriesContext
from datetime import timedelta, date
from decimal import Decimal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from resources.models import Resource, Skill, TimeEntry, Availability
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import (
    ResourceDemandForecast, HistoricalUtilization, 
    SkillDemandAnalysis, ProjectCostTracking
)


class DatabasePerformanceTest(TestCase):
    """Test database query performance and optimization"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test data for performance testing
        self.create_performance_test_data()
        
    def create_performance_test_data(self):
        """Create large dataset for performance testing"""
        print("Creating performance test data...")
        
        # Create skills
        skills = []
        for i in range(20):
            skills.append(Skill(name=f'Skill {i}', category=f'Category {i % 5}'))
        Skill.objects.bulk_create(skills)
        
        # Create resources
        resources = []
        for i in range(100):
            resources.append(Resource(
                name=f'Resource {i}',
                role=f'Role {i % 10}',
                department=f'Department {i % 5}',
                capacity=40,
                cost_per_hour=Decimal('75.00')
            ))
        Resource.objects.bulk_create(resources)
        
        # Add skills to resources
        all_resources = Resource.objects.all()
        all_skills = Skill.objects.all()
        for i, resource in enumerate(all_resources):
            # Add 2-5 random skills to each resource
            skills_to_add = all_skills[i % 5:(i % 5) + 3]
            resource.skills.add(*skills_to_add)
        
        # Create projects
        projects = []
        for i in range(50):
            projects.append(Project(
                name=f'Project {i}',
                description=f'Description for project {i}',
                start_date=date.today() - timedelta(days=i),
                end_date=date.today() + timedelta(days=60 - i),
                status=['planning', 'active', 'on_hold', 'completed'][i % 4],
                budget=Decimal(f'{50000 + (i * 1000)}')
            ))
        Project.objects.bulk_create(projects)
        
        # Create tasks
        tasks = []
        all_projects = Project.objects.all()
        for project in all_projects:
            for j in range(10):  # 10 tasks per project
                tasks.append(Task(
                    project=project,
                    name=f'Task {j} for {project.name}',
                    description=f'Description for task {j}',
                    start_date=project.start_date,
                    end_date=project.start_date + timedelta(days=14),
                    estimated_hours=40 + (j * 10),
                    status=['not_started', 'in_progress', 'blocked', 'completed'][j % 4]
                ))
        Task.objects.bulk_create(tasks)
        
        # Create assignments
        assignments = []
        all_tasks = Task.objects.all()
        for i, task in enumerate(all_tasks[:300]):  # Assign first 300 tasks
            resource = all_resources[i % len(all_resources)]
            assignments.append(Assignment(
                task=task,
                resource=resource,
                allocated_hours=task.estimated_hours
            ))
        Assignment.objects.bulk_create(assignments)
        
        # Create time entries
        time_entries = []
        for i, assignment in enumerate(Assignment.objects.all()[:100]):  # Time entries for first 100 assignments
            for day in range(5):  # 5 days of work
                time_entries.append(TimeEntry(
                    resource=assignment.resource,
                    date=date.today() - timedelta(days=day),
                    hours=8,
                    description=f'Work on {assignment.task.name} day {day + 1}',
                    billable=True,
                    task=assignment.task
                ))
        TimeEntry.objects.bulk_create(time_entries)
        
        # Create historical utilization data
        utilization_data = []
        for resource in all_resources[:50]:  # First 50 resources
            for day in range(30):  # 30 days of history
                utilization_data.append(HistoricalUtilization(
                    resource=resource,
                    date=date.today() - timedelta(days=day),
                    utilization_percentage=Decimal(f'{60 + (day % 40)}'),
                    allocated_hours=Decimal('32.0'),
                    available_hours=Decimal('40.0')
                ))
        HistoricalUtilization.objects.bulk_create(utilization_data)
        
        print(f"Created test data:")
        print(f"- Skills: {Skill.objects.count()}")
        print(f"- Resources: {Resource.objects.count()}")
        print(f"- Projects: {Project.objects.count()}")
        print(f"- Tasks: {Task.objects.count()}")
        print(f"- Assignments: {Assignment.objects.count()}")
        print(f"- Time Entries: {TimeEntry.objects.count()}")
        print(f"- Historical Data: {HistoricalUtilization.objects.count()}")
        
    def test_dashboard_query_performance(self):
        """Test dashboard page query performance"""
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('dashboard'))
            end_time = time.time()
            
        response_time = end_time - start_time
        query_count = len(context)
        
        print(f"Dashboard Performance:")
        print(f"- Response time: {response_time:.3f} seconds")
        print(f"- Query count: {query_count}")
        
        # Performance assertions
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0, "Dashboard should load in under 2 seconds")
        self.assertLess(query_count, 50, "Dashboard should use fewer than 50 queries")
        
    def test_resource_list_query_performance(self):
        """Test resource list page query performance"""
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('resources:resource_list'))
            end_time = time.time()
            
        response_time = end_time - start_time
        query_count = len(context)
        
        print(f"Resource List Performance:")
        print(f"- Response time: {response_time:.3f} seconds")
        print(f"- Query count: {query_count}")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.5, "Resource list should load in under 1.5 seconds")
        self.assertLess(query_count, 30, "Resource list should use fewer than 30 queries")
        
    def test_allocation_board_query_performance(self):
        """Test allocation board query performance"""
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('allocation_board'))
            end_time = time.time()
            
        response_time = end_time - start_time
        query_count = len(context)
        
        print(f"Allocation Board Performance:")
        print(f"- Response time: {response_time:.3f} seconds")
        print(f"- Query count: {query_count}")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 3.0, "Allocation board should load in under 3 seconds")
        self.assertLess(query_count, 100, "Allocation board should use fewer than 100 queries")
        
    def test_analytics_dashboard_query_performance(self):
        """Test analytics dashboard query performance"""
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('analytics:analytics_dashboard'))
            end_time = time.time()
            
        response_time = end_time - start_time
        query_count = len(context)
        
        print(f"Analytics Dashboard Performance:")
        print(f"- Response time: {response_time:.3f} seconds")
        print(f"- Query count: {query_count}")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.5, "Analytics dashboard should load in under 2.5 seconds")
        self.assertLess(query_count, 75, "Analytics dashboard should use fewer than 75 queries")
        
    def test_utilization_calculation_performance(self):
        """Test resource utilization calculation performance"""
        resources = Resource.objects.all()[:20]  # Test with 20 resources
        
        start_time = time.time()
        utilizations = []
        for resource in resources:
            utilization = resource.current_utilization()
            utilizations.append(utilization)
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        print(f"Utilization Calculation Performance:")
        print(f"- Calculation time for 20 resources: {calculation_time:.3f} seconds")
        print(f"- Average per resource: {calculation_time / 20:.3f} seconds")
        
        self.assertLess(calculation_time, 1.0, "Utilization calculation should be fast")
        self.assertEqual(len(utilizations), 20)
        
    def test_bulk_assignment_performance(self):
        """Test bulk assignment operation performance"""
        unassigned_tasks = Task.objects.filter(assignments=None)[:50]
        available_resources = Resource.objects.all()[:10]
        
        assignments_data = []
        for i, task in enumerate(unassigned_tasks):
            resource = available_resources[i % len(available_resources)]
            assignments_data.append({
                'task_id': task.id,
                'resource_id': resource.id,
                'allocated_hours': task.estimated_hours
            })
        
        start_time = time.time()
        
        # Simulate bulk assignment via API calls
        successful_assignments = 0
        for assignment_data in assignments_data[:10]:  # Test with first 10
            response = self.client.post(
                reverse('assign_task'),
                assignment_data,
                content_type='application/json'
            )
            if response.status_code == 200:
                successful_assignments += 1
                
        end_time = time.time()
        
        bulk_assignment_time = end_time - start_time
        
        print(f"Bulk Assignment Performance:")
        print(f"- Time for 10 assignments: {bulk_assignment_time:.3f} seconds")
        print(f"- Successful assignments: {successful_assignments}")
        print(f"- Average per assignment: {bulk_assignment_time / 10:.3f} seconds")
        
        self.assertLess(bulk_assignment_time, 5.0, "Bulk assignment should be reasonably fast")
        self.assertGreater(successful_assignments, 5, "Most assignments should succeed")


class ConcurrentAccessTest(TransactionTestCase):
    """Test application performance under concurrent access"""
    
    def setUp(self):
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'concuser{i}',
                email=f'concuser{i}@example.com',
                password='testpass123'
            )
            self.users.append(user)
            
        # Create minimal test data
        self.resource = Resource.objects.create(
            name='Concurrent Test Resource',
            role='Developer',
            capacity=40
        )
        
        self.project = Project.objects.create(
            name='Concurrent Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active'
        )
        
        # Create multiple tasks for concurrent assignment testing
        self.tasks = []
        for i in range(20):
            task = Task.objects.create(
                project=self.project,
                name=f'Concurrent Task {i}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=7),
                estimated_hours=40,
                status='not_started'
            )
            self.tasks.append(task)
            
    def simulate_user_session(self, user_id):
        """Simulate a user session with multiple page requests"""
        client = Client()
        user = self.users[user_id]
        client.force_login(user)
        
        results = {
            'user_id': user_id,
            'requests': [],
            'errors': 0,
            'total_time': 0
        }
        
        # Simulate typical user workflow
        test_urls = [
            reverse('dashboard'),
            reverse('resources:resource_list'),
            reverse('project_list'),
            reverse('allocation_board'),
            reverse('analytics:analytics_dashboard')
        ]
        
        session_start = time.time()
        
        for url in test_urls:
            request_start = time.time()
            try:
                response = client.get(url)
                request_end = time.time()
                request_time = request_end - request_start
                
                results['requests'].append({
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': request_time
                })
                
                if response.status_code != 200:
                    results['errors'] += 1
                    
            except Exception as e:
                request_end = time.time()
                results['errors'] += 1
                results['requests'].append({
                    'url': url,
                    'status_code': 500,
                    'response_time': request_end - request_start,
                    'error': str(e)
                })
                
        session_end = time.time()
        results['total_time'] = session_end - session_start
        
        return results
        
    def test_concurrent_user_access(self):
        """Test multiple users accessing the system simultaneously"""
        print("Testing concurrent user access...")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor to simulate concurrent users
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for 5 concurrent users
            futures = [executor.submit(self.simulate_user_session, i) for i in range(5)]
            
            # Collect results
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
        end_time = time.time()
        total_test_time = end_time - start_time
        
        # Analyze results
        total_requests = sum(len(r['requests']) for r in results)
        total_errors = sum(r['errors'] for r in results)
        avg_session_time = sum(r['total_time'] for r in results) / len(results)
        
        # Calculate response time statistics
        all_response_times = []
        for result in results:
            for request in result['requests']:
                if 'response_time' in request:
                    all_response_times.append(request['response_time'])
                    
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        
        print(f"Concurrent Access Test Results:")
        print(f"- Total test time: {total_test_time:.3f} seconds")
        print(f"- Concurrent users: 5")
        print(f"- Total requests: {total_requests}")
        print(f"- Total errors: {total_errors}")
        print(f"- Error rate: {(total_errors / total_requests * 100):.1f}%")
        print(f"- Average session time: {avg_session_time:.3f} seconds")
        print(f"- Average response time: {avg_response_time:.3f} seconds")
        print(f"- Maximum response time: {max_response_time:.3f} seconds")
        
        # Performance assertions
        self.assertLess(total_errors / total_requests, 0.1, "Error rate should be less than 10%")
        self.assertLess(avg_response_time, 2.0, "Average response time should be under 2 seconds")
        self.assertLess(max_response_time, 5.0, "Maximum response time should be under 5 seconds")
        
    def test_concurrent_assignment_operations(self):
        """Test concurrent assignment operations"""
        print("Testing concurrent assignment operations...")
        
        def assign_task_concurrently(task_id, user_id):
            """Attempt to assign a task from a concurrent user session"""
            client = Client()
            user = self.users[user_id % len(self.users)]
            client.force_login(user)
            
            assignment_data = {
                'task_id': task_id,
                'resource_id': self.resource.id,
                'allocated_hours': 40
            }
            
            try:
                response = client.post(
                    reverse('assign_task'),
                    assignment_data,
                    content_type='application/json'
                )
                return {
                    'task_id': task_id,
                    'user_id': user_id,
                    'status_code': response.status_code,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'task_id': task_id,
                    'user_id': user_id,
                    'status_code': 500,
                    'success': False,
                    'error': str(e)
                }
        
        start_time = time.time()
        
        # Try to assign first 10 tasks concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(assign_task_concurrently, self.tasks[i].id, i)
                for i in range(10)
            ]
            
            assignment_results = []
            for future in as_completed(futures):
                result = future.result()
                assignment_results.append(result)
                
        end_time = time.time()
        concurrent_assignment_time = end_time - start_time
        
        # Analyze assignment results
        successful_assignments = sum(1 for r in assignment_results if r['success'])
        failed_assignments = len(assignment_results) - successful_assignments
        
        print(f"Concurrent Assignment Test Results:")
        print(f"- Test time: {concurrent_assignment_time:.3f} seconds")
        print(f"- Attempted assignments: {len(assignment_results)}")
        print(f"- Successful assignments: {successful_assignments}")
        print(f"- Failed assignments: {failed_assignments}")
        print(f"- Success rate: {(successful_assignments / len(assignment_results) * 100):.1f}%")
        
        # Verify database consistency
        actual_assignments = Assignment.objects.filter(
            task__in=[t.id for t in self.tasks[:10]],
            resource=self.resource
        ).count()
        
        print(f"- Actual assignments in database: {actual_assignments}")
        
        # Assertions
        self.assertLessEqual(actual_assignments, 10, "Should not have more assignments than tasks")
        self.assertGreater(successful_assignments, 0, "At least some assignments should succeed")
        self.assertLess(concurrent_assignment_time, 10.0, "Concurrent assignments should complete reasonably quickly")


class LoadTestingTest(TestCase):
    """Test application under sustained load"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='loadtest',
            email='load@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create moderate amount of test data
        self.create_load_test_data()
        
    def create_load_test_data(self):
        """Create data for load testing"""
        # Create 50 resources
        resources = []
        for i in range(50):
            resources.append(Resource(
                name=f'Load Test Resource {i}',
                role=f'Role {i % 5}',
                capacity=40,
                cost_per_hour=Decimal('75.00')
            ))
        Resource.objects.bulk_create(resources)
        
        # Create 25 projects
        projects = []
        for i in range(25):
            projects.append(Project(
                name=f'Load Test Project {i}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=60),
                status='active',
                budget=Decimal('100000.00')
            ))
        Project.objects.bulk_create(projects)
        
        # Create tasks
        tasks = []
        for project in Project.objects.all():
            for j in range(5):  # 5 tasks per project
                tasks.append(Task(
                    project=project,
                    name=f'Task {j} for {project.name}',
                    start_date=project.start_date,
                    end_date=project.start_date + timedelta(days=14),
                    estimated_hours=80,
                    status='not_started'
                ))
        Task.objects.bulk_create(tasks)
        
    def test_sustained_dashboard_load(self):
        """Test dashboard under sustained load"""
        print("Testing sustained dashboard load...")
        
        request_count = 50
        response_times = []
        errors = 0
        
        start_time = time.time()
        
        for i in range(request_count):
            request_start = time.time()
            try:
                response = self.client.get(reverse('dashboard'))
                request_end = time.time()
                
                response_time = request_end - request_start
                response_times.append(response_time)
                
                if response.status_code != 200:
                    errors += 1
                    
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                errors += 1
                print(f"Error on request {i}: {e}")
                
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        requests_per_second = request_count / total_time
        
        print(f"Sustained Dashboard Load Results:")
        print(f"- Total requests: {request_count}")
        print(f"- Total time: {total_time:.3f} seconds")
        print(f"- Requests per second: {requests_per_second:.2f}")
        print(f"- Errors: {errors}")
        print(f"- Error rate: {(errors / request_count * 100):.1f}%")
        print(f"- Average response time: {avg_response_time:.3f} seconds")
        print(f"- Min response time: {min_response_time:.3f} seconds")
        print(f"- Max response time: {max_response_time:.3f} seconds")
        
        # Performance assertions
        self.assertLess(errors / request_count, 0.05, "Error rate should be less than 5%")
        self.assertLess(avg_response_time, 1.0, "Average response time should be under 1 second")
        self.assertGreater(requests_per_second, 10, "Should handle at least 10 requests per second")
        
    def test_allocation_board_load(self):
        """Test allocation board under load"""
        print("Testing allocation board load...")
        
        request_count = 20  # Fewer requests due to complexity
        response_times = []
        errors = 0
        
        for i in range(request_count):
            request_start = time.time()
            try:
                response = self.client.get(reverse('allocation_board'))
                request_end = time.time()
                
                response_time = request_end - request_start
                response_times.append(response_time)
                
                if response.status_code != 200:
                    errors += 1
                    
                time.sleep(0.2)  # Longer delay for complex page
                
            except Exception as e:
                errors += 1
                print(f"Error on allocation board request {i}: {e}")
                
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"Allocation Board Load Results:")
        print(f"- Total requests: {request_count}")
        print(f"- Errors: {errors}")
        print(f"- Average response time: {avg_response_time:.3f} seconds")
        print(f"- Max response time: {max_response_time:.3f} seconds")
        
        # Performance assertions
        self.assertLess(errors / request_count, 0.1, "Error rate should be less than 10%")
        self.assertLess(avg_response_time, 2.0, "Average response time should be under 2 seconds")
        self.assertLess(max_response_time, 5.0, "Maximum response time should be under 5 seconds")


class MemoryUsageTest(TestCase):
    """Test memory usage patterns"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='memtest',
            email='mem@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_large_dataset_memory_usage(self):
        """Test memory usage with large datasets"""
        print("Testing memory usage with large datasets...")
        
        # Create large dataset
        large_resources = []
        for i in range(500):
            large_resources.append(Resource(
                name=f'Memory Test Resource {i}',
                role=f'Role {i % 10}',
                capacity=40,
                cost_per_hour=Decimal('75.00')
            ))
        Resource.objects.bulk_create(large_resources)
        
        # Test memory usage of resource list
        start_time = time.time()
        response = self.client.get(reverse('resources:resource_list'))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"Large Dataset Memory Test:")
        print(f"- Resources created: 500")
        print(f"- Response time: {response_time:.3f} seconds")
        print(f"- Response status: {response.status_code}")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 3.0, "Should handle large datasets reasonably well")
        
    def test_complex_query_performance(self):
        """Test performance of complex queries"""
        print("Testing complex query performance...")
        
        # Create test data with relationships
        skill = Skill.objects.create(name='Complex Test Skill', category='Test')
        
        resources = []
        for i in range(100):
            resources.append(Resource(
                name=f'Complex Resource {i}',
                role='Developer',
                capacity=40
            ))
        Resource.objects.bulk_create(resources)
        
        # Add skills to all resources
        for resource in Resource.objects.all():
            resource.skills.add(skill)
            
        projects = []
        for i in range(20):
            projects.append(Project(
                name=f'Complex Project {i}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                status='active'
            ))
        Project.objects.bulk_create(projects)
        
        # Create tasks and assignments
        assignments = []
        for project in Project.objects.all():
            for i in range(5):
                task = Task.objects.create(
                    project=project,
                    name=f'Complex Task {i}',
                    start_date=project.start_date,
                    end_date=project.end_date,
                    estimated_hours=80,
                    status='in_progress'
                )
                task.skills_required.add(skill)
                
                # Assign to a resource
                resource = Resource.objects.all()[i % Resource.objects.count()]
                assignments.append(Assignment(
                    task=task,
                    resource=resource,
                    allocated_hours=80
                ))
        Assignment.objects.bulk_create(assignments)
        
        # Test complex analytics query
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(reverse('analytics:utilization_report'))
            end_time = time.time()
            
        response_time = end_time - start_time
        query_count = len(context)
        
        print(f"Complex Query Performance:")
        print(f"- Response time: {response_time:.3f} seconds")
        print(f"- Query count: {query_count}")
        print(f"- Data created: 100 resources, 20 projects, 100 tasks, 100 assignments")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5.0, "Complex queries should complete in reasonable time")
        self.assertLess(query_count, 200, "Should not generate excessive queries")


class APIPerformanceTest(TestCase):
    """Test API endpoint performance"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='apitest',
            email='api@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test data for API testing
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
        
        # Create multiple tasks for testing
        self.tasks = []
        for i in range(50):
            task = Task.objects.create(
                project=self.project,
                name=f'API Test Task {i}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=7),
                estimated_hours=40,
                status='not_started'
            )
            self.tasks.append(task)
            
    def test_assignment_api_performance(self):
        """Test assignment API performance under load"""
        print("Testing assignment API performance...")
        
        assignment_times = []
        successful_assignments = 0
        
        for i, task in enumerate(self.tasks[:20]):  # Test first 20 tasks
            assignment_data = {
                'task_id': task.id,
                'resource_id': self.resource.id,
                'allocated_hours': 40
            }
            
            start_time = time.time()
            response = self.client.post(
                reverse('assign_task'),
                assignment_data,
                content_type='application/json'
            )
            end_time = time.time()
            
            assignment_time = end_time - start_time
            assignment_times.append(assignment_time)
            
            if response.status_code == 200:
                successful_assignments += 1
                
        avg_assignment_time = sum(assignment_times) / len(assignment_times)
        max_assignment_time = max(assignment_times)
        
        print(f"Assignment API Performance:")
        print(f"- Total assignments attempted: {len(assignment_times)}")
        print(f"- Successful assignments: {successful_assignments}")
        print(f"- Average assignment time: {avg_assignment_time:.3f} seconds")
        print(f"- Maximum assignment time: {max_assignment_time:.3f} seconds")
        
        self.assertGreater(successful_assignments, 15, "Most assignments should succeed")
        self.assertLess(avg_assignment_time, 0.5, "Average assignment time should be fast")
        self.assertLess(max_assignment_time, 2.0, "Maximum assignment time should be reasonable")
        
    def test_conflict_checking_performance(self):
        """Test conflict checking API performance"""
        print("Testing conflict checking performance...")
        
        # Create some assignments first
        for task in self.tasks[:10]:
            Assignment.objects.create(
                task=task,
                resource=self.resource,
                allocated_hours=40
            )
            
        conflict_check_times = []
        
        for task in self.tasks[10:20]:  # Check conflicts for next 10 tasks
            start_time = time.time()
            response = self.client.get(
                reverse('check_assignment_conflicts'),
                {'task_id': task.id, 'resource_id': self.resource.id}
            )
            end_time = time.time()
            
            conflict_time = end_time - start_time
            conflict_check_times.append(conflict_time)
            
            self.assertEqual(response.status_code, 200)
            
        avg_conflict_time = sum(conflict_check_times) / len(conflict_check_times)
        max_conflict_time = max(conflict_check_times)
        
        print(f"Conflict Checking Performance:")
        print(f"- Conflict checks performed: {len(conflict_check_times)}")
        print(f"- Average conflict check time: {avg_conflict_time:.3f} seconds")
        print(f"- Maximum conflict check time: {max_conflict_time:.3f} seconds")
        
        self.assertLess(avg_conflict_time, 0.2, "Conflict checking should be very fast")
        self.assertLess(max_conflict_time, 1.0, "Maximum conflict check time should be reasonable")
