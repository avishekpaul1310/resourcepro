from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    ResourceDemandForecast, HistoricalUtilization, 
    ProjectCostTracking, SkillDemandAnalysis, 
    ResourcePerformanceMetrics, UtilizationTrend
)
from resources.models import Resource, Skill, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment


class ResourceDemandForecastModelTest(TestCase):
    """Test cases for ResourceDemandForecast model"""
    
    def setUp(self):
        self.forecast = ResourceDemandForecast.objects.create(
            forecast_date=date.today(),
            resource_role="Software Developer",
            predicted_demand_hours=Decimal('240.50'),
            confidence_score=Decimal('0.85'),
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30)
        )
    
    def test_forecast_creation(self):
        """Test forecast creation and basic properties"""
        expected_str = f"Forecast for Software Developer - {date.today()}"
        self.assertEqual(str(self.forecast), expected_str)
        self.assertEqual(self.forecast.resource_role, "Software Developer")
        self.assertEqual(self.forecast.predicted_demand_hours, Decimal('240.50'))
        self.assertEqual(self.forecast.confidence_score, Decimal('0.85'))
    
    def test_forecast_ordering(self):
        """Test forecast ordering by forecast_date desc"""
        forecast2 = ResourceDemandForecast.objects.create(
            forecast_date=date.today() + timedelta(days=1),
            resource_role="Designer",
            predicted_demand_hours=Decimal('160.00'),
            confidence_score=Decimal('0.75'),
            period_start=date.today() + timedelta(days=1),
            period_end=date.today() + timedelta(days=31)
        )
        
        forecasts = list(ResourceDemandForecast.objects.all())
        self.assertEqual(forecasts[0], forecast2)  # Most recent first
        self.assertEqual(forecasts[1], self.forecast)
    
    def test_forecast_period_validation(self):
        """Test forecast period start/end dates"""
        self.assertLessEqual(self.forecast.period_start, self.forecast.period_end)
    
    def test_confidence_score_range(self):
        """Test confidence score is within valid range"""
        self.assertGreaterEqual(self.forecast.confidence_score, Decimal('0.00'))
        self.assertLessEqual(self.forecast.confidence_score, Decimal('1.00'))


class HistoricalUtilizationModelTest(TestCase):
    """Test cases for HistoricalUtilization model"""
    
    def setUp(self):
        self.resource = Resource.objects.create(
            name="John Developer",
            role="Software Developer",
            capacity=40  # 40 hours per week
        )
        
        self.utilization = HistoricalUtilization.objects.create(
            resource=self.resource,
            date=date.today(),
            utilization_percentage=Decimal('87.50'),
            allocated_hours=Decimal('35.00'),
            available_hours=Decimal('40.00')
        )
    
    def test_utilization_creation(self):
        """Test utilization creation and basic properties"""
        expected_str = f"{self.resource.name} - {date.today()} (87.50%)"
        self.assertEqual(str(self.utilization), expected_str)
        self.assertEqual(self.utilization.utilization_percentage, Decimal('87.50'))
        self.assertEqual(self.utilization.allocated_hours, Decimal('35.00'))
        self.assertEqual(self.utilization.available_hours, Decimal('40.00'))
    
    def test_utilization_calculation_consistency(self):
        """Test utilization percentage calculation consistency"""
        # Calculate expected utilization: (35/40) * 100 = 87.5%
        expected_utilization = (self.utilization.allocated_hours / 
                              self.utilization.available_hours) * 100
        self.assertEqual(self.utilization.utilization_percentage, expected_utilization)
    
    def test_unique_constraint(self):
        """Test unique constraint on resource-date combination"""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            HistoricalUtilization.objects.create(
                resource=self.resource,
                date=date.today(),
                utilization_percentage=Decimal('50.00'),
                allocated_hours=Decimal('20.00'),
                available_hours=Decimal('40.00')
            )
    
    def test_utilization_ordering(self):
        """Test utilization ordering by date desc"""
        utilization2 = HistoricalUtilization.objects.create(
            resource=self.resource,
            date=date.today() + timedelta(days=1),
            utilization_percentage=Decimal('92.50'),
            allocated_hours=Decimal('37.00'),
            available_hours=Decimal('40.00')
        )
        
        utilizations = list(HistoricalUtilization.objects.all())
        self.assertEqual(utilizations[0], utilization2)  # Most recent first
        self.assertEqual(utilizations[1], self.utilization)


