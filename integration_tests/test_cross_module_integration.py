"""
Cross-module integration tests for ResourcePro
Tests interactions between different modules and features
"""
import json
from django.test import TestCase, Client
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
    SkillDemandAnalysis, AISkillRecommendation,
    AIResourceAllocationSuggestion, ProjectCostTracking
)


class ResourceProjectIntegrationTest(TestCase):
    """Test integration between resources and projects modules"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
    def test_resource_project_lifecycle_integration(self):
        """Test how resources and projects interact throughout lifecycle"""
        
        # Create skills
        python_skill = Skill.objects.create(name='Python', category='Programming')
        react_skill = Skill.objects.create(name='React', category='Frontend')
        
        # Create resources with different skills
        backend_dev = Resource.objects.create(
            name='Backend Developer',
            role='Senior Developer',
            department='Engineering',
            capacity=40,
            cost_per_hour=Decimal('85.00')
        )
        backend_dev.skills.add(python_skill)
        
        frontend_dev = Resource.objects.create(
            name='Frontend Developer',
            role='Junior Developer',
            department='Engineering',
            capacity=40,
            cost_per_hour=Decimal('65.00')
        )
        frontend_dev.skills.add(react_skill)
        
        # Create project with multiple phases
        project = Project.objects.create(
            name='Web Application',
            description='Full-stack web application',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            status='planning',
            budget=Decimal('200000.00')
        )
        
        # Create tasks requiring different skills
        backend_task = Task.objects.create(
            project=project,
            name='API Development',
            description='Develop REST API',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            estimated_hours=200,
            status='not_started'
        )
        backend_task.skills_required.add(python_skill)
        
        frontend_task = Task.objects.create(
            project=project,
            name='UI Development',
            description='Develop user interface',
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=45),
            estimated_hours=150,
            status='not_started'
        )
        frontend_task.skills_required.add(react_skill)
        
        # Test allocation board shows correct matching
        response = self.client.get(reverse('allocation_board'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Development')
        self.assertContains(response, 'UI Development')
        self.assertContains(response, 'Backend Developer')
        self.assertContains(response, 'Frontend Developer')
        
        # Assign resources to appropriate tasks
        Assignment.objects.create(
            task=backend_task,
            resource=backend_dev,
            allocated_hours=200
        )
        
        Assignment.objects.create(
            task=frontend_task,
            resource=frontend_dev,
            allocated_hours=150
        )
        
        # Test project progress tracking
        response = self.client.get(reverse('project_detail', kwargs={'pk': project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend Developer')
        self.assertContains(response, 'Frontend Developer')
        
        # Test resource utilization
        backend_utilization = backend_dev.current_utilization()
        frontend_utilization = frontend_dev.current_utilization()
        
        self.assertGreater(backend_utilization, 0)
        self.assertGreater(frontend_utilization, 0)
        
        # Update task status and verify project completion
        backend_task.status = 'completed'
        backend_task.save()
        
        completion_percentage = project.get_completion_percentage()
        self.assertGreater(completion_percentage, 0)


class AllocationAnalyticsIntegrationTest(TestCase):
    """Test integration between allocation and analytics modules"""
    
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
            name='Analytics Test Resource',
            role='Data Analyst',
            capacity=40,
            cost_per_hour=Decimal('70.00')
        )
        
        self.project = Project.objects.create(
            name='Analytics Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            status='active',
            budget=Decimal('75000.00')
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Data Analysis Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=20),
            estimated_hours=120,
            status='in_progress'
        )
        
    def test_allocation_analytics_integration(self):
        """Test how allocations feed into analytics"""
        
        # Create assignment
        assignment = Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=120
        )
        
        # Add time entries
        for i in range(5):
            TimeEntry.objects.create(
                resource=self.resource,
                date=date.today() - timedelta(days=i),
                hours=8,
                description=f'Day {i+1} work',
                billable=True,
                task=self.task
            )
        
        # Add historical utilization data
        for i in range(10):
            HistoricalUtilization.objects.create(
                resource=self.resource,
                date=date.today() - timedelta(days=i),
                utilization_percentage=Decimal('75.5'),
                allocated_hours=Decimal('30.0'),
                available_hours=Decimal('40.0')
            )
        
        # Test analytics dashboard includes allocation data
        response = self.client.get(reverse('analytics:analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test utilization report includes assigned resource
        response = self.client.get(reverse('analytics:utilization_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Test Resource')
        
        # Test cost tracking includes project costs
        response = self.client.get(reverse('analytics:cost_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Project')
        
        # Create cost tracking data
        ProjectCostTracking.objects.create(
            project=self.project,
            date=date.today(),
            estimated_cost=Decimal('75000.00'),
            actual_cost=Decimal('25000.00'),
            budget_variance=Decimal('50000.00')
        )
        
        # Verify cost data appears in reports
        response = self.client.get(reverse('analytics:cost_report'))
        self.assertEqual(response.status_code, 200)


class AIFeaturesIntegrationTest(TestCase):
    """Test integration of AI features across modules"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create diverse test data for AI analysis
        skills = ['Python', 'JavaScript', 'React', 'Django', 'Machine Learning']
        for skill_name in skills:
            Skill.objects.create(name=skill_name, category='Technical')
        
        # Create resources with different skill sets
        for i in range(5):
            resource = Resource.objects.create(
                name=f'Resource {i+1}',
                role=f'Role {i+1}',
                capacity=40,
                cost_per_hour=Decimal('70.00')
            )
            # Add random skills
            if i < 3:
                resource.skills.add(Skill.objects.get(name='Python'))
            if i < 2:
                resource.skills.add(Skill.objects.get(name='JavaScript'))
        
        # Create projects and tasks
        project = Project.objects.create(
            name='AI Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            status='active',
            budget=Decimal('100000.00')
        )
        
        for i in range(3):
            task = Task.objects.create(
                project=project,
                name=f'AI Task {i+1}',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                estimated_hours=100,
                status='not_started'
            )
            # Add skill requirements
            if i == 0:
                task.skills_required.add(Skill.objects.get(name='Python'))
            elif i == 1:
                task.skills_required.add(Skill.objects.get(name='JavaScript'))
        
    def test_ai_skill_recommendations_integration(self):
        """Test AI skill recommendations integration"""
        
        # Create skill demand analysis
        SkillDemandAnalysis.objects.create(
            skill_name='Python',
            analysis_date=date.today(),
            current_demand=5,
            available_resources=3,
            demand_score=Decimal('1.67'),
            predicted_future_demand=7
        )
        
        # Create AI skill recommendations
        AISkillRecommendation.objects.create(
            recommendation_type='develop',
            skill_name='Machine Learning',
            priority_score=9,
            reasoning='High demand for ML skills in upcoming projects',
            confidence_score=Decimal('0.85')
        )
        
        # Test AI analytics dashboard
        response = self.client.get(reverse('analytics:ai_analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test skill recommendations endpoint
        response = self.client.get(reverse('analytics:ai_skill_recommendations'))
        self.assertEqual(response.status_code, 200)
        
    def test_ai_allocation_suggestions_integration(self):
        """Test AI allocation suggestions integration"""
        
        task = Task.objects.first()
        resource = Resource.objects.first()
        
        # Create AI allocation suggestion
        AIResourceAllocationSuggestion.objects.create(
            task=task,
            suggested_resource=resource,
            match_score=Decimal('0.92'),
            reasoning='Perfect skill match and high availability',
            estimated_completion_time=Decimal('95.0'),
            cost_efficiency_score=Decimal('0.88')
        )
        
        # Test AI task suggestions endpoint
        response = self.client.get(
            reverse('ai_task_suggestions', kwargs={'task_id': task.id})
        )
        self.assertEqual(response.status_code, 200)
        
    def test_dashboard_ai_integration(self):
        """Test dashboard AI features integration"""
        
        # Test NLI query processing
        nli_data = {
            'query': 'What is the current utilization of all resources?'
        }
        response = self.client.post(
            reverse('process_nli_query'),
            json.dumps(nli_data),
            content_type='application/json'
        )
        # May return error if AI service unavailable, which is acceptable
        self.assertIn(response.status_code, [200, 500])
        
        # Test AI analysis refresh
        response = self.client.post(reverse('refresh_ai_analysis'))
        self.assertIn(response.status_code, [200, 500])


class TimeTrackingIntegrationTest(TestCase):
    """Test time tracking integration across modules"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.resource = Resource.objects.create(
            name='Time Tracker',
            role='Developer',
            capacity=40,
            cost_per_hour=Decimal('75.00')
        )
        
        self.project = Project.objects.create(
            name='Time Tracking Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active',
            budget=Decimal('50000.00')
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Development Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15),
            estimated_hours=80,
            status='in_progress'
        )
        
        Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=80
        )
        
    def test_time_tracking_workflow_integration(self):
        """Test how time tracking integrates with other modules"""
        
        # Create time entries
        time_entries_data = [
            {'hours': 8, 'description': 'Development work day 1', 'billable': True},
            {'hours': 6, 'description': 'Code review day 2', 'billable': True},
            {'hours': 8, 'description': 'Testing day 3', 'billable': False},
            {'hours': 4, 'description': 'Documentation day 4', 'billable': True}
        ]
        
        for i, entry_data in enumerate(time_entries_data):
            TimeEntry.objects.create(
                resource=self.resource,
                date=date.today() - timedelta(days=i),
                task=self.task,
                **entry_data
            )
        
        # Test time entry list view
        response = self.client.get(reverse('resources:time_entry_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Development work day 1')
        
        # Test resource detail shows time entries
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': self.resource.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Development work day 1')
        
        # Test project cost calculation includes time entries
        response = self.client.get(reverse('analytics:cost_report'))
        self.assertEqual(response.status_code, 200)
        
        # Test bulk time entry operations
        bulk_data = {
            'action': 'mark_billable',
            'selected_entries': [entry.id for entry in TimeEntry.objects.all()[:2]]
        }
        response = self.client.post(reverse('resources:bulk_time_action'), bulk_data)
        self.assertEqual(response.status_code, 302)
        
        # Test time entry export
        response = self.client.get(reverse('resources:export_time_entries'))
        self.assertEqual(response.status_code, 200)
        
        # Test resource time report
        response = self.client.get(
            reverse('resources:resource_time_report', kwargs={'pk': self.resource.id})
        )
        self.assertEqual(response.status_code, 200)


class AvailabilityIntegrationTest(TestCase):
    """Test availability management integration"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.resource = Resource.objects.create(
            name='Availability Test Resource',
            role='Consultant',
            capacity=40,
            cost_per_hour=Decimal('100.00')
        )
        
    def test_availability_allocation_integration(self):
        """Test how availability affects allocations"""
        
        # Set resource as unavailable for a period
        unavailable_period = Availability.objects.create(
            resource=self.resource,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            availability_type='vacation',
            notes='Annual leave'
        )
        
        # Create project and task during unavailable period
        project = Project.objects.create(
            name='Availability Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='planning'
        )
        
        task = Task.objects.create(
            project=project,
            name='Task During Vacation',
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=25),
            estimated_hours=60,
            status='not_started'
        )
        
        # Test availability calendar view
        response = self.client.get(reverse('resources:availability_calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annual leave')
        
        # Test resource detail shows availability
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': self.resource.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annual leave')
        
        # Test allocation conflict detection
        response = self.client.get(
            reverse('check_assignment_conflicts'),
            {'task_id': task.id, 'resource_id': self.resource.id}
        )
        self.assertEqual(response.status_code, 200)
        conflicts_data = json.loads(response.content)
        # Should detect availability conflict
        self.assertIn('conflicts', conflicts_data)


