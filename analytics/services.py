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
from .ai_services import AIForecastEnhancementService

class PredictiveAnalyticsService:
    """Service for predictive analytics and forecasting"""
    
    def __init__(self):
        self.ai_forecast_service = AIForecastEnhancementService()
    
    def generate_resource_demand_forecast(self, days_ahead=30, include_ai_enhancement=True):
        """Generate resource demand forecast using adaptive methods based on available data"""
        # Get historical assignment data with flexible timeframe
        historical_data = self._get_historical_assignment_data()
        
        # Determine the best forecasting method based on available data
        method, confidence_level = self._determine_forecast_method(historical_data)
        
        if method == "insufficient":
            return None
        elif method == "bootstrap":
            forecasts = self._generate_bootstrap_forecast(historical_data, days_ahead)
        elif method == "trend":
            forecasts = self._generate_trend_forecast(historical_data, days_ahead)
        else:
            # Use the existing statistical method for sufficient data
            forecasts = self._generate_statistical_forecast(historical_data, days_ahead)
        
        if not forecasts:
            return None
        
        # Apply AI enhancement if requested and we have enough confidence
        if include_ai_enhancement and confidence_level >= 2:
            try:
                enhanced_result = self.ai_forecast_service.enhance_resource_demand_forecast(
                    forecasts
                )
                
                return {
                    "statistical_forecasts": forecasts,
                    "ai_enhanced": enhanced_result,
                    "generation_method": f"{method}_with_ai_enhancement",
                    "confidence_level": confidence_level,
                    "data_quality": method
                }
            except Exception as e:
                print(f"AI enhancement failed: {e}")
                return {
                    "statistical_forecasts": forecasts,
                    "generation_method": f"{method}_only",
                    "confidence_level": confidence_level,
                    "data_quality": method
                }
        
        return forecasts
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
        
        # Apply AI enhancement if requested
        if include_ai_enhancement and role_forecasts:
            try:
                enhanced_result = self.ai_forecast_service.enhance_resource_demand_forecast(
                    role_forecasts
                )
                
                # Return both statistical and AI-enhanced forecasts
                return {
                    "statistical_forecasts": role_forecasts,
                    "ai_enhanced": enhanced_result,
                    "generation_method": "statistical_with_ai_enhancement"
                }
            except Exception as e:
                # Fall back to statistical forecasts if AI enhancement fails
                print(f"AI enhancement failed: {e}")
                return {
                    "statistical_forecasts": role_forecasts,
                    "generation_method": "statistical_only"
                }
        
        return role_forecasts
    
    def generate_skill_specific_forecast(self, skill_id, days_ahead=30):
        """Generate forecasts specifically for a skill, not just role-based"""
        from resources.models import Skill
        
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return None
        
        # Get resources that have this skill
        resources_with_skill = Resource.objects.filter(skills=skill)
        
        if not resources_with_skill:
            return None
        
        # Get historical data for these specific resources
        historical_data = self._get_skill_specific_historical_data(skill, resources_with_skill)
        
        if len(historical_data) < 5:  # Need minimum data points
            return None
        
        # Prepare data for ML model
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        # Group by date and aggregate
        skill_data = df.groupby('date').agg({
            'allocated_hours': 'sum',
            'week_of_year': 'first',
            'month': 'first',
            'quarter': 'first'
        }).reset_index()
        
        if len(skill_data) < 3:
            return None
        
        # Prepare features for prediction
        X = skill_data[['week_of_year', 'month', 'quarter']].values
        y = skill_data['allocated_hours'].values
        
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
        
        # Create forecasts for each role that has this skill
        forecasts = []
        roles_with_skill = list(set([r.role for r in resources_with_skill]))
        
        for role in roles_with_skill:
            # Distribute the predicted demand across roles based on resource count
            role_resources = [r for r in resources_with_skill if r.role == role]
            role_weight = len(role_resources) / len(resources_with_skill)
            role_demand = predicted_demand * role_weight
            
            # Create a unique forecast for this skill-role combination
            forecast = ResourceDemandForecast.objects.create(
                forecast_date=timezone.now().date(),
                resource_role=f"{role} ({skill.name})",  # Make it skill-specific
                predicted_demand_hours=max(0, role_demand),
                confidence_score=confidence,
                period_start=future_date,
                period_end=future_date + timedelta(days=7)
            )
            
            forecasts.append(forecast)
        
        return forecasts
    
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
            
            # Store analysis result
            analysis, created = SkillDemandAnalysis.objects.get_or_create(
                skill_name=skill.name,
                analysis_date=timezone.now().date(),
                defaults={
                    'current_demand': current_demand,
                    'available_resources': available_resources,
                    'demand_score': min(99.99, demand_score),  # Cap at 99.99 for database
                    'predicted_future_demand': predicted_future_demand
                }            )
            
            analyses.append(analysis)
        
        return analyses

    def _get_historical_assignment_data(self, max_days=180):
        """Get historical assignment data with flexible timeframe"""
        # Try different timeframes, starting with the requested max_days
        timeframes = [max_days, 90, 60, 30, 14, 7]
        
        for days in timeframes:
            assignments = Assignment.objects.select_related('resource', 'task').filter(
                created_at__gte=timezone.now() - timedelta(days=days)
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
            
            # If we have enough data points, use this timeframe
            unique_dates = len(set(d['date'] for d in data))
            if len(data) >= 10 and unique_dates >= 3:
                return data
        
        # Return whatever we have, even if minimal
        assignments = Assignment.objects.select_related('resource', 'task').all()[:50]  # At least try recent assignments
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
    
    def _get_skill_specific_historical_data(self, skill, resources_with_skill):
        """Get historical assignment data for resources with a specific skill"""
        assignments = Assignment.objects.select_related('resource', 'task').filter(
            resource__in=resources_with_skill,
            task__skills_required=skill,  # Only tasks that require this skill
            created_at__gte=timezone.now() - timedelta(days=180)
        )
        
        data = []
        for assignment in assignments:
            data.append({
                'date': assignment.created_at.date(),
                'role': assignment.resource.role,
                'allocated_hours': float(assignment.allocated_hours),
                'resource_id': assignment.resource.id,
                'task_id': assignment.task.id,
                'skill': skill.name
            })
        
        return data

    def _determine_forecast_method(self, historical_data):
        """Determine the best forecasting method based on available data"""
        data_days = len(set(d['date'] for d in historical_data))
        total_points = len(historical_data)
        
        if data_days < 7 or total_points < 10:
            return "insufficient", 0
        elif data_days < 30:
            return "bootstrap", 1  # Basic projections using team capacity
        elif data_days < 90:
            return "trend", 2      # Trend-based forecasts
        elif data_days < 180:
            return "statistical", 3 # Statistical forecasting
        else:
            return "advanced", 4   # Advanced predictive modeling
    
    def _generate_bootstrap_forecast(self, historical_data, days_ahead=30):
        """Bootstrap mode: Use team capacity + industry benchmarks"""
        from resources.models import Resource
        
        forecasts = []
        
        # Get all roles and their typical utilization
        roles_data = {}
        for record in historical_data:
            role = record['role']
            if role not in roles_data:
                roles_data[role] = []
            roles_data[role].append(record['allocated_hours'])
        
        # Industry benchmarks for utilization by role
        industry_benchmarks = {
            'Senior Developer': 85,
            'Developer': 80,
            'Junior Developer': 75,
            'Project Manager': 70,
            'Designer': 75,
            'QA Engineer': 80,
            'DevOps Engineer': 85,
            'Business Analyst': 75,
        }
        
        future_date = timezone.now().date() + timedelta(days=1)
        
        for role, hours_list in roles_data.items():
            # Use recent average or industry benchmark
            if hours_list:
                recent_avg = sum(hours_list[-5:]) / len(hours_list[-5:])  # Last 5 data points
            else:
                recent_avg = 40  # Default 40 hours per week
            
            # Apply industry benchmark confidence
            benchmark_util = industry_benchmarks.get(role, 80)
            predicted_demand = recent_avg * (benchmark_util / 100)
            
            forecast = ResourceDemandForecast.objects.create(
                forecast_date=timezone.now().date(),
                resource_role=role,
                predicted_demand_hours=max(0, predicted_demand),
                confidence_score=0.5,  # Lower confidence for bootstrap
                period_start=future_date,
                period_end=future_date + timedelta(days=7)
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def _generate_trend_forecast(self, historical_data, days_ahead=30):
        """Trend-based forecasting using rolling averages"""
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        
        forecasts = []
        future_date = timezone.now().date() + timedelta(days=1)
        
        for role in df['role'].unique():
            role_data = df[df['role'] == role].copy()
            role_data = role_data.groupby('date')['allocated_hours'].sum().reset_index()
            role_data = role_data.sort_values('date')
            
            if len(role_data) < 3:
                continue
            
            # Calculate rolling averages
            role_data['ma_7'] = role_data['allocated_hours'].rolling(window=min(7, len(role_data))).mean()
            role_data['ma_14'] = role_data['allocated_hours'].rolling(window=min(14, len(role_data))).mean()
            
            # Use the most recent trend
            recent_trend = role_data['ma_7'].iloc[-1] if not pd.isna(role_data['ma_7'].iloc[-1]) else role_data['allocated_hours'].mean()
            
            # Simple linear trend calculation
            if len(role_data) >= 5:
                x = np.arange(len(role_data))
                y = role_data['allocated_hours'].values
                slope, intercept = np.polyfit(x, y, 1)
                predicted_demand = max(0, intercept + slope * len(role_data))
            else:
                predicted_demand = recent_trend
            
            confidence = min(0.8, 0.4 + (len(role_data) / 100))  # Confidence grows with data
            
            forecast = ResourceDemandForecast.objects.create(
                forecast_date=timezone.now().date(),
                resource_role=role,
                predicted_demand_hours=predicted_demand,
                confidence_score=confidence,
                period_start=future_date,
                period_end=future_date + timedelta(days=7)
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def _generate_statistical_forecast(self, historical_data, days_ahead=30):
        """Statistical forecasting for when we have sufficient data (90+ days)"""
        # This is the original statistical method, extracted for modularity
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
            
            # Simple trend analysis with seasonal adjustment
            role_data = role_data.sort_values('date')
            recent_trend = role_data['allocated_hours'].rolling(window=7).mean().iloc[-1]
            
            if pd.isna(recent_trend):
                recent_trend = role_data['allocated_hours'].mean()
            
            # Apply seasonal adjustment based on quarter
            current_quarter = timezone.now().quarter
            quarter_avg = role_data[role_data['quarter'] == current_quarter]['allocated_hours'].mean()
            overall_avg = role_data['allocated_hours'].mean()
            
            if not pd.isna(quarter_avg) and overall_avg > 0:
                seasonal_factor = quarter_avg / overall_avg
            else:
                seasonal_factor = 1.0
            
            predicted_demand = recent_trend * seasonal_factor
            
            # Calculate confidence based on data variance
            variance = role_data['allocated_hours'].var()
            mean_hours = role_data['allocated_hours'].mean()
            if mean_hours > 0:
                cv = (variance ** 0.5) / mean_hours  # Coefficient of variation
                confidence = max(0.5, min(0.95, 1 - cv))
            else:
                confidence = 0.7
            
            future_date = timezone.now().date() + timedelta(days=1)
            
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
    def get_cost_variance_report(self, start_date=None, end_date=None, project_status=None, client=None):
        """Generate cost variance report with optional filters"""
        projects = Project.objects.all()
        
        # Apply filters
        if project_status:
            projects = projects.filter(status=project_status)
        
        if client:
            projects = projects.filter(manager__username=client)
        
        # Date filtering based on project dates
        if start_date:
            projects = projects.filter(end_date__gte=start_date)
        
        if end_date:
            projects = projects.filter(start_date__lte=end_date)
        
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