class ProjectCostTrackingModelTest(TestCase):
    """Test cases for ProjectCostTracking model"""
    
    def setUp(self):
        self.project = Project.objects.create(
            name="E-commerce Platform",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            budget=Decimal('50000.00')
        )
        
        self.cost_tracking = ProjectCostTracking.objects.create(
            project=self.project,
            date=date.today(),
            estimated_cost=Decimal('45000.00'),
            actual_cost=Decimal('42000.00'),
            budget_variance=Decimal('8000.00')  # budget - actual = 50000 - 42000
        )
    
    def test_cost_tracking_creation(self):
        """Test cost tracking creation and basic properties"""
        expected_str = f"{self.project.name} - Cost Tracking {date.today()}"
        self.assertEqual(str(self.cost_tracking), expected_str)
        self.assertEqual(self.cost_tracking.estimated_cost, Decimal('45000.00'))
        self.assertEqual(self.cost_tracking.actual_cost, Decimal('42000.00'))
        self.assertEqual(self.cost_tracking.budget_variance, Decimal('8000.00'))
    
    def test_budget_variance_calculation(self):
        """Test budget variance calculation"""
        # Positive variance means under budget
        self.assertGreater(self.cost_tracking.budget_variance, 0)
        
        # Calculate expected variance
        expected_variance = self.project.budget - self.cost_tracking.actual_cost
        self.assertEqual(self.cost_tracking.budget_variance, expected_variance)
    
    def test_cost_tracking_relationship(self):
        """Test relationship with project"""
        self.assertEqual(self.cost_tracking.project, self.project)
        
        # Test reverse relationship
        project_tracking = self.project.cost_tracking.all()
        self.assertIn(self.cost_tracking, project_tracking)


class SkillDemandAnalysisModelTest(TestCase):
    """Test cases for SkillDemandAnalysis model"""
    
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")
        
        self.skill_analysis = SkillDemandAnalysis.objects.create(
            skill=self.skill,
            analysis_date=date.today(),
            current_demand=Decimal('120.00'),
            future_demand=Decimal('180.00'),
            supply_available=Decimal('100.00'),
            gap_analysis=Decimal('-20.00'),  # demand - supply = 120 - 100
            growth_rate=Decimal('0.25'),  # 25% growth
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30)
        )
    
    def test_skill_analysis_creation(self):
        """Test skill analysis creation"""
        expected_str = f"Python demand analysis - {date.today()}"
        self.assertEqual(str(self.skill_analysis), expected_str)
        self.assertEqual(self.skill_analysis.current_demand, Decimal('120.00'))
        self.assertEqual(self.skill_analysis.future_demand, Decimal('180.00'))
        self.assertEqual(self.skill_analysis.gap_analysis, Decimal('-20.00'))
    
    def test_gap_analysis_calculation(self):
        """Test gap analysis calculation"""
        # Negative gap means demand exceeds supply
        self.assertLess(self.skill_analysis.gap_analysis, 0)
        
        expected_gap = self.skill_analysis.current_demand - self.skill_analysis.supply_available
        self.assertEqual(self.skill_analysis.gap_analysis, expected_gap)
    
    def test_growth_rate_validation(self):
        """Test growth rate is reasonable"""
        self.assertEqual(self.skill_analysis.growth_rate, Decimal('0.25'))
        # Growth rate of 25% means future demand should be higher
        expected_future = self.skill_analysis.current_demand * (1 + self.skill_analysis.growth_rate)
        self.assertEqual(self.skill_analysis.future_demand, expected_future)


