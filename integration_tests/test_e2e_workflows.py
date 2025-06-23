"""
End-to-end workflow tests for ResourcePro
Tests complete user scenarios from start to finish
"""
from django.test import TestCase, LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db import models
from datetime import timedelta, date
from decimal import Decimal
import time

from resources.models import Resource, Skill, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment


class ProjectDeliveryE2ETest(TestCase):
    """
    End-to-end test for complete project delivery workflow
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='projectmanager',
            email='pm@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_complete_project_delivery_workflow(self):
        """Test complete project delivery from planning to completion"""
        
        # Phase 1: Project Setup
        print("Phase 1: Setting up project...")
        
        # Create required skills
        skills_data = [
            {'name': 'Python', 'category': 'Backend'},
            {'name': 'React', 'category': 'Frontend'},
            {'name': 'PostgreSQL', 'category': 'Database'},
            {'name': 'DevOps', 'category': 'Infrastructure'}
        ]
        
        skills = {}
        for skill_data in skills_data:
            response = self.client.post(reverse('resources:create_skill'), skill_data)
            self.assertEqual(response.status_code, 302)
            skills[skill_data['name']] = Skill.objects.get(name=skill_data['name'])
        
        # Create team members
        team_data = [
            {
                'name': 'Alice Backend',
                'role': 'Senior Backend Developer',
                'department': 'Engineering',
                'capacity': 40,
                'cost_per_hour': '95.00',
                'email': 'alice@company.com',
                'skills': ['Python', 'PostgreSQL']
            },
            {
                'name': 'Bob Frontend',
                'role': 'Frontend Developer',
                'department': 'Engineering',
                'capacity': 40,
                'cost_per_hour': '85.00',
                'email': 'bob@company.com',
                'skills': ['React']
            },
            {
                'name': 'Charlie DevOps',
                'role': 'DevOps Engineer',
                'department': 'Infrastructure',
                'capacity': 40,
                'cost_per_hour': '90.00',
                'email': 'charlie@company.com',
                'skills': ['DevOps']
            }
        ]
        
        team_members = {}
        for member_data in team_data:
            member_skills = member_data.pop('skills')
            response = self.client.post(reverse('resources:resource_create'), member_data)
            self.assertEqual(response.status_code, 302)
            
            member = Resource.objects.get(name=member_data['name'])
            for skill_name in member_skills:
                member.skills.add(skills[skill_name])
            team_members[member_data['name']] = member
        
        # Create project
        project_data = {
            'name': 'E-commerce Platform v2.0',
            'description': 'Complete rewrite of e-commerce platform with modern stack',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=120)).strftime('%Y-%m-%d'),
            'status': 'planning',
            'priority': 5,
            'budget': '300000.00'
        }
        
        response = self.client.post(reverse('project_create'), project_data)
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name='E-commerce Platform v2.0')
        
        # Phase 2: Task Planning and Assignment
        print("Phase 2: Planning and assigning tasks...")
        
        # Create project tasks with dependencies
        tasks_data = [
            {
                'name': 'Database Design',
                'description': 'Design database schema and relationships',
                'start_date': date.today(),
                'duration': 14,
                'estimated_hours': 80,
                'required_skills': ['PostgreSQL'],
                'assigned_to': 'Alice Backend'
            },
            {
                'name': 'API Development',
                'description': 'Develop REST API endpoints',
                'start_date': date.today() + timedelta(days=7),
                'duration': 35,
                'estimated_hours': 200,
                'required_skills': ['Python'],
                'assigned_to': 'Alice Backend'
            },
            {
                'name': 'Frontend Components',
                'description': 'Develop reusable React components',
                'start_date': date.today() + timedelta(days=21),
                'duration': 28,
                'estimated_hours': 160,
                'required_skills': ['React'],
                'assigned_to': 'Bob Frontend'
            },
            {
                'name': 'Infrastructure Setup',
                'description': 'Set up CI/CD and deployment infrastructure',
                'start_date': date.today() + timedelta(days=14),
                'duration': 21,
                'estimated_hours': 120,
                'required_skills': ['DevOps'],
                'assigned_to': 'Charlie DevOps'
            },
            {
                'name': 'Integration Testing',
                'description': 'End-to-end integration testing',
                'start_date': date.today() + timedelta(days=70),
                'duration': 14,
                'estimated_hours': 80,
                'required_skills': ['Python', 'React'],
                'assigned_to': 'Alice Backend'
            }
        ]
        
        created_tasks = {}
        for task_data in tasks_data:
            # Extract custom fields
            duration = task_data.pop('duration')
            required_skills = task_data.pop('required_skills')
            assigned_to = task_data.pop('assigned_to')
            
            # Prepare task data for creation
            task_create_data = {
                'project': project.id,
                'name': task_data['name'],
                'description': task_data['description'],
                'start_date': task_data['start_date'].strftime('%Y-%m-%d'),
                'end_date': (task_data['start_date'] + timedelta(days=duration)).strftime('%Y-%m-%d'),
                'estimated_hours': task_data['estimated_hours'],
                'status': 'not_started',
                'priority': 4
            }
            
            response = self.client.post(reverse('task_create'), task_create_data)
            self.assertEqual(response.status_code, 302)
            
            task = Task.objects.get(name=task_data['name'], project=project)
            
            # Add required skills
            for skill_name in required_skills:
                task.skills_required.add(skills[skill_name])
            
            # Create assignment
            assignment_data = {
                'task_id': task.id,
                'resource_id': team_members[assigned_to].id,
                'allocated_hours': task_data['estimated_hours']
            }
            
            response = self.client.post(
                reverse('assign_task'),
                assignment_data,
                content_type='application/json'
            )
            
            created_tasks[task_data['name']] = task
        
        # Phase 3: Project Execution and Tracking
        print("Phase 3: Executing project and tracking progress...")
        
        # Simulate project execution over time
        execution_phases = [
            {
                'day': 0,
                'activities': [
                    {'task': 'Database Design', 'resource': 'Alice Backend', 'hours': 8, 'description': 'Initial schema design'},
                    {'task': 'Infrastructure Setup', 'resource': 'Charlie DevOps', 'hours': 6, 'description': 'Environment setup'}
                ]
            },
            {
                'day': 7,
                'activities': [
                    {'task': 'Database Design', 'resource': 'Alice Backend', 'hours': 8, 'description': 'Database optimization'},
                    {'task': 'API Development', 'resource': 'Alice Backend', 'hours': 2, 'description': 'API planning'},
                    {'task': 'Infrastructure Setup', 'resource': 'Charlie DevOps', 'hours': 8, 'description': 'CI/CD pipeline'}
                ]
            },
            {
                'day': 14,
                'activities': [
                    {'task': 'API Development', 'resource': 'Alice Backend', 'hours': 8, 'description': 'Core API endpoints'},
                    {'task': 'Infrastructure Setup', 'resource': 'Charlie DevOps', 'hours': 8, 'description': 'Deployment automation'}
                ]
            },
            {
                'day': 21,
                'activities': [
                    {'task': 'API Development', 'resource': 'Alice Backend', 'hours': 8, 'description': 'API testing and refinement'},
                    {'task': 'Frontend Components', 'resource': 'Bob Frontend', 'hours': 8, 'description': 'Base component library'}
                ]
            },
            {
                'day': 35,
                'activities': [
                    {'task': 'Frontend Components', 'resource': 'Bob Frontend', 'hours': 8, 'description': 'Advanced components'},
                    {'task': 'API Development', 'resource': 'Alice Backend', 'hours': 6, 'description': 'API documentation'}
                ]
            }
        ]
        
        for phase in execution_phases:
            current_date = date.today() + timedelta(days=phase['day'])
            
            for activity in phase['activities']:
                # Create time entry
                time_entry_data = {
                    'resource': team_members[activity['resource']].id,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'hours': activity['hours'],
                    'description': activity['description'],
                    'billable': True,
                    'task': created_tasks[activity['task']].id
                }
                
                response = self.client.post(reverse('resources:time_entry_create'), time_entry_data)
                self.assertEqual(response.status_code, 302)
        
        # Update task statuses based on progress
        status_updates = [
            {'task': 'Database Design', 'status': 'completed'},
            {'task': 'API Development', 'status': 'in_progress'},
            {'task': 'Frontend Components', 'status': 'in_progress'},
            {'task': 'Infrastructure Setup', 'status': 'in_progress'},
            {'task': 'Integration Testing', 'status': 'not_started'}
        ]
        
        for update in status_updates:
            task = created_tasks[update['task']]
            task.status = update['status']
            task.save()
        
        # Phase 4: Monitoring and Analytics
        print("Phase 4: Monitoring project progress...")
        
        # Check dashboard shows correct information
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'E-commerce Platform v2.0')
        
        # Check allocation board
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Backend')
        self.assertContains(response, 'Bob Frontend')
        self.assertContains(response, 'Charlie DevOps')
        
        # Check project detail page
        response = self.client.get(reverse('project_detail', kwargs={'pk': project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Database Design')
        self.assertContains(response, 'API Development')
        
        # Check analytics
        response = self.client.get(reverse('analytics:analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('analytics:utilization_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Backend')
        
        response = self.client.get(reverse('analytics:cost_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'E-commerce Platform v2.0')
        
        # Phase 5: Verification and Completion
        print("Phase 5: Verifying project completion...")
        
        # Verify data integrity
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 5)
        self.assertEqual(Resource.objects.count(), 3)
        self.assertEqual(Assignment.objects.count(), 5)
        self.assertGreater(TimeEntry.objects.count(), 0)
        
        # Verify resource utilizations
        for resource in team_members.values():
            utilization = resource.current_utilization()
            self.assertGreaterEqual(utilization, 0)
            self.assertLessEqual(utilization, 200)  # Allow for over-allocation
        
        # Verify project completion percentage
        completion = project.get_completion_percentage()
        self.assertGreater(completion, 0)
        self.assertLessEqual(completion, 100)
        
        # Verify time tracking totals
        total_hours = TimeEntry.objects.aggregate(
            total=models.Sum('hours')
        )['total'] or 0
        self.assertGreater(total_hours, 0)
        
        print(f"Project delivery test completed successfully!")
        print(f"- Created {Project.objects.count()} project")
        print(f"- Created {Task.objects.count()} tasks")
        print(f"- Created {Resource.objects.count()} resources")
        print(f"- Created {Assignment.objects.count()} assignments")
        print(f"- Tracked {TimeEntry.objects.count()} time entries")
        print(f"- Total hours logged: {total_hours}")
        print(f"- Project completion: {completion}%")


class ResourceOnboardingE2ETest(TestCase):
    """
    End-to-end test for resource onboarding workflow
    """
    
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        self.client.force_login(self.manager)
        
    def test_complete_resource_onboarding(self):
        """Test complete resource onboarding process"""
        
        print("Testing resource onboarding workflow...")
        
        # Step 1: Create necessary skills
        skills_to_create = [
            {'name': 'Java', 'category': 'Programming'},
            {'name': 'Spring Boot', 'category': 'Framework'},
            {'name': 'Kubernetes', 'category': 'DevOps'},
            {'name': 'Team Leadership', 'category': 'Soft Skills'}
        ]
        
        created_skills = {}
        for skill_data in skills_to_create:
            response = self.client.post(reverse('resources:create_skill'), skill_data)
            self.assertEqual(response.status_code, 302)
            created_skills[skill_data['name']] = Skill.objects.get(name=skill_data['name'])
        
        # Step 2: Create new resource profile
        resource_data = {
            'name': 'John Senior Developer',
            'role': 'Senior Software Engineer',
            'department': 'Engineering',
            'capacity': 40,
            'cost_per_hour': '110.00',
            'email': 'john.senior@company.com'
        }
        
        response = self.client.post(reverse('resources:resource_create'), resource_data)
        self.assertEqual(response.status_code, 302)
        
        resource = Resource.objects.get(name='John Senior Developer')
        
        # Step 3: Assign skills to resource
        resource.skills.add(created_skills['Java'])
        resource.skills.add(created_skills['Spring Boot'])
        resource.skills.add(created_skills['Kubernetes'])
        resource.skills.add(created_skills['Team Leadership'])
        
        # Step 4: Set initial availability
        availability_data = {
            'resource': resource.id,
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'availability_type': 'available',
            'notes': 'Available for assignment after onboarding'
        }
        
        response = self.client.post(reverse('resources:availability_create'), availability_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 5: Create onboarding project and tasks
        onboarding_project_data = {
            'name': 'John Senior Developer - Onboarding',
            'description': 'Onboarding activities for new team member',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'status': 'active',
            'priority': 3,
            'budget': '5000.00'
        }
        
        response = self.client.post(reverse('project_create'), onboarding_project_data)
        self.assertEqual(response.status_code, 302)
        
        onboarding_project = Project.objects.get(name='John Senior Developer - Onboarding')
        
        # Create onboarding tasks
        onboarding_tasks = [
            {
                'name': 'System Setup',
                'description': 'Set up development environment and tools',
                'duration': 2,
                'estimated_hours': 16
            },
            {
                'name': 'Code Review Training',
                'description': 'Learn team code review processes',
                'duration': 3,
                'estimated_hours': 24
            },
            {
                'name': 'Architecture Overview',
                'description': 'Understand system architecture',
                'duration': 5,
                'estimated_hours': 40
            },
            {
                'name': 'First Assignment',
                'description': 'Complete first small development task',
                'duration': 4,
                'estimated_hours': 32
            }
        ]
        
        for i, task_data in enumerate(onboarding_tasks):
            task_create_data = {
                'project': onboarding_project.id,
                'name': task_data['name'],
                'description': task_data['description'],
                'start_date': (date.today() + timedelta(days=i*2)).strftime('%Y-%m-%d'),
                'end_date': (date.today() + timedelta(days=i*2 + task_data['duration'])).strftime('%Y-%m-%d'),
                'estimated_hours': task_data['estimated_hours'],
                'status': 'not_started',
                'priority': 3
            }
            
            response = self.client.post(reverse('task_create'), task_create_data)
            self.assertEqual(response.status_code, 302)
            
            task = Task.objects.get(name=task_data['name'], project=onboarding_project)
            
            # Assign task to new resource
            assignment_data = {
                'task_id': task.id,
                'resource_id': resource.id,
                'allocated_hours': task_data['estimated_hours']
            }
            
            response = self.client.post(
                reverse('assign_task'),
                assignment_data,
                content_type='application/json'
            )
        
        # Step 6: Track onboarding progress
        # Simulate first few days of onboarding
        onboarding_activities = [
            {'day': 0, 'task': 'System Setup', 'hours': 8, 'description': 'Laptop setup and software installation'},
            {'day': 1, 'task': 'System Setup', 'hours': 8, 'description': 'IDE configuration and access setup'},
            {'day': 2, 'task': 'Code Review Training', 'hours': 8, 'description': 'Code review process training'},
            {'day': 3, 'task': 'Code Review Training', 'hours': 8, 'description': 'Practice code reviews'},
            {'day': 4, 'task': 'Architecture Overview', 'hours': 8, 'description': 'System architecture study'}
        ]
        
        for activity in onboarding_activities:
            activity_date = date.today() + timedelta(days=activity['day'])
            task = Task.objects.get(name=activity['task'], project=onboarding_project)
            
            time_entry_data = {
                'resource': resource.id,
                'date': activity_date.strftime('%Y-%m-%d'),
                'hours': activity['hours'],
                'description': activity['description'],
                'billable': False,  # Onboarding is typically non-billable
                'task': task.id
            }
            
            response = self.client.post(reverse('resources:time_entry_create'), time_entry_data)
            self.assertEqual(response.status_code, 302)
        
        # Update task statuses
        Task.objects.filter(name='System Setup', project=onboarding_project).update(status='completed')
        Task.objects.filter(name='Code Review Training', project=onboarding_project).update(status='completed')
        Task.objects.filter(name='Architecture Overview', project=onboarding_project).update(status='in_progress')
        
        # Step 7: Verify onboarding progress
        # Check resource detail page
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': resource.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Senior Developer')
        self.assertContains(response, 'Java')
        self.assertContains(response, 'Spring Boot')
        
        # Check project progress
        response = self.client.get(reverse('project_detail', kwargs={'pk': onboarding_project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'System Setup')
        
        # Check time tracking
        response = self.client.get(reverse('resources:time_entry_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop setup')
        
        # Check utilization
        utilization = resource.current_utilization()
        self.assertGreater(utilization, 0)
        
        # Verify onboarding completion metrics
        total_onboarding_hours = TimeEntry.objects.filter(
            resource=resource,
            task__project=onboarding_project
        ).aggregate(total=models.Sum('hours'))['total'] or 0
        
        completion_percentage = onboarding_project.get_completion_percentage()
        
        print(f"Resource onboarding test completed successfully!")
        print(f"- Resource created: {resource.name}")
        print(f"- Skills assigned: {resource.skills.count()}")
        print(f"- Onboarding tasks: {onboarding_project.tasks.count()}")
        print(f"- Hours logged: {total_onboarding_hours}")
        print(f"- Onboarding completion: {completion_percentage}%")
        print(f"- Current utilization: {utilization}%")


class CapacityPlanningE2ETest(TestCase):
    """
    End-to-end test for capacity planning scenario
    """
    
    def setUp(self):
        self.planner = User.objects.create_user(
            username='planner',
            email='planner@example.com',
            password='testpass123'
        )
        self.client.force_login(self.planner)
        
    def test_capacity_planning_workflow(self):
        """Test complete capacity planning workflow"""
        
        print("Testing capacity planning workflow...")
        
        # Step 1: Create team with different capacities
        team_setup = [
            {'name': 'Full-time Dev 1', 'capacity': 40, 'cost': '80.00', 'role': 'Senior Developer'},
            {'name': 'Full-time Dev 2', 'capacity': 40, 'cost': '75.00', 'role': 'Developer'},
            {'name': 'Part-time Dev', 'capacity': 20, 'cost': '70.00', 'role': 'Junior Developer'},
            {'name': 'Consultant', 'capacity': 30, 'cost': '120.00', 'role': 'Technical Consultant'},
            {'name': 'Designer', 'capacity': 40, 'cost': '65.00', 'role': 'UI/UX Designer'}
        ]
        
        team_resources = {}
        for member in team_setup:
            resource_data = {
                'name': member['name'],
                'role': member['role'],
                'department': 'Product Development',
                'capacity': member['capacity'],
                'cost_per_hour': member['cost'],
                'email': f"{member['name'].replace(' ', '.').lower()}@company.com"
            }
            
            response = self.client.post(reverse('resources:resource_create'), resource_data)
            self.assertEqual(response.status_code, 302)
            team_resources[member['name']] = Resource.objects.get(name=member['name'])
        
        # Step 2: Create multiple competing projects
        projects_data = [
            {
                'name': 'Mobile App Redesign',
                'priority': 5,
                'duration': 60,
                'budget': '150000.00',
                'tasks': [
                    {'name': 'UI/UX Design', 'hours': 120, 'resource': 'Designer'},
                    {'name': 'Backend API', 'hours': 160, 'resource': 'Full-time Dev 1'},
                    {'name': 'Mobile Frontend', 'hours': 140, 'resource': 'Full-time Dev 2'},
                    {'name': 'Testing', 'hours': 80, 'resource': 'Part-time Dev'}
                ]
            },
            {
                'name': 'Data Analytics Platform',
                'priority': 4,
                'duration': 90,
                'budget': '200000.00',
                'tasks': [
                    {'name': 'Architecture Design', 'hours': 60, 'resource': 'Consultant'},
                    {'name': 'Data Pipeline', 'hours': 180, 'resource': 'Full-time Dev 1'},
                    {'name': 'Analytics Dashboard', 'hours': 160, 'resource': 'Full-time Dev 2'},
                    {'name': 'Data Visualization', 'hours': 100, 'resource': 'Designer'}
                ]
            },
            {
                'name': 'Legacy System Migration',
                'priority': 3,
                'duration': 120,
                'budget': '250000.00',
                'tasks': [
                    {'name': 'Migration Planning', 'hours': 80, 'resource': 'Consultant'},
                    {'name': 'Data Migration', 'hours': 200, 'resource': 'Full-time Dev 1'},
                    {'name': 'System Integration', 'hours': 180, 'resource': 'Full-time Dev 2'},
                    {'name': 'Testing & Validation', 'hours': 120, 'resource': 'Part-time Dev'}
                ]
            }
        ]
        
        created_projects = {}
        all_tasks = []
        
        for project_data in projects_data:
            # Create project
            project_create_data = {
                'name': project_data['name'],
                'description': f"Project: {project_data['name']}",
                'start_date': date.today().strftime('%Y-%m-%d'),
                'end_date': (date.today() + timedelta(days=project_data['duration'])).strftime('%Y-%m-%d'),
                'status': 'planning',
                'priority': project_data['priority'],
                'budget': project_data['budget']
            }
            
            response = self.client.post(reverse('project_create'), project_create_data)
            self.assertEqual(response.status_code, 302)
            
            project = Project.objects.get(name=project_data['name'])
            created_projects[project_data['name']] = project
            
            # Create tasks for project
            for task_data in project_data['tasks']:
                task_create_data = {
                    'project': project.id,
                    'name': task_data['name'],
                    'description': f"Task: {task_data['name']}",
                    'start_date': date.today().strftime('%Y-%m-%d'),
                    'end_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'estimated_hours': task_data['hours'],
                    'status': 'not_started',
                    'priority': project_data['priority']
                }
                
                response = self.client.post(reverse('task_create'), task_create_data)
                self.assertEqual(response.status_code, 302)
                
                task = Task.objects.get(name=task_data['name'], project=project)
                all_tasks.append({
                    'task': task,
                    'resource_name': task_data['resource'],
                    'hours': task_data['hours']
                })
        
        # Step 3: Analyze capacity constraints
        print("Analyzing capacity constraints...")
        
        # Check allocation board for conflicts
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        
        # Calculate total demand vs capacity
        resource_demand = {}
        for task_info in all_tasks:
            resource_name = task_info['resource_name']
            hours = task_info['hours']
            
            if resource_name not in resource_demand:
                resource_demand[resource_name] = 0
            resource_demand[resource_name] += hours
        
        # Check for over-allocation
        over_allocated_resources = []
        for resource_name, total_demand in resource_demand.items():
            resource = team_resources[resource_name]
            max_capacity = resource.capacity * 4 * 4  # 4 weeks capacity
            
            if total_demand > max_capacity:
                over_allocated_resources.append({
                    'resource': resource_name,
                    'demand': total_demand,
                    'capacity': max_capacity,
                    'over_allocation': total_demand - max_capacity
                })
        
        print(f"Found {len(over_allocated_resources)} over-allocated resources")
        
        # Step 4: Implement capacity balancing strategy
        print("Implementing capacity balancing...")
        
        # Strategy 1: Assign high-priority tasks first
        high_priority_tasks = [t for t in all_tasks if Task.objects.get(id=t['task'].id).priority >= 4]
        
        for task_info in high_priority_tasks:
            resource = team_resources[task_info['resource_name']]
            assignment_data = {
                'task_id': task_info['task'].id,
                'resource_id': resource.id,
                'allocated_hours': task_info['hours']
            }
            
            response = self.client.post(
                reverse('assign_task'),
                assignment_data,
                content_type='application/json'
            )
            
            # Check for conflicts
            if response.status_code == 200:
                print(f"Assigned {task_info['task'].name} to {resource.name}")
            else:
                print(f"Conflict assigning {task_info['task'].name} to {resource.name}")
        
        # Step 5: Monitor and report capacity utilization
        print("Monitoring capacity utilization...")
        
        # Check resource utilization
        for resource_name, resource in team_resources.items():
            utilization = resource.current_utilization()
            print(f"{resource_name}: {utilization:.1f}% utilized")
        
        # Generate analytics reports
        response = self.client.get(reverse('analytics:utilization_report'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('analytics:cost_report'))
        self.assertEqual(response.status_code, 200)
        
        # Step 6: Verify capacity planning results
        print("Verifying capacity planning results...")
        
        # Count assignments
        total_assignments = Assignment.objects.count()
        total_allocated_hours = Assignment.objects.aggregate(
            total=models.Sum('allocated_hours')
        )['total'] or 0
        
        # Calculate team utilization
        team_utilizations = []
        for resource in team_resources.values():
            utilization = resource.current_utilization()
            team_utilizations.append(utilization)
        
        avg_utilization = sum(team_utilizations) / len(team_utilizations) if team_utilizations else 0
        
        print(f"Capacity planning test completed!")
        print(f"- Projects created: {len(created_projects)}")
        print(f"- Tasks created: {len(all_tasks)}")
        print(f"- Resources: {len(team_resources)}")
        print(f"- Assignments: {total_assignments}")
        print(f"- Total allocated hours: {total_allocated_hours}")
        print(f"- Average team utilization: {avg_utilization:.1f}%")
        print(f"- Over-allocated resources: {len(over_allocated_resources)}")
        
        # Verify system handles capacity constraints
        self.assertGreater(total_assignments, 0)
        self.assertGreater(total_allocated_hours, 0)
        self.assertGreaterEqual(avg_utilization, 0)
        self.assertLessEqual(avg_utilization, 200)  # Allow for reasonable over-allocation
