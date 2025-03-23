from django.test import TestCase
from projects.models import Project, Task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class ProjectModelTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='manager123')
        self.today = timezone.now().date()
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            start_date=self.today,
            end_date=self.today + timedelta(days=30),
            manager=self.manager,
            status='active',
            priority=3
        )

    def test_get_completion_percentage_no_tasks(self):
        """Test completion percentage when no tasks exist"""
        self.assertEqual(self.project.get_completion_percentage(), 0)

    def test_get_completion_percentage_with_tasks(self):
        """Test with a mix of completed and incomplete tasks"""
        Task.objects.create(
            project=self.project,
            name='Task 1',
            start_date=self.today,
            end_date=self.today + timedelta(days=5),
            estimated_hours=10,
            status='completed'
        )
        
        Task.objects.create(
            project=self.project,
            name='Task 2',
            start_date=self.today,
            end_date=self.today + timedelta(days=10),
            estimated_hours=20,
            status='in_progress'
        )
        
        # 1 of 2 tasks completed = 50%
        self.assertEqual(self.project.get_completion_percentage(), 50)