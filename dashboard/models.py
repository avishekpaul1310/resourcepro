from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from resources.models import Resource
from projects.models import Project, Task
import json

class DashboardAIAnalysis(models.Model):
    """
    Store AI-generated dashboard analysis and insights
    """
    ANALYSIS_TYPES = [
        ('daily_briefing', 'Daily Briefing'),
        ('risk_assessment', 'Risk Assessment'),
        ('recommendations', 'Recommendations'),
    ]
    
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    analysis_data = models.JSONField(default=dict)
    summary = models.TextField()
    risks = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['analysis_type', 'created_at']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class RiskCategory(models.Model):
    """Categorize different types of project risks"""
    RISK_TYPES = [
        ('resource', 'Resource & Allocation'),
        ('technical', 'Technical & Quality'),
        ('external', 'External Dependencies'),  
        ('team', 'Team Dynamics'),
        ('business', 'Business & Strategic'),
        ('operational', 'Operational'),
        ('financial', 'Financial & Budget'),
        ('timeline', 'Schedule & Timeline'),
        ('scope', 'Scope & Requirements'),
        ('quality', 'Quality & Standards'),
    ]
    
    name = models.CharField(max_length=100)
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    description = models.TextField()
    severity_weight = models.FloatField(default=1.0)  # Impact multiplier
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_risk_type_display()})"

class DynamicRisk(models.Model):
    """Store dynamically identified risks with AI analysis"""
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    probability = models.FloatField()  # 0.0 to 1.0
    impact_score = models.FloatField()  # 0.0 to 10.0
    
    # Context
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    related_resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)
    
    # AI Analysis
    ai_analysis = models.JSONField(default=dict)  # Store AI analysis data
    suggested_interventions = models.JSONField(default=list)  # AI-suggested interventions
    
    # Status tracking
    status = models.CharField(max_length=20, default='identified')
    identified_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-severity', '-impact_score', '-identified_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"

class InterventionScenario(models.Model):
    """
    Store intervention scenarios and their simulated outcomes
    """
    SCENARIO_TYPES = [
        ('reassignment', 'Task Reassignment'),
        ('overtime', 'Overtime Authorization'),
        ('resource_addition', 'Additional Resource'),
        ('deadline_extension', 'Deadline Extension'),
        ('scope_reduction', 'Scope Reduction'),
        # Enhanced intervention types
        ('training', 'Training & Skill Development'),
        ('process_improvement', 'Process Optimization'),
        ('external_resource', 'External Consultant/Contractor'),
        ('technology_upgrade', 'Technology/Tool Upgrade'),
        ('risk_mitigation', 'Risk Mitigation Plan'),
        ('communication_plan', 'Communication Enhancement'),
        ('quality_assurance', 'Quality Assurance Boost'),
        ('stakeholder_engagement', 'Stakeholder Re-engagement'),
        ('custom', 'Custom Intervention'),
    ]
    
    SCENARIO_STATUS = [
        ('simulated', 'Simulated'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    scenario_type = models.CharField(max_length=30, choices=SCENARIO_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    related_resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)
    
    # Simulation parameters
    simulation_data = models.JSONField(default=dict)
    predicted_outcome = models.JSONField(default=dict)
    estimated_impact = models.TextField()
    success_probability = models.FloatField(default=0.0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_time_impact = models.IntegerField(help_text="Impact in hours", null=True, blank=True)
    
    # Execution tracking
    status = models.CharField(max_length=15, choices=SCENARIO_STATUS, default='simulated')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    # Enhanced fields for dynamic scenarios
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE, null=True, blank=True)
    dynamic_risk = models.ForeignKey(DynamicRisk, on_delete=models.CASCADE, null=True, blank=True)
    intervention_type = models.CharField(max_length=30, choices=SCENARIO_TYPES, default='reassignment')
    
    # Custom intervention details
    custom_intervention_type = models.CharField(max_length=100, blank=True)
    custom_description = models.TextField(blank=True)
    ai_generated = models.BooleanField(default=False)  # Whether AI suggested this intervention
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['scenario_type', 'status']),
            models.Index(fields=['related_project', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class NLIQuery(models.Model):
    """
    Store Natural Language Interface queries and responses
    """
    query_text = models.TextField()
    intent = models.CharField(max_length=100, blank=True)
    entities = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    response_text = models.TextField(blank=True)
    execution_time = models.FloatField(default=0.0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['intent', 'success']),
        ]
    
    def __str__(self):
        return f"Query: {self.query_text[:50]}..."

class AIInsight(models.Model):
    """
    Store specific AI insights and alerts
    """
    INSIGHT_TYPES = [
        ('bottleneck', 'Resource Bottleneck'),
        ('deadline_risk', 'Deadline Risk'),
        ('overallocation', 'Overallocation Warning'),
        ('underutilization', 'Underutilization Alert'),
        ('skill_gap', 'Skill Gap Identified'),
        ('opportunity', 'Optimization Opportunity'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=255)
    description = models.TextField()
    affected_resources = models.ManyToManyField(Resource, blank=True)
    affected_projects = models.ManyToManyField(Project, blank=True)
    affected_tasks = models.ManyToManyField(Task, blank=True)
    
    recommended_actions = models.JSONField(default=list)
    data_context = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['insight_type', 'severity', 'is_active']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_severity_display()} {self.get_insight_type_display()}: {self.title}"
    
    def resolve(self, user=None):
        """Mark this insight as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()

class InterventionTemplate(models.Model):
    """Templates for common intervention strategies by risk type"""
    name = models.CharField(max_length=100)
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE)
    intervention_type = models.CharField(max_length=30, choices=InterventionScenario.SCENARIO_TYPES)
    
    # Template configuration
    template_config = models.JSONField(default=dict)  # Configuration parameters
    success_conditions = models.JSONField(default=list)  # What defines success
    resource_requirements = models.JSONField(default=dict)  # Required resources
    
    # Effectiveness metrics
    average_success_rate = models.FloatField(default=0.0)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    average_time_impact = models.IntegerField(null=True, blank=True)  # in hours
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} for {self.risk_category.name}"
