from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import pytz

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
    department = models.CharField(max_length=100, default='General')
    skills = models.ManyToManyField(Skill, through='ResourceSkill')
    capacity = models.IntegerField(default=40)  # Hours per week
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    color = models.CharField(max_length=7, default="#4F46E5")  # For UI display
    
    # Remote worker fields
    timezone = models.CharField(
        max_length=100, 
        default='UTC',
        help_text="Resource's timezone (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')"
    )
    location = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Location (e.g., 'New York, USA', 'London, UK', 'Remote')"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_local_time(self):
        """Get current local time for this resource"""
        try:
            tz = pytz.timezone(self.timezone)
            return timezone.now().astimezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            return timezone.now()
    
    def get_formatted_local_time(self):
        """Get formatted local time string"""
        local_time = self.get_local_time()
        return local_time.strftime("%I:%M %p")
    
    def get_local_date(self):
        """Get current local date for this resource"""
        local_time = self.get_local_time()
        return local_time.date()
    
    def is_business_hours(self, start_hour=9, end_hour=17):
        """Check if it's currently business hours for this resource"""
        local_time = self.get_local_time()
        hour = local_time.hour
        # Check if it's a weekday (Monday=0, Sunday=6)
        is_weekday = local_time.weekday() < 5
        return is_weekday and start_hour <= hour < end_hour
    
    def get_work_hours_overlap(self, other_resource, start_hour=9, end_hour=17):
        """Calculate overlapping work hours with another resource"""
        if not other_resource:
            return None
            
        # Get both resources' local times
        my_time = self.get_local_time()
        other_time = other_resource.get_local_time()
        
        # Convert to UTC hours for comparison
        my_start_utc = (my_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)).astimezone(pytz.UTC).hour
        my_end_utc = (my_time.replace(hour=end_hour, minute=0, second=0, microsecond=0)).astimezone(pytz.UTC).hour
        
        other_start_utc = (other_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)).astimezone(pytz.UTC).hour
        other_end_utc = (other_time.replace(hour=end_hour, minute=0, second=0, microsecond=0)).astimezone(pytz.UTC).hour
        
        # Calculate overlap
        overlap_start = max(my_start_utc, other_start_utc)
        overlap_end = min(my_end_utc, other_end_utc)
        
        if overlap_start < overlap_end:
            return overlap_end - overlap_start
        return 0
    
    @staticmethod
    def get_team_overlap_hours(resources, start_hour=9, end_hour=17):
        """Calculate overlapping work hours for a team of resources"""
        if not resources or len(resources) < 2:
            return None
            
        # Find the common overlap for all resources
        overlap_hours = []
        for i in range(24):  # Check each hour of the day in UTC
            hour_overlap = True
            for resource in resources:
                local_time = resource.get_local_time()
                # Convert UTC hour to resource's local time
                utc_time = timezone.now().replace(hour=i, minute=0, second=0, microsecond=0)
                resource_local_hour = utc_time.astimezone(pytz.timezone(resource.timezone)).hour
                
                # Check if this hour falls within the resource's work hours
                if not (start_hour <= resource_local_hour < end_hour):
                    hour_overlap = False
                    break
                    
                # Check if it's a weekday for the resource
                resource_weekday = utc_time.astimezone(pytz.timezone(resource.timezone)).weekday()
                if resource_weekday >= 5:  # Weekend
                    hour_overlap = False
                    break
                    
            if hour_overlap:
                overlap_hours.append(i)
                
        return overlap_hours
    
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
    
    def get_total_cost(self, start_date=None, end_date=None):
        """Calculate total cost for resource assignments in a given period"""
        assignments = self.assignments.all()
        if start_date:
            assignments = assignments.filter(task__start_date__gte=start_date)
        if end_date:
            assignments = assignments.filter(task__end_date__lte=end_date)
        
        total_cost = sum(assignment.allocated_hours * self.cost_per_hour 
                        for assignment in assignments)
        return total_cost
    
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

class ResourceAvailability(models.Model):
    """Track resource availability, vacations, and time off"""
    AVAILABILITY_TYPES = [
        ('available', 'Available'),
        ('vacation', 'Vacation'),
        ('sick_leave', 'Sick Leave'),
        ('personal_leave', 'Personal Leave'),
        ('training', 'Training'),
        ('meeting', 'Meeting'),
        ('unavailable', 'Unavailable'),
    ]
    
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='availability')
    start_date = models.DateField()
    end_date = models.DateField()
    availability_type = models.CharField(max_length=20, choices=AVAILABILITY_TYPES, default='available')
    notes = models.TextField(blank=True, null=True)
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.resource.name} - {self.get_availability_type_display()} ({self.start_date} to {self.end_date})"
    
    class Meta:
        ordering = ['start_date']

class TimeEntry(models.Model):
    """Track actual time spent on tasks"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='time_entries')
    task = models.ForeignKey('projects.Task', on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_billable = models.BooleanField(default=True, help_text="Whether this time entry is billable to the client")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.resource.name} - {self.task.name} ({self.hours}h on {self.date})"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['resource', 'task', 'date']