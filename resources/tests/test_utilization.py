from django.test import TestCase
from resources.models import Resource
from projects.models import Project, Task
from allocation.models import Assignment
from django.utils import timezone
from datetime import timedelta

class ResourceUtilizationTests(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        # Start of the current week (Monday)
        self.week_start = self.today - timedelta(days=self.today.weekday())
        self.week_end = self.week_start + timedelta(days=6)
        
        self.resource = Resource.objects.create(
            name='Test Resource',
            role='Developer',
            capacity=40  # 40 hours per week
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=self.week_start,
            end_date=self.week_end + timedelta(days=30),
            status='active'
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            start_date=self.week_start,
            end_date=self.week_end,
            estimated_hours=20,
            status='in_progress'
        )

    def test_utilization_no_assignments(self):
        """Test utilization with no assignments"""
        self.assertEqual(self.resource.current_utilization(), 0)

    def test_utilization_with_assignments(self):
        """Test utilization with assignments"""
        Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=20
        )
        
        # 20 hours out of 40 hours capacity = 50%
        self.assertEqual(self.resource.current_utilization(), 50)

    def test_utilization_overallocated(self):
        """Test utilization when overallocated"""
        Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=60
        )
        
        # 60 hours out of 40 hours capacity = 150%
        self.assertEqual(self.resource.current_utilization(), 150)

    def test_utilization_with_date_range(self):
        """Test utilization calculation for specific date range"""
        next_week_start = self.week_start + timedelta(days=7)
        next_week_end = next_week_start + timedelta(days=6)
        
        future_task = Task.objects.create(
            project=self.project,
            name='Future Task',
            start_date=next_week_start,
            end_date=next_week_end,
            estimated_hours=30,
            status='not_started'
        )
        
        Assignment.objects.create(
            resource=self.resource,
            task=self.task,
            allocated_hours=20
        )
        
        Assignment.objects.create(
            resource=self.resource,
            task=future_task,
            allocated_hours=30
        )
        
        # Current week: 20 hours out of 40 = 50%
        self.assertEqual(self.resource.current_utilization(), 50)
        
        # Next week: 30 hours out of 40 = 75%
        self.assertEqual(
            self.resource.current_utilization(start_date=next_week_start, end_date=next_week_end), 
            75
        )