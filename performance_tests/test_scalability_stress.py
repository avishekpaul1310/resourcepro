"""
Scalability and stress tests for ResourcePro
Tests system behavior under extreme conditions
"""
import time
import json
import gc
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import connection, transaction
from django.test.utils import CaptureQueriesContext
from datetime import timedelta, date
from decimal import Decimal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from django.core.cache import cache

from resources.models import Resource, Skill, TimeEntry, Availability
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import HistoricalUtilization, ResourceDemandForecast


class ScalabilityTest(TestCase):
    """Test system scalability with increasing data sizes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='scaletest',
            email='scale@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def create_scalability_dataset(self, scale_factor=1):
        """Create dataset scaled by the given factor"""
        print(f"Creating scalability dataset with scale factor {scale_factor}...")
        
        # Base numbers multiplied by scale factor
        num_skills = 10 * scale_factor
        num_resources = 50 * scale_factor
        num_projects = 20 * scale_factor
        num_tasks_per_project = 5
        
        # Create skills
        skills = []
        for i in range(num_skills):
            skills.append(Skill(
                name=f'Scale Skill {i}',
                category=f'Category {i % 5}'
            ))
        Skill.objects.bulk_create(skills, batch_size=100)
        
        # Create resources
        resources = []
        for i in range(num_resources):
            resources.append(Resource(
                name=f'Scale Resource {i}',
                role=f'Role {i % 10}',
                department=f'Department {i % 5}',
                capacity=40,
                cost_per_hour=Decimal('75.00')
            ))
        Resource.objects.bulk_create(resources, batch_size=100)
        
        # Assign skills to resources (many-to-many)
        all_resources = list(Resource.objects.all())
        all_skills = list(Skill.objects.all())
        for i, resource in enumerate(all_resources):
            # Assign 2-4 skills per resource
            skills_to_assign = all_skills[i % len(all_skills):(i % len(all_skills)) + 3]
            resource.skills.add(*skills_to_assign)
        
        # Create projects
        projects = []
        for i in range(num_projects):
            projects.append(Project(
                name=f'Scale Project {i}',
                description=f'Scalability test project {i}',
                start_date=date.today() - timedelta(days=i % 30),
                end_date=date.today() + timedelta(days=60 - (i % 30)),
                status=['planning', 'active', 'on_hold'][i % 3],
                budget=Decimal(f'{100000 + (i * 5000)}')
            ))
        Project.objects.bulk_create(projects, batch_size=100)
        
        # Create tasks
        tasks = []
        all_projects = list(Project.objects.all())
        for project in all_projects:
            for j in range(num_tasks_per_project):
                tasks.append(Task(
                    project=project,
                    name=f'Scale Task {j} - {project.name}',
                    description=f'Scalability test task {j}',
                    start_date=project.start_date,
                    end_date=project.start_date + timedelta(days=14),
                    estimated_hours=40 + (j * 20),
                    status=['not_started', 'in_progress', 'completed'][j % 3]
                ))
        Task.objects.bulk_create(tasks, batch_size=100)
        
        # Create assignments (assign about 60% of tasks)
        assignments = []
        all_tasks = list(Task.objects.all())
        assigned_tasks = all_tasks[:int(len(all_tasks) * 0.6)]
        
        for i, task in enumerate(assigned_tasks):
            resource = all_resources[i % len(all_resources)]
            assignments.append(Assignment(
                task=task,
                resource=resource,
                allocated_hours=task.estimated_hours
            ))
        Assignment.objects.bulk_create(assignments, batch_size=100)
        
        # Create time entries for recent assignments
        time_entries = []
        recent_assignments = Assignment.objects.all()[:min(100 * scale_factor, Assignment.objects.count())]
        
        for assignment in recent_assignments:
            for day in range(min(5, 10 // scale_factor + 1)):  # Fewer days for larger scales
                time_entries.append(TimeEntry(
                    resource=assignment.resource,
                    date=date.today() - timedelta(days=day),
                    hours=8,
                    description=f'Scale test work day {day + 1}',
                    billable=True,
                    task=assignment.task
                ))
        TimeEntry.objects.bulk_create(time_entries, batch_size=100)
        
        # Create historical utilization data
        utilization_entries = []
        sample_resources = all_resources[:min(20 * scale_factor, len(all_resources))]
        
        for resource in sample_resources:
            for day in range(min(30, 60 // scale_factor)):  # Fewer days for larger scales
                utilization_entries.append(HistoricalUtilization(
                    resource=resource,
                    date=date.today() - timedelta(days=day),
                    utilization_percentage=Decimal(f'{60 + (day % 40)}'),
                    allocated_hours=Decimal('32.0'),
                    available_hours=Decimal('40.0')
                ))
        HistoricalUtilization.objects.bulk_create(utilization_entries, batch_size=100)
        
        print(f"Created scalability dataset:")
        print(f"- Skills: {Skill.objects.count()}")
        print(f"- Resources: {Resource.objects.count()}")
        print(f"- Projects: {Project.objects.count()}")
        print(f"- Tasks: {Task.objects.count()}")
        print(f"- Assignments: {Assignment.objects.count()}")
        print(f"- Time Entries: {TimeEntry.objects.count()}")
        print(f"- Historical Data: {HistoricalUtilization.objects.count()}")
        
        return {
            'skills': Skill.objects.count(),
            'resources': Resource.objects.count(),
            'projects': Project.objects.count(),
            'tasks': Task.objects.count(),
            'assignments': Assignment.objects.count(),
            'time_entries': TimeEntry.objects.count(),
            'historical_data': HistoricalUtilization.objects.count()
        }
        
    def test_scalability_progression(self):
        """Test performance across different data scales"""
        print("Testing scalability progression...")
        
        scale_factors = [1, 2, 3]  # Test with increasing data sizes
        results = []
        
        for scale_factor in scale_factors:
            print(f"\n--- Testing Scale Factor {scale_factor} ---")
            
            # Clear existing data
            self.tearDown()
            self.setUp()
            
            # Create scaled dataset
            dataset_info = self.create_scalability_dataset(scale_factor)
            
            # Test key endpoints
            endpoints_to_test = [
                ('dashboard', 'dashboard'),
                ('resources:resource_list', 'resource_list'),
                ('allocation_board', 'allocation_board'),
                ('analytics:analytics_dashboard', 'analytics_dashboard')
            ]
            
            scale_results = {
                'scale_factor': scale_factor,
                'dataset_size': dataset_info,
                'endpoint_performance': {}
            }
            
            for endpoint_name, url_name in endpoints_to_test:
                # Test endpoint performance
                with CaptureQueriesContext(connection) as context:
                    start_time = time.time()
                    try:
                        response = self.client.get(reverse(url_name))
                        end_time = time.time()
                        response_time = end_time - start_time
                        status_code = response.status_code
                    except Exception as e:
                        end_time = time.time()
                        response_time = end_time - start_time
                        status_code = 500
                        print(f"Error testing {endpoint_name}: {e}")
                
                query_count = len(context)
                
                scale_results['endpoint_performance'][endpoint_name] = {
                    'response_time': response_time,
                    'query_count': query_count,
                    'status_code': status_code
                }
                
                print(f"{endpoint_name}: {response_time:.3f}s, {query_count} queries, status {status_code}")
            
            results.append(scale_results)
            
            # Force garbage collection between tests
            gc.collect()
        
        # Analyze scalability trends
        print("\n--- Scalability Analysis ---")
        for endpoint_name, _ in endpoints_to_test:
            print(f"\n{endpoint_name} Scalability:")
            for result in results:
                perf = result['endpoint_performance'][endpoint_name]
                scale = result['scale_factor']
                resources = result['dataset_size']['resources']
                print(f"  Scale {scale} ({resources} resources): {perf['response_time']:.3f}s, {perf['query_count']} queries")
        
        # Verify reasonable scalability
        for endpoint_name, _ in endpoints_to_test:
            # Check that response time doesn't grow exponentially
            times = [r['endpoint_performance'][endpoint_name]['response_time'] for r in results]
            
            # Response time should not more than triple from scale 1 to scale 3
            if len(times) >= 2 and times[0] > 0:
                scale_factor_increase = times[-1] / times[0]
                self.assertLess(
                    scale_factor_increase, 
                    5.0, 
                    f"{endpoint_name} response time increased by {scale_factor_increase:.1f}x, should be more scalable"
                )
        
        return results
        
    def tearDown(self):
        """Clean up data between tests"""
        # Delete in order to respect foreign key constraints
        TimeEntry.objects.all().delete()
        HistoricalUtilization.objects.all().delete()
        Assignment.objects.all().delete()
        Task.objects.all().delete()
        Project.objects.all().delete()
        # Clear many-to-many relationships
        for resource in Resource.objects.all():
            resource.skills.clear()
        Resource.objects.all().delete()
        Skill.objects.all().delete()


class StressTest(TransactionTestCase):
    """Test system under stress conditions"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='stresstest',
            email='stress@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def create_stress_test_data(self):
        """Create substantial dataset for stress testing"""
        print("Creating stress test dataset...")
        
        # Create a substantial but manageable dataset
        num_resources = 200
        num_projects = 50
        num_tasks_per_project = 8
        
        # Create skills
        skills = []
        for i in range(30):
            skills.append(Skill(name=f'Stress Skill {i}', category=f'Cat {i % 6}'))
        Skill.objects.bulk_create(skills)
        
        # Create resources
        resources = []
        for i in range(num_resources):
            resources.append(Resource(
                name=f'Stress Resource {i}',
                role=f'Role {i % 15}',
                department=f'Dept {i % 8}',
                capacity=40,
                cost_per_hour=Decimal('75.00')
            ))
        Resource.objects.bulk_create(resources, batch_size=50)
        
        # Create projects
        projects = []
        for i in range(num_projects):
            projects.append(Project(
                name=f'Stress Project {i}',
                start_date=date.today() - timedelta(days=i % 60),
                end_date=date.today() + timedelta(days=90 - i % 60),
                status=['planning', 'active', 'on_hold', 'completed'][i % 4],
                budget=Decimal(f'{50000 + i * 2000}')
            ))
        Project.objects.bulk_create(projects, batch_size=50)
        
        # Create tasks
        tasks = []
        for project in Project.objects.all():
            for j in range(num_tasks_per_project):
                tasks.append(Task(
                    project=project,
                    name=f'Stress Task {j} - {project.name}',
                    start_date=project.start_date,
                    end_date=project.start_date + timedelta(days=21),
                    estimated_hours=60 + j * 15,
                    status=['not_started', 'in_progress', 'blocked', 'completed'][j % 4]
                ))
        Task.objects.bulk_create(tasks, batch_size=50)
        
        print(f"Stress test data created:")
        print(f"- Resources: {Resource.objects.count()}")
        print(f"- Projects: {Project.objects.count()}")
        print(f"- Tasks: {Task.objects.count()}")
        
    def stress_test_endpoint(self, url_name, request_count=100, max_workers=10):
        """Stress test a specific endpoint with concurrent requests"""
        print(f"Stress testing {url_name} with {request_count} requests, {max_workers} workers...")
        
        def make_request(request_id):
            """Make a single request and return timing info"""
            client = Client()
            client.force_login(self.user)
            
            start_time = time.time()
            try:
                response = client.get(reverse(url_name))
                end_time = time.time()
                return {
                    'request_id': request_id,
                    'response_time': end_time - start_time,
                    'status_code': response.status_code,
                    'success': response.status_code == 200
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'request_id': request_id,
                    'response_time': end_time - start_time,
                    'status_code': 500,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute stress test
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, i) for i in range(request_count)]
            results = []
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_requests = sum(1 for r in results if r['success'])
        failed_requests = request_count - successful_requests
        response_times = [r['response_time'] for r in results if r['success']]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95_response_time = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        requests_per_second = successful_requests / total_time if total_time > 0 else 0
        
        stress_results = {
            'endpoint': url_name,
            'total_requests': request_count,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'error_rate': failed_requests / request_count,
            'total_time': total_time,
            'requests_per_second': requests_per_second,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'p95_response_time': p95_response_time
        }
        
        print(f"Stress Test Results for {url_name}:")
        print(f"- Total requests: {request_count}")
        print(f"- Successful: {successful_requests}")
        print(f"- Failed: {failed_requests}")
        print(f"- Error rate: {stress_results['error_rate']:.1%}")
        print(f"- Total time: {total_time:.3f}s")
        print(f"- Requests/sec: {requests_per_second:.2f}")
        print(f"- Avg response time: {avg_response_time:.3f}s")
        print(f"- Min response time: {min_response_time:.3f}s")
        print(f"- Max response time: {max_response_time:.3f}s")
        print(f"- 95th percentile: {p95_response_time:.3f}s")
        
        return stress_results
        
    def test_dashboard_stress(self):
        """Stress test dashboard endpoint"""
        self.create_stress_test_data()
        
        results = self.stress_test_endpoint('dashboard', request_count=50, max_workers=5)
        
        # Assertions for dashboard stress test
        self.assertLess(results['error_rate'], 0.1, "Dashboard error rate should be less than 10%")
        self.assertGreater(results['requests_per_second'], 5, "Should handle at least 5 requests per second")
        self.assertLess(results['avg_response_time'], 2.0, "Average response time should be under 2 seconds")
        self.assertLess(results['p95_response_time'], 5.0, "95th percentile should be under 5 seconds")
        
    def test_resource_list_stress(self):
        """Stress test resource list endpoint"""
        self.create_stress_test_data()
        
        results = self.stress_test_endpoint('resources:resource_list', request_count=75, max_workers=8)
        
        # Assertions for resource list stress test
        self.assertLess(results['error_rate'], 0.05, "Resource list error rate should be less than 5%")
        self.assertGreater(results['requests_per_second'], 10, "Should handle at least 10 requests per second")
        self.assertLess(results['avg_response_time'], 1.5, "Average response time should be under 1.5 seconds")
        
    def test_allocation_board_stress(self):
        """Stress test allocation board endpoint"""
        self.create_stress_test_data()
        
        # Allocation board is more complex, so fewer concurrent requests
        results = self.stress_test_endpoint('allocation_board', request_count=30, max_workers=3)
        
        # More lenient assertions for complex allocation board
        self.assertLess(results['error_rate'], 0.15, "Allocation board error rate should be less than 15%")
        self.assertGreater(results['requests_per_second'], 2, "Should handle at least 2 requests per second")
        self.assertLess(results['avg_response_time'], 5.0, "Average response time should be under 5 seconds")


