from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import json
from decimal import Decimal

from .models import (
    DashboardAIAnalysis, RiskCategory, DynamicRisk, 
    AIRecommendation, AISearchQuery, AISearchResult
)
from projects.models import Project, Task
from resources.models import Resource, Skill
from allocation.models import Assignment


class DashboardAIAnalysisModelTest(TestCase):
    """Test cases for DashboardAIAnalysis model"""
    
    def setUp(self):
        self.analysis_data = {
            'metrics': {
                'total_projects': 5,
                'active_tasks': 12,
                'resource_utilization': 85.5
            },
            'trends': ['increasing_utilization', 'deadline_pressure']
        }
        
        self.risks = [
            {'id': 'risk_1', 'type': 'resource', 'severity': 'high'},
            {'id': 'risk_2', 'type': 'timeline', 'severity': 'medium'}
        ]
        
        self.recommendations = [
            {'id': 'rec_1', 'action': 'hire_contractor', 'priority': 'high'},
            {'id': 'rec_2', 'action': 'adjust_timeline', 'priority': 'medium'}
        ]
        
        self.analysis = DashboardAIAnalysis.objects.create(
            analysis_type='daily_briefing',
            analysis_data=self.analysis_data,
            summary="Daily briefing showing high resource utilization",
            risks=self.risks,
            recommendations=self.recommendations,
            confidence_score=0.85
        )
    
    def test_analysis_creation(self):
        """Test analysis creation and basic properties"""
        expected_str = f"Daily Briefing - {self.analysis.created_at.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(self.analysis), expected_str)
        self.assertEqual(self.analysis.analysis_type, 'daily_briefing')
        self.assertEqual(self.analysis.confidence_score, 0.85)
        self.assertTrue(self.analysis.is_active)
    
    def test_analysis_json_fields(self):
        """Test JSON field storage and retrieval"""
        self.assertEqual(self.analysis.analysis_data['metrics']['total_projects'], 5)
        self.assertEqual(len(self.analysis.risks), 2)
        self.assertEqual(len(self.analysis.recommendations), 2)
        self.assertEqual(self.analysis.risks[0]['severity'], 'high')
    
    def test_analysis_types(self):
        """Test different analysis types"""
        risk_analysis = DashboardAIAnalysis.objects.create(
            analysis_type='risk_assessment',
            summary="Risk assessment analysis",
            confidence_score=0.75
        )
        
        recommendations_analysis = DashboardAIAnalysis.objects.create(
            analysis_type='recommendations',
            summary="Strategic recommendations",
            confidence_score=0.90
        )
        
        self.assertEqual(risk_analysis.analysis_type, 'risk_assessment')
        self.assertEqual(recommendations_analysis.analysis_type, 'recommendations')
    
    def test_analysis_ordering(self):
        """Test analysis ordering by created_at desc"""
        analysis2 = DashboardAIAnalysis.objects.create(
            analysis_type='risk_assessment',
            summary="Second analysis"
        )
        
        analyses = list(DashboardAIAnalysis.objects.all())
        self.assertEqual(analyses[0], analysis2)  # Most recent first
        self.assertEqual(analyses[1], self.analysis)


class RiskCategoryModelTest(TestCase):
    """Test cases for RiskCategory model"""
    
    def setUp(self):
        self.risk_category = RiskCategory.objects.create(
            name="Resource Shortage",
            risk_type="resource",
            description="Insufficient resources for project demands",
            severity_level=4,
            color="#FF6B6B"
        )
    
    def test_risk_category_creation(self):
        """Test risk category creation"""
        self.assertEqual(str(self.risk_category), "Resource Shortage")
        self.assertEqual(self.risk_category.risk_type, "resource")
        self.assertEqual(self.risk_category.severity_level, 4)
        self.assertEqual(self.risk_category.color, "#FF6B6B")
    
    def test_risk_category_defaults(self):
        """Test default values"""
        category = RiskCategory.objects.create(
            name="Default Category",
            risk_type="operational"
        )
        
        self.assertEqual(category.severity_level, 3)
        self.assertEqual(category.color, "#FFA500")
        self.assertTrue(category.is_active)
    
    def test_risk_type_choices(self):
        """Test risk type choices"""
        valid_types = [
            'resource', 'technical', 'external', 'team', 
            'business', 'operational', 'financial', 'timeline',
            'scope', 'quality'
        ]
        
        for risk_type in valid_types:
            category = RiskCategory.objects.create(
                name=f"Test {risk_type}",
                risk_type=risk_type
            )
            self.assertEqual(category.risk_type, risk_type)


