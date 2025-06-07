import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from resources.models import Resource, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment
from .models import ResourceDemandForecast, HistoricalUtilization, SkillDemandAnalysis

class PredictiveAnalyticsService:
    """Service for predictive analytics and forecasting"""
    
    def generate_resource_demand_forecast(self, days_ahead=30):
        """Generate resource demand forecast using historical data"""
        # Get historical assignment data
        historical_data = self._get_historical_assignment_data()
        
        if len(historical_data) < 10:  # Need minimum data points
            return None
          # Prepare data for ML model
        df = pd.DataFrame(historical_data)
        
        # Convert date column to datetime if it's not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Create features
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        # Group by role and time period
        role_forecasts = []
        
        for role in df['role'].unique():
            role_data = df[df['role'] == role].copy()
            role_data = role_data.groupby('date').agg({
                'allocated_hours': 'sum',
                'week_of_year': 'first',
                'month': 'first',
                'quarter': 'first'
            }).reset_index()
            
            if len(role_data) < 5:
                continue
            
            # Prepare features for prediction
            X = role_data[['week_of_year', 'month', 'quarter']].values
            y = role_data['allocated_hours'].values
            
            # Train model
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            # Generate forecast
            future_date = timezone.now().date() + timedelta(days=days_ahead)
            future_features = [[
                future_date.isocalendar()[1],  # week
                future_date.month,
                (future_date.month - 1) // 3 + 1  # quarter
            ]]
            
            future_scaled = scaler.transform(future_features)
            predicted_demand = model.predict(future_scaled)[0]
            
            # Calculate confidence score based on R²
            r2_score = model.score(X_scaled, y)
            confidence = max(0.1, min(1.0, r2_score))
            
            # Create forecast record
            forecast = ResourceDemandForecast.objects.create(
                forecast_date=timezone.now().date(),
                resource_role=role,
                predicted_demand_hours=max(0, predicted_demand),
                confidence_score=confidence,
                period_start=future_date,
                period_end=future_date + timedelta(days=7)
            )
            
            role_forecasts.append(forecast)
        
        return role_forecasts
    
    def analyze_skill_demand(self):
        """Analyze current and predicted skill demand"""
        from resources.models import Skill
        
        skills = Skill.objects.all()
        analyses = []
        
        for skill in skills:
            # Current demand (active tasks requiring this skill)
            current_demand = Task.objects.filter(
                skills_required=skill,
                status__in=['not_started', 'in_progress']
            ).count()
            
            # Available resources with this skill
            available_resources = Resource.objects.filter(
                skills=skill
            ).count()
            
            # Calculate demand score
            if available_resources > 0:
                demand_score = current_demand / available_resources
            else:
                demand_score = float('inf')
            
            # Predict future demand (simplified - based on historical trends)
            historical_tasks = Task.objects.filter(
                skills_required=skill,
                created_at__gte=timezone.now() - timedelta(days=90)
            ).count()
            
            predicted_future_demand = int(historical_tasks * 0.3)  # 30% growth assumption
            
            analysis = SkillDemandAnalysis.objects.create(
                skill_name=skill.name,
                analysis_date=timezone.now().date(),
                current_demand=current_demand,
                available_resources=available_resources,
                demand_score=min(99.99, demand_score),  # Cap at 99.99 for database
                predicted_future_demand=predicted_future_demand
            )
            
            analyses.append(analysis)
        
        return analyses
    
    def _get_historical_assignment_data(self):
        """Get historical assignment data for analysis"""
        assignments = Assignment.objects.select_related('resource', 'task').filter(
            created_at__gte=timezone.now() - timedelta(days=180)
        )
        
        data = []
        for assignment in assignments:
            data.append({
                'date': assignment.created_at.date(),
                'role': assignment.resource.role,
                'allocated_hours': float(assignment.allocated_hours),
                'resource_id': assignment.resource.id,
                'task_id': assignment.task.id
            })
        
        return data

class UtilizationTrackingService:
    """Service for tracking and storing utilization metrics"""
    
    def record_daily_utilization(self, date=None):
        """Record utilization data for all resources for a given date"""
        if date is None:
            date = timezone.now().date()
        
        resources = Resource.objects.all()
        
        for resource in resources:
            utilization = resource.current_utilization(date, date)
            
            # Calculate allocated and available hours for the day
            assignments = Assignment.objects.filter(
                resource=resource,
                task__start_date__lte=date,
                task__end_date__gte=date
            )
            
            allocated_hours = sum(
                assignment.allocated_hours / 
                max(1, (assignment.task.end_date - assignment.task.start_date).days + 1)
                for assignment in assignments
            )
            
            # Assuming 8 hours per day capacity
            available_hours = resource.capacity / 5  # Weekly capacity / 5 days
            
            HistoricalUtilization.objects.update_or_create(
                resource=resource,
                date=date,
                defaults={
                    'utilization_percentage': utilization,
                    'allocated_hours': allocated_hours,
                    'available_hours': available_hours
                }
            )
    
    def get_utilization_trends(self, resource=None, days=30):
        """Get utilization trends for analysis"""
        queryset = HistoricalUtilization.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=days)
        ).order_by('date')
        
        if resource:
            queryset = queryset.filter(resource=resource)
        
        return queryset

class CostTrackingService:
    """Service for cost analysis and budget tracking"""
    
    def update_project_costs(self, project_id=None):
        """Update cost tracking for projects"""
        from .models import ProjectCostTracking
        
        projects = Project.objects.all()
        if project_id:
            projects = projects.filter(id=project_id)
        
        for project in projects:
            estimated_cost = project.get_estimated_cost()
            actual_cost = project.get_actual_cost()
            budget_variance = project.get_budget_variance() or 0
            
            ProjectCostTracking.objects.update_or_create(
                project=project,
                date=timezone.now().date(),
                defaults={
                    'estimated_cost': estimated_cost,
                    'actual_cost': actual_cost,
                    'budget_variance': budget_variance
                }
            )
    
    def get_cost_variance_report(self):
        """Generate cost variance report"""
        projects = Project.objects.filter(status__in=['active', 'planning'])
        
        report_data = []
        for project in projects:
            estimated = project.get_estimated_cost()
            actual = project.get_actual_cost()
            variance = estimated - actual if estimated and actual else 0
            variance_percentage = (variance / estimated * 100) if estimated > 0 else 0
            
            report_data.append({
                'project': project,
                'estimated_cost': estimated,
                'actual_cost': actual,
                'variance': variance,
                'variance_percentage': variance_percentage,
                'budget': project.budget,
                'budget_utilization': (actual / project.budget * 100) if project.budget else 0
            })
        
        return report_data
