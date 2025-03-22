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
        
        # Get assigned hours for the period
        assigned_hours = Assignment.objects.filter(
            resource=self,
            task__start_date__lte=end_date,
            task__end_date__gte=start_date
        ).aggregate(total=models.Sum('allocated_hours'))['total'] or 0
        
        # Calculate utilization
        if available_hours > 0:
            utilization = (assigned_hours / available_hours) * 100
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