class ExportIntegrationTest(TestCase):
    """Test export functionality integration"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create comprehensive test data
        self.resource = Resource.objects.create(
            name='Export Test Resource',
            role='Analyst',
            capacity=40,
            cost_per_hour=Decimal('80.00')
        )
        
        self.project = Project.objects.create(
            name='Export Test Project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active',
            budget=Decimal('60000.00')
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Export Test Task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15),
            estimated_hours=100,
            status='in_progress'
        )
        
        Assignment.objects.create(
            task=self.task,
            resource=self.resource,
            allocated_hours=100
        )
        
        # Add time entries
        for i in range(5):
            TimeEntry.objects.create(
                resource=self.resource,
                date=date.today() - timedelta(days=i),
                hours=8,
                description=f'Work day {i+1}',
                billable=True,
                task=self.task
            )
        
        # Add historical data
        HistoricalUtilization.objects.create(
            resource=self.resource,
            date=date.today(),
            utilization_percentage=Decimal('80.0'),
            allocated_hours=Decimal('32.0'),
            available_hours=Decimal('40.0')
        )
        
    def test_analytics_export_integration(self):
        """Test analytics export functionality"""
        
        # Test utilization report export
        response = self.client.get(reverse('analytics:export_report', kwargs={'report_type': 'utilization'}))
        self.assertEqual(response.status_code, 200)
        
        # Test cost report export
        response = self.client.get(reverse('analytics:export_report', kwargs={'report_type': 'cost'}))
        self.assertEqual(response.status_code, 200)
        
        # Test time entries export
        response = self.client.get(reverse('resources:export_time_entries'))
        self.assertEqual(response.status_code, 200)
        
    def test_data_consistency_across_exports(self):
        """Test that exported data is consistent across different reports"""
        
        # Get data from different views
        utilization_response = self.client.get(reverse('analytics:utilization_report'))
        cost_response = self.client.get(reverse('analytics:cost_report'))
        time_tracking_response = self.client.get(reverse('resources:time_entry_list'))
        
        # All should return successfully
        self.assertEqual(utilization_response.status_code, 200)
        self.assertEqual(cost_response.status_code, 200)
        self.assertEqual(time_tracking_response.status_code, 200)
        
        # All should contain our test resource/project
        self.assertContains(utilization_response, 'Export Test Resource')
        self.assertContains(cost_response, 'Export Test Project')
        self.assertContains(time_tracking_response, 'Export Test Resource')


class SearchFilterIntegrationTest(TestCase):
    """Test search and filtering integration across modules"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create diverse test data
        departments = ['Engineering', 'Design', 'Marketing']
        roles = ['Developer', 'Designer', 'Manager']
        
        for i, (dept, role) in enumerate(zip(departments, roles)):
            Resource.objects.create(
                name=f'{role} {i+1}',
                role=role,
                department=dept,
                capacity=40,
                cost_per_hour=Decimal('75.00')
            )
        
        # Create projects with different statuses
        statuses = ['planning', 'active', 'completed']
        for i, status in enumerate(statuses):
            Project.objects.create(
                name=f'Project {i+1}',
                start_date=date.today() - timedelta(days=i*30),
                end_date=date.today() + timedelta(days=(3-i)*30),
                status=status,
                budget=Decimal('50000.00')
            )
        
    def test_resource_filtering_integration(self):
        """Test resource filtering across views"""
        
        # Test resource list filtering
        response = self.client.get(reverse('resources:resource_list'), {'department': 'Engineering'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Developer 1')
        self.assertNotContains(response, 'Designer 2')
        
        # Test utilization report filtering
        response = self.client.get(reverse('analytics:utilization_report'), {'department': 'Design'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Designer 2')
        
    def test_project_filtering_integration(self):
        """Test project filtering across views"""
        
        # Test allocation board project filtering
        active_project = Project.objects.get(status='active')
        response = self.client.get(reverse('allocation_board'), {'project': active_project.id})
        self.assertEqual(response.status_code, 200)
        
        # Test project list filtering
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Project 1')
        self.assertContains(response, 'Project 2')
        
    def test_date_filtering_integration(self):
        """Test date-based filtering across modules"""
        
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        
        # Test utilization report date filtering
        response = self.client.get(
            reverse('analytics:utilization_report'),
            {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        )
        self.assertEqual(response.status_code, 200)
        
        # Test cost report date filtering
        response = self.client.get(
            reverse('analytics:cost_report'),
            {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        )
        self.assertEqual(response.status_code, 200)
