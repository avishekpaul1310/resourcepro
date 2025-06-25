from django.db import models


class DemoSession(models.Model):
    """Track demo sessions and their status"""
    session_id = models.CharField(max_length=100, unique=True)
    scenario_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    data_loaded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Demo: {self.scenario_name} ({self.session_id})"


class DemoMetrics(models.Model):
    """Track metrics for demo scenarios"""
    scenario_name = models.CharField(max_length=100)
    total_resources = models.IntegerField(default=0)
    total_projects = models.IntegerField(default=0)
    total_tasks = models.IntegerField(default=0)
    total_assignments = models.IntegerField(default=0)
    load_duration = models.FloatField(null=True, blank=True)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Metrics: {self.scenario_name} - {self.total_resources} resources, {self.total_projects} projects"
