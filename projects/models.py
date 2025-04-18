from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from resources.models import Skill

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='planning')
    priority = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=3)  # 1-5 scale
    color = models.CharField(max_length=7, default="#4F46E5")  # For UI display
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_completion_percentage(self):
        """Calculate the project completion percentage based on weighted tasks and partial completion."""
        tasks = self.tasks.all()
        if not tasks:
            return 0
        
        total_estimated_hours = sum(task.estimated_hours for task in tasks)
        if total_estimated_hours == 0:
            return 0
            
        # Calculate completed hours based on task completion percentages
        completed_hours = sum(
            task.estimated_hours * (task.completion_percentage / 100) 
            for task in tasks
        )
        
        return int((completed_hours / total_estimated_hours) * 100)
    
    class Meta:
        ordering = ['-start_date']

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    estimated_hours = models.IntegerField()
    actual_hours = models.IntegerField(blank=True, null=True)
    skills_required = models.ManyToManyField(Skill, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ], default='not_started')
    completion_percentage = models.IntegerField(default=0, help_text="Percentage of task completed (0-100)")
    priority = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=3)  # 1-5 scale
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"
    
    def save(self, *args, **kwargs):
        # Automatically set completion to 100% when status is completed
        if self.status == 'completed' and self.completion_percentage != 100:
            self.completion_percentage = 100
        # Reset completion to 0% when task is marked as not started
        elif self.status == 'not_started' and self.completion_percentage != 0:
            self.completion_percentage = 0
        # Set a default of 50% when status changes to in_progress and completion is still 0%
        elif self.status == 'in_progress' and self.completion_percentage == 0:
            self.completion_percentage = 50
        # If blocked, keep the current percentage but ensure it's not 100%
        elif self.status == 'blocked' and self.completion_percentage == 100:
            self.completion_percentage = 90
            
        super().save(*args, **kwargs)
    
    @property
    def is_assigned(self):
        """Check if task has any resources assigned."""
        return self.assignments.exists()
    
    @property
    def is_overdue(self):
        """Check if task is overdue."""
        return self.end_date < timezone.now().date() and self.status != 'completed'
    
    class Meta:
        ordering = ['project', 'start_date']