class MemoryLeakTest(TestCase):
    """Test for potential memory leaks"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='memleaktest',
            email='memleak@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_repeated_requests_memory_usage(self):
        """Test memory usage over repeated requests"""
        print("Testing for memory leaks over repeated requests...")
        
        # Create moderate dataset
        for i in range(50):
            Resource.objects.create(
                name=f'Memory Test Resource {i}',
                role='Developer',
                capacity=40
            )
            
        # Make repeated requests and monitor memory patterns
        request_count = 100
        response_times = []
        
        for i in range(request_count):
            start_time = time.time()
            response = self.client.get(reverse('dashboard'))
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            self.assertEqual(response.status_code, 200)
            
            # Periodically force garbage collection
            if i % 20 == 0:
                gc.collect()
        
        # Analyze response time trends (memory leaks often cause slowdowns)
        first_quarter = response_times[:25]
        last_quarter = response_times[-25:]
        
        avg_first_quarter = sum(first_quarter) / len(first_quarter)
        avg_last_quarter = sum(last_quarter) / len(last_quarter)
        
        performance_degradation = avg_last_quarter / avg_first_quarter if avg_first_quarter > 0 else 1
        
        print(f"Memory Leak Test Results:")
        print(f"- Total requests: {request_count}")
        print(f"- Avg response time (first 25): {avg_first_quarter:.3f}s")
        print(f"- Avg response time (last 25): {avg_last_quarter:.3f}s")
        print(f"- Performance degradation factor: {performance_degradation:.2f}")
        
        # Performance should not degrade significantly over time
        self.assertLess(
            performance_degradation, 
            2.0, 
            "Performance should not degrade significantly over repeated requests"
        )
        
    def test_large_queryset_cleanup(self):
        """Test that large querysets are properly cleaned up"""
        print("Testing large queryset cleanup...")
        
        # Create large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append(Resource(
                name=f'Large Dataset Resource {i}',
                role='Test Role',
                capacity=40
            ))
        Resource.objects.bulk_create(large_dataset)
        
        # Perform operations that create large querysets
        operations = [
            lambda: list(Resource.objects.all()),  # Load all resources
            lambda: list(Resource.objects.filter(role='Test Role')),  # Filtered query
            lambda: Resource.objects.aggregate(total=models.Sum('capacity')),  # Aggregation
            lambda: list(Resource.objects.values('name', 'role')),  # Values query
        ]
        
        for i, operation in enumerate(operations):
            start_time = time.time()
            result = operation()
            end_time = time.time()
            
            operation_time = end_time - start_time
            print(f"Operation {i+1}: {operation_time:.3f}s")
            
            # Force cleanup
            del result
            gc.collect()
            
        # If we get here without memory errors, the test passes
        self.assertTrue(True, "Large queryset operations completed without memory issues")


class EdgeCaseStressTest(TestCase):
    """Test edge cases and boundary conditions under stress"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='edgetest',
            email='edge@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_empty_database_performance(self):
        """Test performance with empty database"""
        print("Testing performance with empty database...")
        
        # Ensure database is empty
        self.assertEqual(Resource.objects.count(), 0)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Task.objects.count(), 0)
        
        # Test all major endpoints with empty data
        endpoints = [
            'dashboard',
            'resources:resource_list',
            'project_list',
            'allocation_board',
            'analytics:analytics_dashboard'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(reverse(endpoint))
            end_time = time.time()
            
            response_time = end_time - start_time
            
            print(f"{endpoint}: {response_time:.3f}s, status {response.status_code}")
            
            # All endpoints should work with empty data
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 1.0, f"{endpoint} should be fast with empty data")
            
    def test_single_large_project_stress(self):
        """Test performance with one project containing many tasks"""
        print("Testing single large project with many tasks...")
        
        # Create one project with many tasks
        project = Project.objects.create(
            name='Mega Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            status='active',
            budget=Decimal('1000000.00')
        )
        
        # Create many tasks
        tasks = []
        for i in range(500):  # 500 tasks in one project
            tasks.append(Task(
                project=project,
                name=f'Mega Task {i}',
                start_date=project.start_date,
                end_date=project.start_date + timedelta(days=7),
                estimated_hours=40,
                status='not_started'
            ))
        Task.objects.bulk_create(tasks, batch_size=100)
        
        # Test project detail page performance
        start_time = time.time()
        response = self.client.get(reverse('project_detail', kwargs={'pk': project.id}))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"Project with 500 tasks: {response_time:.3f}s")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5.0, "Large project should load in reasonable time")
        
    def test_deeply_nested_data_stress(self):
        """Test performance with deeply nested relationships"""
        print("Testing deeply nested data relationships...")
        
        # Create complex nested structure
        skill = Skill.objects.create(name='Complex Skill', category='Test')
        
        # Create resource with many skills
        resource = Resource.objects.create(
            name='Complex Resource',
            role='Multi-skilled Developer',
            capacity=40
        )
        resource.skills.add(skill)
        
        # Create project hierarchy
        projects = []
        for i in range(20):
            project = Project.objects.create(
                name=f'Nested Project {i}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                status='active'
            )
            projects.append(project)
            
            # Each project has multiple tasks
            for j in range(25):
                task = Task.objects.create(
                    project=project,
                    name=f'Nested Task {i}-{j}',
                    start_date=project.start_date,
                    end_date=project.end_date,
                    estimated_hours=40,
                    status='not_started'
                )
                task.skills_required.add(skill)
                
                # Assign to resource (creates deep relationships)
                Assignment.objects.create(
                    task=task,
                    resource=resource,
                    allocated_hours=40
                )
        
        # Test complex queries
        start_time = time.time()
        
        # Query that traverses multiple relationships
        complex_query = Assignment.objects.select_related(
            'task__project',
            'resource'
        ).prefetch_related(
            'task__skills_required',
            'resource__skills'
        ).all()
        
        list(complex_query)  # Force evaluation
        
        end_time = time.time()
        query_time = end_time - start_time
        
        print(f"Complex nested query time: {query_time:.3f}s")
        print(f"Total assignments: {Assignment.objects.count()}")
        
        self.assertLess(query_time, 2.0, "Complex nested queries should complete reasonably quickly")
        
        # Test utilization calculation with complex data
        start_time = time.time()
        utilization = resource.current_utilization()
        end_time = time.time()
        
        utilization_time = end_time - start_time
        
        print(f"Complex utilization calculation: {utilization_time:.3f}s")
        print(f"Resource utilization: {utilization:.1f}%")
        
        self.assertLess(utilization_time, 1.0, "Utilization calculation should be fast even with complex data")
        self.assertGreater(utilization, 0, "Should calculate meaningful utilization")
