from django.contrib import admin
from .models import Skill, Resource, ResourceSkill, TimeEntry, ResourceAvailability

class ResourceSkillInline(admin.TabularInline):
    model = ResourceSkill
    extra = 1

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'capacity', 'cost_per_hour')
    search_fields = ('name', 'role')
    list_filter = ('role', 'capacity')
    inlines = [ResourceSkillInline]

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['resource', 'task', 'date', 'hours', 'is_billable', 'created_at']
    list_filter = ['resource', 'task', 'date', 'is_billable', 'created_at']
    search_fields = ['resource__name', 'task__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
    date_hierarchy = 'date'

@admin.register(ResourceAvailability)
class ResourceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['resource', 'availability_type', 'start_date', 'end_date', 'created_at']
    list_filter = ['resource', 'availability_type', 'start_date', 'created_at']
    search_fields = ['resource__user__first_name', 'resource__user__last_name', 'notes']
    readonly_fields = ['created_at']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'