class ResourcePerformanceMetricsModelTest(TestCase):
    """Test cases for ResourcePerformanceMetrics model"""
    
    def setUp(self):
        self.resource = Resource.objects.create(
            name="Senior Developer",
            role="Software Developer",
            cost_per_hour=Decimal('85.00')
        )
        
        self.performance = ResourcePerformanceMetrics.objects.create(
            resource=self.resource,
            measurement_date=date.today(),
            productivity_score=Decimal('8.5'),
            quality_score=Decimal('9.0'),
            efficiency_score=Decimal('7.8'),
            overall_rating=Decimal('8.4'),
            tasks_completed=15,
            average_task_completion_time=Decimal('2.3'),  # days
            defect_rate=Decimal('0.05'),  # 5%
            client_satisfaction=Decimal('4.7'),  # out of 5
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today()
        )
    
    def test_performance_creation(self):
        """Test performance metrics creation"""
        expected_str = f"Senior Developer performance - {date.today()}"
        self.assertEqual(str(self.performance), expected_str)
        self.assertEqual(self.performance.productivity_score, Decimal('8.5'))
        self.assertEqual(self.performance.quality_score, Decimal('9.0'))
        self.assertEqual(self.performance.overall_rating, Decimal('8.4'))
    
    def test_performance_scores_range(self):
        """Test performance scores are within valid range"""
        scores = [
            self.performance.productivity_score,
            self.performance.quality_score,
            self.performance.efficiency_score,
            self.performance.overall_rating
        ]
        
        for score in scores:
            self.assertGreaterEqual(score, Decimal('0.0'))
            self.assertLessEqual(score, Decimal('10.0'))
    
    def test_defect_rate_validation(self):
        """Test defect rate is percentage"""
        self.assertGreaterEqual(self.performance.defect_rate, Decimal('0.0'))
        self.assertLessEqual(self.performance.defect_rate, Decimal('1.0'))
    
    def test_client_satisfaction_range(self):
        """Test client satisfaction is within 1-5 range"""
        self.assertGreaterEqual(self.performance.client_satisfaction, Decimal('1.0'))
        self.assertLessEqual(self.performance.client_satisfaction, Decimal('5.0'))


class UtilizationTrendModelTest(TestCase):
    """Test cases for UtilizationTrend model"""
    
    def setUp(self):
        self.trend = UtilizationTrend.objects.create(
            trend_date=date.today(),
            period_type='weekly',
            average_utilization=Decimal('82.5'),
            peak_utilization=Decimal('95.0'),
            low_utilization=Decimal('65.0'),
            trend_direction='increasing',
            change_percentage=Decimal('0.08'),  # 8% increase
            total_resources_analyzed=25,
            overutilized_resources=3,
            underutilized_resources=5
        )
    
    def test_trend_creation(self):
        """Test utilization trend creation"""
        expected_str = f"Utilization trend - {date.today()} (weekly)"
        self.assertEqual(str(self.trend), expected_str)
        self.assertEqual(self.trend.period_type, 'weekly')
        self.assertEqual(self.trend.average_utilization, Decimal('82.5'))
        self.assertEqual(self.trend.trend_direction, 'increasing')
    
    def test_period_type_choices(self):
        """Test period type choices"""
        period_types = ['daily', 'weekly', 'monthly', 'quarterly']
        
        for period_type in period_types:
            trend = UtilizationTrend.objects.create(
                trend_date=date.today() + timedelta(days=1),
                period_type=period_type,
                average_utilization=Decimal('80.0')
            )
            self.assertEqual(trend.period_type, period_type)
    
    def test_trend_direction_choices(self):
        """Test trend direction choices"""
        directions = ['increasing', 'decreasing', 'stable']
        
        for direction in directions:
            trend = UtilizationTrend.objects.create(
                trend_date=date.today() + timedelta(days=2),
                period_type='weekly',
                average_utilization=Decimal('75.0'),
                trend_direction=direction
            )
            self.assertEqual(trend.trend_direction, direction)
    
    def test_utilization_consistency(self):
        """Test utilization values consistency"""
        # Peak should be >= average >= low
        self.assertGreaterEqual(self.trend.peak_utilization, self.trend.average_utilization)
        self.assertGreaterEqual(self.trend.average_utilization, self.trend.low_utilization)


