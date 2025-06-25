from django.contrib import admin
from .models import DemoSession, DemoMetrics


@admin.register(DemoSession)
class DemoSessionAdmin(admin.ModelAdmin):
    list_display = ('scenario_name', 'session_id', 'is_active', 'data_loaded', 'created_at')
    list_filter = ('scenario_name', 'is_active', 'data_loaded')
    search_fields = ('session_id', 'scenario_name')
    ordering = ['-created_at']


@admin.register(DemoMetrics)
class DemoMetricsAdmin(admin.ModelAdmin):
    list_display = ('scenario_name', 'total_resources', 'total_projects', 'total_tasks', 'load_duration', 'created_at')
    list_filter = ('scenario_name',)
    ordering = ['-created_at']
