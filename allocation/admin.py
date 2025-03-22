from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('resource', 'task', 'allocated_hours')
    search_fields = ('resource__name', 'task__name')
    list_filter = ('resource', 'task__project')