class DynamicRiskModelTest(TestCase):
    """Test cases for DynamicRisk model"""
    
    def setUp(self):
        self.risk_category = RiskCategory.objects.create(
            name="Resource Risk",
            risk_type="resource"
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.resource = Resource.objects.create(
            name="Test Resource",
            role="Developer"
        )
        
        self.dynamic_risk = DynamicRisk.objects.create(
            risk_id="risk_001",
            category=self.risk_category,
            title="Resource Overallocation",
            description="Resource allocated beyond capacity",
            severity_score=0.8,
            impact_score=0.7,
            likelihood_score=0.9,
            project=self.project,
            resource=self.resource,
            detection_algorithm="capacity_analysis",
            risk_data={'utilization': 150, 'capacity': 40}
        )
    
    def test_dynamic_risk_creation(self):
        """Test dynamic risk creation"""
        expected_str = "risk_001 - Resource Overallocation (High)"
        self.assertEqual(str(self.dynamic_risk), expected_str)
        self.assertEqual(self.dynamic_risk.risk_id, "risk_001")
        self.assertEqual(self.dynamic_risk.severity_score, 0.8)
    
    def test_risk_severity_levels(self):
        """Test risk severity level calculation"""
        # High severity (> 0.7)
        high_risk = DynamicRisk.objects.create(
            risk_id="high_risk",
            category=self.risk_category,
            title="High Risk",
            severity_score=0.9
        )
        self.assertEqual(high_risk.get_severity_level(), "High")
        
        # Medium severity (0.4 - 0.7)
        medium_risk = DynamicRisk.objects.create(
            risk_id="medium_risk",
            category=self.risk_category,
            title="Medium Risk",
            severity_score=0.5
        )
        self.assertEqual(medium_risk.get_severity_level(), "Medium")
        
        # Low severity (< 0.4)
        low_risk = DynamicRisk.objects.create(
            risk_id="low_risk",
            category=self.risk_category,
            title="Low Risk",
            severity_score=0.2
        )
        self.assertEqual(low_risk.get_severity_level(), "Low")
    
    def test_risk_data_json_field(self):
        """Test risk data JSON field"""
        self.assertEqual(self.dynamic_risk.risk_data['utilization'], 150)
        self.assertEqual(self.dynamic_risk.risk_data['capacity'], 40)
    
    def test_risk_relationships(self):
        """Test risk relationships with project and resource"""
        self.assertEqual(self.dynamic_risk.project, self.project)
        self.assertEqual(self.dynamic_risk.resource, self.resource)
        self.assertEqual(self.dynamic_risk.category, self.risk_category)


class AIRecommendationModelTest(TestCase):
    """Test cases for AIRecommendation model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.recommendation = AIRecommendation.objects.create(
            recommendation_id="rec_001",
            title="Hire Additional Developer",
            description="Consider hiring a senior developer to meet project deadlines",
            recommendation_type="resource_planning",
            priority="high",
            confidence_score=0.85,
            estimated_impact="Reduces project risk by 30%",
            implementation_effort="high",
            status="pending",
            created_by=self.user,
            recommendation_data={
                'skill_requirements': ['Python', 'Django'],
                'estimated_cost': 50000,
                'timeline': '2 weeks'
            }
        )
    
    def test_recommendation_creation(self):
        """Test recommendation creation"""
        expected_str = "rec_001 - Hire Additional Developer (High Priority)"
        self.assertEqual(str(self.recommendation), expected_str)
        self.assertEqual(self.recommendation.recommendation_type, "resource_planning")
        self.assertEqual(self.recommendation.priority, "high")
        self.assertEqual(self.recommendation.confidence_score, 0.85)
    
    def test_recommendation_status_choices(self):
        """Test recommendation status choices"""
        statuses = ['pending', 'accepted', 'rejected', 'implemented']
        
        for status in statuses:
            rec = AIRecommendation.objects.create(
                recommendation_id=f"rec_{status}",
                title=f"Test {status}",
                status=status
            )
            self.assertEqual(rec.status, status)
    
    def test_recommendation_priority_choices(self):
        """Test recommendation priority choices"""
        priorities = ['low', 'medium', 'high', 'critical']
        
        for priority in priorities:
            rec = AIRecommendation.objects.create(
                recommendation_id=f"rec_{priority}",
                title=f"Test {priority}",
                priority=priority
            )
            self.assertEqual(rec.priority, priority)
    
    def test_recommendation_data_field(self):
        """Test recommendation data JSON field"""
        data = self.recommendation.recommendation_data
        self.assertEqual(data['estimated_cost'], 50000)
        self.assertIn('Python', data['skill_requirements'])


class AISearchQueryModelTest(TestCase):
    """Test cases for AISearchQuery model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.search_query = AISearchQuery.objects.create(
            user=self.user,
            query_text="Who is available for Python development?",
            query_type="resource_availability",
            processed_query="resource search: skill=Python, availability=true",
            response_time=0.25,
            session_id="session_123"
        )
    
    def test_search_query_creation(self):
        """Test search query creation"""
        expected_str = f"testuser - Who is available for Python development? ({self.search_query.created_at.strftime('%Y-%m-%d')})"
        self.assertEqual(str(self.search_query), expected_str)
        self.assertEqual(self.search_query.query_type, "resource_availability")
        self.assertEqual(self.search_query.response_time, 0.25)
    
    def test_query_types(self):
        """Test different query types"""
        query_types = [
            'resource_search', 'project_status', 'allocation_analysis',
            'skill_analysis', 'general_question', 'resource_availability'
        ]
        
        for query_type in query_types:
            query = AISearchQuery.objects.create(
                user=self.user,
                query_text=f"Test {query_type} query",
                query_type=query_type
            )
            self.assertEqual(query.query_type, query_type)


class AISearchResultModelTest(TestCase):
    """Test cases for AISearchResult model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.search_query = AISearchQuery.objects.create(
            user=self.user,
            query_text="Test query",
            query_type="resource_search"
        )
        
        self.search_result = AISearchResult.objects.create(
            query=self.search_query,
            result_text="Found 3 Python developers available",
            result_data={
                'developers': [
                    {'name': 'John Doe', 'availability': 40},
                    {'name': 'Jane Smith', 'availability': 20}
                ],
                'total_found': 2
            },
            confidence_score=0.9,
            result_type="structured_data"
        )
    
    def test_search_result_creation(self):
        """Test search result creation"""
        expected_str = f"Result for 'Test query' - structured_data (90.0% confidence)"
        self.assertEqual(str(self.search_result), expected_str)
        self.assertEqual(self.search_result.confidence_score, 0.9)
        self.assertEqual(self.search_result.result_type, "structured_data")
    
    def test_result_data_field(self):
        """Test result data JSON field"""
        data = self.search_result.result_data
        self.assertEqual(data['total_found'], 2)
        self.assertEqual(len(data['developers']), 2)
        self.assertEqual(data['developers'][0]['name'], 'John Doe')


class DashboardViewsTest(TestCase):
    """Test cases for Dashboard views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create some test data
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            manager=self.user
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="Test Resource",
            role="Developer"
        )
        
        self.client.force_login(self.user)
    
    def test_dashboard_home_view(self):
        """Test dashboard home view"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
    
    def test_ai_analysis_api_view(self):
        """Test AI analysis API endpoint"""
        response = self.client.get('/dashboard/api/ai-analysis/')
        self.assertEqual(response.status_code, 200)
        
        # Should return JSON
        data = response.json()
        self.assertIn('status', data)
    
    def test_risk_assessment_view(self):
        """Test risk assessment view"""
        response = self.client.get('/dashboard/risks/')
        self.assertEqual(response.status_code, 200)
    
    def test_ai_search_api(self):
        """Test AI search API endpoint"""
        search_data = {
            'query': 'Who is available for development?',
            'query_type': 'resource_availability'
        }
        
        response = self.client.post(
            '/dashboard/api/ai-search/',
            data=json.dumps(search_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)


class DashboardIntegrationTest(TestCase):
    """Integration tests for Dashboard functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            password='testpass123'
        )
        
        # Create comprehensive test data
        self.skill_python = Skill.objects.create(name="Python")
        self.skill_react = Skill.objects.create(name="React")
        
        self.developer = Resource.objects.create(
            user=self.user,
            name="Senior Developer",
            role="Software Developer",
            capacity=40,
            cost_per_hour=Decimal('85.00')
        )
        
        self.project = Project.objects.create(
            name="E-commerce Platform",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            manager=self.user,
            budget=Decimal('50000.00'),
            status='active'
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Backend Development",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            estimated_hours=120,
            status='in_progress'
        )
        
        self.assignment = Assignment.objects.create(
            resource=self.developer,
            task=self.task,
            allocated_hours=120
        )
    
    def test_complete_ai_analysis_workflow(self):
        """Test complete AI analysis workflow"""
        # Create AI analysis
        analysis = DashboardAIAnalysis.objects.create(
            analysis_type='daily_briefing',
            analysis_data={
                'total_projects': 1,
                'active_tasks': 1,
                'resource_utilization': 100.0
            },
            summary="High resource utilization detected",
            risks=[
                {
                    'id': 'overallocation_001',
                    'type': 'resource',
                    'severity': 'high',
                    'description': 'Developer at 100% capacity'
                }
            ],
            recommendations=[
                {
                    'id': 'hire_contractor',
                    'action': 'Consider hiring contractor',
                    'priority': 'high'
                }
            ],
            confidence_score=0.85
        )
        
        # Create related risk
        risk_category = RiskCategory.objects.create(
            name="Resource Overallocation",
            risk_type="resource"
        )
        
        dynamic_risk = DynamicRisk.objects.create(
            risk_id="overallocation_001",
            category=risk_category,
            title="Developer Overallocation",
            description="Senior Developer allocated at 100% capacity",
            severity_score=0.9,
            project=self.project,
            resource=self.developer,
            risk_data={'allocation_percentage': 100}
        )
        
        # Create recommendation
        recommendation = AIRecommendation.objects.create(
            recommendation_id="hire_contractor",
            title="Hire Additional Contractor",
            description="Consider hiring a contractor to reduce workload",
            recommendation_type="resource_planning",
            priority="high",
            confidence_score=0.8,
            status="pending"
        )
        
        # Test relationships and data integrity
        self.assertEqual(analysis.risks[0]['id'], dynamic_risk.risk_id)
        self.assertEqual(analysis.recommendations[0]['id'], recommendation.recommendation_id)
        self.assertEqual(dynamic_risk.project, self.project)
        self.assertEqual(dynamic_risk.resource, self.developer)
    
    def test_ai_search_workflow(self):
        """Test AI search functionality workflow"""
        # Create search query
        search_query = AISearchQuery.objects.create(
            user=self.user,
            query_text="Show me overallocated resources",
            query_type="resource_analysis",
            processed_query="resource analysis: allocation > capacity",
            response_time=0.15
        )
        
        # Create search result
        search_result = AISearchResult.objects.create(
            query=search_query,
            result_text="Found 1 overallocated resource: Senior Developer (100% capacity)",
            result_data={
                'overallocated_resources': [
                    {
                        'name': 'Senior Developer',
                        'allocation_percentage': 100,
                        'capacity': 40,
                        'allocated_hours': 40
                    }
                ],
                'total_count': 1
            },
            confidence_score=0.95,
            result_type="resource_analysis"
        )
        
        # Test search functionality
        self.assertEqual(search_query.user, self.user)
        self.assertEqual(search_result.query, search_query)
        self.assertEqual(search_result.result_data['total_count'], 1)
        self.assertEqual(
            search_result.result_data['overallocated_resources'][0]['name'],
            'Senior Developer'
        )
    
    def test_dashboard_metrics_calculation(self):
        """Test dashboard metrics calculation"""
        # Test project metrics
        self.assertEqual(Project.objects.filter(status='active').count(), 1)
        self.assertEqual(Task.objects.filter(status='in_progress').count(), 1)
        
        # Test resource metrics
        total_allocated_hours = sum(
            assignment.allocated_hours 
            for assignment in Assignment.objects.all()
        )
        self.assertEqual(total_allocated_hours, 120)
        
        # Test utilization calculation
        resource_capacity = self.developer.capacity  # 40 hours per week
        # For 30-day task, approximately 4.3 weeks
        estimated_capacity = resource_capacity * 4.3  # ~172 hours
        utilization_percentage = (120 / estimated_capacity) * 100
        self.assertLess(utilization_percentage, 100)  # Should be under 100%
