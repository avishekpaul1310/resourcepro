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
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_completion_percentage(self):
        """Calculate the project completion percentage based on weighted tasks and partial completion."""
        tasks = self.tasks.all()
        if not tasks:
            return 0
        
        total_weighted_completion = 0
        total_estimated_hours = 0
        
        for task in tasks:
            estimated_hours = task.estimated_hours or 0
            completion = task.completion_percentage or 0
            
            total_weighted_completion += (estimated_hours * completion)
            total_estimated_hours += estimated_hours
        
        if total_estimated_hours == 0:
            return 0
        
        return round((total_weighted_completion / total_estimated_hours), 1)
    
    def get_estimated_cost(self):
        """Calculate estimated cost based on allocated resources"""
        total_cost = 0
        for assignment in self.get_all_assignments():
            if assignment.resource.cost_per_hour:
                total_cost += assignment.allocated_hours * assignment.resource.cost_per_hour
        return total_cost
    
    def get_actual_cost(self):
        """Calculate actual cost based on time entries"""
        total_cost = 0
        for task in self.tasks.all():
            for time_entry in task.time_entries.all():
                if time_entry.resource.cost_per_hour:
                    total_cost += time_entry.hours * time_entry.resource.cost_per_hour
        return total_cost
    
    def get_all_assignments(self):
        """Get all assignments for this project"""
        from allocation.models import Assignment
        return Assignment.objects.filter(task__project=self)
    
    def get_budget_variance(self):
        """Calculate budget variance (positive = under budget, negative = over budget)"""
        if not self.budget:
            return None
        return self.budget - self.get_actual_cost()
    
    @property
    def completion(self):
        """Return completion percentage for template usage"""
        return self.get_completion_percentage()
    
    class Meta:
        ordering = ['-created_at']

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
        ('blocked', 'Blocked')    ], default='not_started')
    completion_percentage = models.IntegerField(default=0, help_text="Percentage of task completed (0-100)")
    priority = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=3)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def get_actual_hours(self):
        """Calculate actual hours from time entries"""
        return sum(entry.hours for entry in self.time_entries.all())
    
    def get_estimated_vs_actual_variance(self):
        """Calculate variance between estimated and actual hours"""
        actual = self.get_actual_hours()
        if actual == 0:
            return None
        return self.estimated_hours - actual
    
    def get_time_tracking_efficiency(self):
        """Calculate efficiency percentage (estimated/actual * 100)"""
        actual = self.get_actual_hours()
        if actual == 0:
            return None
        return round((self.estimated_hours / actual) * 100, 1)
    
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