from django.contrib import admin
from .models import (
    ResourceDemandForecast, HistoricalUtilization,
    ProjectCostTracking, SkillDemandAnalysis
)


@admin.register(ResourceDemandForecast)
class ResourceDemandForecastAdmin(admin.ModelAdmin):
    list_display = ['resource_role', 'forecast_date', 'predicted_demand_hours', 'confidence_score', 'created_at']
    list_filter = ['resource_role', 'forecast_date', 'created_at']
    search_fields = ['resource_role']
    readonly_fields = ['created_at']
    ordering = ['-forecast_date']


@admin.register(HistoricalUtilization)
class HistoricalUtilizationAdmin(admin.ModelAdmin):
    list_display = ['resource', 'date', 'utilization_percentage', 'created_at']
    list_filter = ['resource', 'date', 'created_at']
    search_fields = ['resource__name']
    readonly_fields = ['created_at']
    ordering = ['-date']


@admin.register(ProjectCostTracking)
class ProjectCostTrackingAdmin(admin.ModelAdmin):
    list_display = ['project', 'date', 'estimated_cost', 'actual_cost', 'budget_variance']
    list_filter = ['project', 'date']
    search_fields = ['project__name']
    readonly_fields = ['budget_variance']
    ordering = ['-date']


@admin.register(SkillDemandAnalysis)
class SkillDemandAnalysisAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'analysis_date', 'current_demand', 'available_resources', 'demand_score']
    list_filter = ['skill_name', 'analysis_date']
    search_fields = ['skill_name']
    readonly_fields = ['analysis_date']
    ordering = ['-analysis_date']
