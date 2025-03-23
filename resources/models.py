from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Resource(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    skills = models.ManyToManyField(Skill, through='ResourceSkill')
    capacity = models.IntegerField(default=40)  # Hours per week
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    color = models.CharField(max_length=7, default="#4F46E5")  # For UI display
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def current_utilization(self, start_date=None, end_date=None):
        """
        Calculate the resource utilization percentage based on assignments.
    
        Returns a percentage value (0-100+).
        """
        from allocation.models import Assignment  # Import here to avoid circular import
        
        # Use current week if dates not specified
        if start_date is None:
            # Get the start of the current week (Monday)
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        if end_date is None:
            # End of current week (Sunday)
            end_date = start_date + timedelta(days=6)
        
        # Calculate work days in the period
        total_days = (end_date - start_date).days + 1
        work_days = sum(1 for i in range(total_days) 
                        if (start_date + timedelta(days=i)).weekday() < 5)
        
        # Calculate hours available in the period
        available_hours = (self.capacity / 5) * work_days  # Assuming 5-day work week
        
        # Get assignments for the period
        assignments = Assignment.objects.filter(
            resource=self,
            task__start_date__lte=end_date,
            task__end_date__gte=start_date
        )
        
        # Calculate total hours, prorating for tasks that extend beyond the date range
        total_hours = 0
        for assignment in assignments:
            task = assignment.task
            
            # Calculate total work days in the entire task duration
            task_start = max(task.start_date, start_date)
            task_end = min(task.end_date, end_date)
            
            task_days = (task_end - task_start).days + 1
            task_work_days = sum(1 for i in range(task_days)
                                 if (task_start + timedelta(days=i)).weekday() < 5)
            
            # Calculate total work days in the entire task
            full_task_days = (task.end_date - task.start_date).days + 1
            full_task_work_days = sum(1 for i in range(full_task_days)
                                      if (task.start_date + timedelta(days=i)).weekday() < 5)
            
            # Prorate the hours based on the proportion of work days in the period
            if full_task_work_days > 0:
                period_hours = (assignment.allocated_hours * task_work_days) / full_task_work_days
                total_hours += period_hours
        
        # Calculate utilization
        if available_hours > 0:
            utilization = (total_hours / available_hours) * 100
        else:
            utilization = 0
            
        return round(utilization, 1)
    
    class Meta:
        ordering = ['name']

class ResourceSkill(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='resource_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.IntegerField(choices=[(i, i) for i in range(1, 11)])  # 1-10 scale
    
    def __str__(self):
        return f"{self.resource.name} - {self.skill.name} ({self.proficiency})"
    
    class Meta:
        unique_together = ['resource', 'skill']