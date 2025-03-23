from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from resources.models import Resource
from projects.models import Project, Task
from allocation.models import Assignment

class EdgeCaseTests(TestCase):
    def test_utilization_weekend_only_task(self):
        """Test task that only spans weekends (should have 0 work days)"""
        # Create a resource
        resource = Resource.objects.create(name='Weekend Resource', capacity=40)
        
        # Find a Saturday
        today = timezone.now().date()
        days_until_saturday = (5 - today.weekday()) % 7
        saturday = today + timedelta(days=days_until_saturday)
        sunday = saturday + timedelta(days=1)
        
        # Create a project and task that only spans the weekend
        project = Project.objects.create(
            name='Weekend Project',
            start_date=saturday,
            end_date=sunday + timedelta(days=7),
            status='active'
        )
        
        task = Task.objects.create(
            project=project,
            name='Weekend Task',
            start_date=saturday,
            end_date=sunday,
            estimated_hours=20,
            status='not_started'
        )
        
        # Assign the task
        Assignment.objects.create(
            resource=resource,
            task=task,
            allocated_hours=20
        )
        
        # Check utilization for exactly this weekend - should handle 0 work days gracefully
        utilization = resource.current_utilization(start_date=saturday, end_date=sunday)
        self.assertEqual(utilization, 0)  # Should not raise divide by zero error
    
    def test_task_across_months(self):
        """Test task that spans multiple months"""
        # Create a resource
        resource = Resource.objects.create(name='Monthly Resource', capacity=40)
        
        # Create a task that spans 3 months
        today = timezone.now().date()
        first_of_month = today.replace(day=1)
        three_months_later = (first_of_month + timedelta(days=90)).replace(day=1) - timedelta(days=1)
        
        project = Project.objects.create(
            name='Long Project',
            start_date=first_of_month,
            end_date=three_months_later + timedelta(days=30),
            status='active'
        )
        
        task = Task.objects.create(
            project=project,
            name='Cross-Month Task',
            start_date=first_of_month,
            end_date=three_months_later,
            estimated_hours=480,  # 40 hours/week * 12 weeks
            status='not_started'
        )
        
        # Assign the task
        Assignment.objects.create(
            resource=resource,
            task=task,
            allocated_hours=480
        )
        
        # Check first month utilization - should be 100%
        next_month = (first_of_month + timedelta(days=32)).replace(day=1)
        end_of_first_month = next_month - timedelta(days=1)
        
        first_month_utilization = resource.current_utilization(
            start_date=first_of_month, 
            end_date=end_of_first_month
        )
        
        self.assertAlmostEqual(first_month_utilization, 100, delta=5)