class AnalyticsViewsTest(TestCase):
    """Test cases for Analytics views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="Test Resource",
            role="Developer"
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.client.force_login(self.user)
    
    def test_analytics_dashboard_view(self):
        """Test analytics dashboard view"""
        response = self.client.get('/analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analytics")
    
    def test_utilization_report_view(self):
        """Test utilization report view"""
        response = self.client.get('/analytics/utilization/')
        self.assertEqual(response.status_code, 200)
    
    def test_cost_analysis_view(self):
        """Test cost analysis view"""
        response = self.client.get('/analytics/costs/')
        self.assertEqual(response.status_code, 200)
    
    def test_skill_analysis_view(self):
        """Test skill analysis view"""
        response = self.client.get('/analytics/skills/')
        self.assertEqual(response.status_code, 200)
    
    def test_performance_metrics_view(self):
        """Test performance metrics view"""
        response = self.client.get('/analytics/performance/')
        self.assertEqual(response.status_code, 200)


class AnalyticsAPITest(TestCase):
    """Test cases for Analytics API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.skill = Skill.objects.create(name="Python")
        self.resource = Resource.objects.create(
            name="Developer",
            role="Software Developer",
            cost_per_hour=Decimal('75.00')
        )
        
        # Create test data
        HistoricalUtilization.objects.create(
            resource=self.resource,
            date=date.today(),
            utilization_percentage=Decimal('85.0'),
            allocated_hours=Decimal('34.0'),
            available_hours=Decimal('40.0')
        )
        
        self.client.force_login(self.user)
    
    def test_utilization_api_endpoint(self):
        """Test utilization data API endpoint"""
        response = self.client.get('/analytics/api/utilization/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('utilization_data', data)
    
    def test_forecast_api_endpoint(self):
        """Test demand forecast API endpoint"""
        ResourceDemandForecast.objects.create(
            forecast_date=date.today(),
            resource_role="Software Developer",
            predicted_demand_hours=Decimal('200.0'),
            confidence_score=Decimal('0.8'),
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30)
        )
        
        response = self.client.get('/analytics/api/forecasts/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('forecasts', data)
    
    def test_skill_demand_api_endpoint(self):
        """Test skill demand API endpoint"""
        SkillDemandAnalysis.objects.create(
            skill=self.skill,
            analysis_date=date.today(),
            current_demand=Decimal('100.0'),
            future_demand=Decimal('150.0'),
            supply_available=Decimal('80.0'),
            gap_analysis=Decimal('-20.0'),
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30)
        )
        
        response = self.client.get('/analytics/api/skill-demand/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('skill_analysis', data)


class AnalyticsIntegrationTest(TestCase):
    """Integration tests for Analytics functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            password='testpass123'
        )
        
        # Create comprehensive test data
        self.skill_python = Skill.objects.create(name="Python")
        self.skill_react = Skill.objects.create(name="React")
        
        self.developer = Resource.objects.create(
            name="Senior Developer",
            role="Software Developer",
            capacity=40,
            cost_per_hour=Decimal('85.00')
        )
        
        self.project = Project.objects.create(
            name="Analytics Test Project",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            manager=self.user,
            budget=Decimal('30000.00')
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Development Task",
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() + timedelta(days=10),
            estimated_hours=80
        )
        
        self.assignment = Assignment.objects.create(
            resource=self.developer,
            task=self.task,
            allocated_hours=80
        )
    
    def test_utilization_tracking_workflow(self):
        """Test complete utilization tracking workflow"""
        # Create historical utilization data
        for i in range(7):  # Last 7 days
            utilization_date = date.today() - timedelta(days=i)
            utilization_pct = Decimal('80.0') + (i * Decimal('2.0'))  # Varying utilization
            
            HistoricalUtilization.objects.create(
                resource=self.developer,
                date=utilization_date,
                utilization_percentage=utilization_pct,
                allocated_hours=utilization_pct * Decimal('0.4'),  # 40 hours capacity
                available_hours=Decimal('40.0')
            )
        
        # Test data retrieval
        utilizations = HistoricalUtilization.objects.filter(resource=self.developer)
        self.assertEqual(utilizations.count(), 7)
        
        # Test average utilization calculation
        avg_utilization = sum(u.utilization_percentage for u in utilizations) / len(utilizations)
        self.assertGreater(avg_utilization, Decimal('80.0'))
    
    def test_cost_tracking_workflow(self):
        """Test project cost tracking workflow"""
        # Create time entries to generate actual costs
        TimeEntry.objects.create(
            resource=self.developer,
            task=self.task,
            date=date.today() - timedelta(days=5),
            hours=8
        )
        
        TimeEntry.objects.create(
            resource=self.developer,
            task=self.task,
            date=date.today() - timedelta(days=4),
            hours=7.5
        )
        
        # Calculate actual cost
        total_hours = sum(entry.hours for entry in self.task.time_entries.all())
        actual_cost = total_hours * self.developer.cost_per_hour
        
        # Create cost tracking entry
        cost_tracking = ProjectCostTracking.objects.create(
            project=self.project,
            date=date.today(),
            estimated_cost=Decimal('6800.00'),  # 80 hours * $85
            actual_cost=actual_cost,
            budget_variance=self.project.budget - actual_cost
        )
        
        # Test cost tracking
        self.assertEqual(cost_tracking.actual_cost, Decimal('1317.50'))  # 15.5 * 85
        self.assertGreater(cost_tracking.budget_variance, Decimal('28000.00'))
    
    def test_demand_forecasting_workflow(self):
        """Test demand forecasting workflow"""
        # Create historical demand data
        ResourceDemandForecast.objects.create(
            forecast_date=date.today(),
            resource_role="Software Developer",
            predicted_demand_hours=Decimal('200.00'),
            confidence_score=Decimal('0.85'),
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30)
        )
        
        # Create skill demand analysis
        SkillDemandAnalysis.objects.create(
            skill=self.skill_python,
            analysis_date=date.today(),
            current_demand=Decimal('120.00'),
            future_demand=Decimal('180.00'),
            supply_available=Decimal('100.00'),
            gap_analysis=Decimal('-20.00'),
            growth_rate=Decimal('0.25'),
            period_start=date.today(),
            period_end=date.today() + timedelta(days=30)
        )
        
        # Test forecasting data
        forecasts = ResourceDemandForecast.objects.filter(resource_role="Software Developer")
        self.assertEqual(forecasts.count(), 1)
        
        skill_analysis = SkillDemandAnalysis.objects.filter(skill=self.skill_python)
        self.assertEqual(skill_analysis.count(), 1)
        self.assertLess(skill_analysis.first().gap_analysis, 0)  # Demand exceeds supply
    
    def test_performance_metrics_workflow(self):
        """Test performance metrics tracking workflow"""
        # Create performance metrics
        performance = ResourcePerformanceMetrics.objects.create(
            resource=self.developer,
            measurement_date=date.today(),
            productivity_score=Decimal('8.5'),
            quality_score=Decimal('9.0'),
            efficiency_score=Decimal('7.8'),
            overall_rating=Decimal('8.4'),
            tasks_completed=12,
            average_task_completion_time=Decimal('2.5'),
            defect_rate=Decimal('0.03'),
            client_satisfaction=Decimal('4.5'),
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today()
        )
        
        # Create utilization trend
        trend = UtilizationTrend.objects.create(
            trend_date=date.today(),
            period_type='weekly',
            average_utilization=Decimal('82.5'),
            peak_utilization=Decimal('95.0'),
            low_utilization=Decimal('65.0'),
            trend_direction='increasing',
            change_percentage=Decimal('0.08'),
            total_resources_analyzed=15,
            overutilized_resources=2,
            underutilized_resources=3
        )
        
        # Test performance tracking
        self.assertEqual(performance.resource, self.developer)
        self.assertEqual(performance.overall_rating, Decimal('8.4'))
        
        # Test trend analysis
        self.assertEqual(trend.trend_direction, 'increasing')
        self.assertGreater(trend.peak_utilization, trend.average_utilization)
