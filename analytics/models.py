from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from resources.models import Resource
from projects.models import Project

class ResourceDemandForecast(models.Model):
    """Store predictive analytics for resource demand"""
    forecast_date = models.DateField()
    resource_role = models.CharField(max_length=100)
    predicted_demand_hours = models.DecimalField(max_digits=8, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2)  # 0.00 to 1.00
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Forecast for {self.resource_role} - {self.forecast_date}"
    
    class Meta:
        ordering = ['-forecast_date']

class HistoricalUtilization(models.Model):
    """Store historical utilization data for analytics"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='historical_utilization')
    date = models.DateField()
    utilization_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    allocated_hours = models.DecimalField(max_digits=6, decimal_places=2)
    available_hours = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.resource.name} - {self.date} ({self.utilization_percentage}%)"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['resource', 'date']

class ProjectCostTracking(models.Model):
    """Track project costs over time"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cost_tracking')
    date = models.DateField()
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2)
    budget_variance = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.name} - Cost Tracking {self.date}"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['project', 'date']

class SkillDemandAnalysis(models.Model):
    """Analyze demand for specific skills"""
    skill_name = models.CharField(max_length=100)
    analysis_date = models.DateField()
    current_demand = models.IntegerField(help_text="Number of tasks requiring this skill")
    available_resources = models.IntegerField(help_text="Number of resources with this skill")
    demand_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Demand/Supply ratio")
    predicted_future_demand = models.IntegerField(help_text="Predicted demand for next month")
    
    def __str__(self):
        return f"{self.skill_name} - {self.analysis_date}"
    
    class Meta:
        ordering = ['-analysis_date']
        unique_together = ['skill_name', 'analysis_date']
