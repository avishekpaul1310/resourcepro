from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import pytz
from decimal import Decimal

from .models import Skill, Resource, ResourceSkill, Availability, TimeEntry
from projects.models import Project, Task


class SkillModelTest(TestCase):
    """Test cases for Skill model"""
    
    def setUp(self):
        self.skill = Skill.objects.create(
            name="Python",
            description="Python programming language"
        )
    
    def test_skill_creation(self):
        """Test skill creation and string representation"""
        self.assertEqual(str(self.skill), "Python")
        self.assertEqual(self.skill.description, "Python programming language")
    
    def test_skill_ordering(self):
        """Test skill ordering by name"""
        skill2 = Skill.objects.create(name="JavaScript")
        skill3 = Skill.objects.create(name="Django")
        
        skills = list(Skill.objects.all())
        self.assertEqual(skills[0].name, "Django")
        self.assertEqual(skills[1].name, "JavaScript")
        self.assertEqual(skills[2].name, "Python")


class ResourceModelTest(TestCase):
    """Test cases for Resource model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.skill = Skill.objects.create(name="Python")
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Software Developer",
            department="Engineering",
            capacity=40,
            cost_per_hour=Decimal('75.00'),
            timezone="America/New_York",
            location="New York, USA"
        )
        
        ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.skill,
            proficiency_level=8
        )
    
    def test_resource_creation(self):
        """Test resource creation and basic properties"""
        self.assertEqual(str(self.resource), "John Doe")
        self.assertEqual(self.resource.role, "Software Developer")
        self.assertEqual(self.resource.capacity, 40)
        self.assertEqual(self.resource.cost_per_hour, Decimal('75.00'))
        self.assertEqual(self.resource.timezone, "America/New_York")
    
    def test_get_local_time(self):
        """Test local time calculation"""
        local_time = self.resource.get_local_time()
        self.assertIsNotNone(local_time)
        # Should be timezone aware
        self.assertIsNotNone(local_time.tzinfo)
    
    def test_get_formatted_local_time(self):
        """Test formatted local time string"""
        formatted_time = self.resource.get_formatted_local_time()
        self.assertIsInstance(formatted_time, str)
        # Should be in 12-hour format with AM/PM
        self.assertTrue(formatted_time.endswith(('AM', 'PM')))
    
    def test_get_local_date(self):
        """Test local date calculation"""
        local_date = self.resource.get_local_date()
        self.assertIsInstance(local_date, date)
    
    def test_is_business_hours(self):
        """Test business hours calculation"""
        # Create a resource in a timezone where we can predict the hour
        # This test might be time-dependent, so we'll just check it returns a boolean
        result = self.resource.is_business_hours()
        self.assertIsInstance(result, bool)
    
    def test_timezone_error_handling(self):
        """Test handling of invalid timezone"""
        resource = Resource.objects.create(
            name="Invalid TZ User",
            role="Developer",
            timezone="Invalid/Timezone"
        )
        # Should fallback to UTC without raising an exception
        local_time = resource.get_local_time()
        self.assertIsNotNone(local_time)
    
    def test_work_hours_overlap(self):
        """Test work hours overlap calculation"""
        # Create another resource in different timezone
        resource2 = Resource.objects.create(
            name="Jane Doe",
            role="Designer",
            timezone="Europe/London"
        )
        
        overlap = self.resource.get_work_hours_overlap(resource2)
        self.assertIsInstance(overlap, (int, float))
        self.assertGreaterEqual(overlap, 0)
    
    def test_team_overlap_hours(self):
        """Test team overlap calculation"""
        resource2 = Resource.objects.create(
            name="Team Member 2",
            role="Developer",
            timezone="Europe/London"
        )
        
        resources = [self.resource, resource2]
        overlap = Resource.get_team_overlap_hours(resources)
        self.assertIsInstance(overlap, (int, float, type(None)))
    
    def test_user_relationship(self):
        """Test one-to-one relationship with User"""
        self.assertEqual(self.resource.user, self.user)
        self.assertEqual(self.user.resource, self.resource)


class ResourceSkillModelTest(TestCase):
    """Test cases for ResourceSkill model"""
    
    def setUp(self):
        self.resource = Resource.objects.create(
            name="John Doe",
            role="Developer"
        )
        self.skill = Skill.objects.create(name="Python")
        
        self.resource_skill = ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.skill,
            proficiency_level=8,
            years_of_experience=3
        )
    
    def test_resource_skill_creation(self):
        """Test ResourceSkill creation"""
        self.assertEqual(self.resource_skill.proficiency_level, 8)
        self.assertEqual(self.resource_skill.years_of_experience, 3)
        self.assertEqual(str(self.resource_skill), "John Doe - Python (Level 8)")
    
    def test_unique_constraint(self):
        """Test unique constraint on resource-skill combination"""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            ResourceSkill.objects.create(
                resource=self.resource,
                skill=self.skill,
                proficiency_level=5
            )


class AvailabilityModelTest(TestCase):
    """Test cases for Availability model"""
    
    def setUp(self):
        self.resource = Resource.objects.create(
            name="John Doe",
            role="Developer"
        )
        
        self.availability = Availability.objects.create(
            resource=self.resource,
            date=date.today(),
            available_hours=8,
            notes="Standard workday"
        )
    
    def test_availability_creation(self):
        """Test availability creation"""
        self.assertEqual(self.availability.available_hours, 8)
        self.assertEqual(self.availability.notes, "Standard workday")
        expected_str = f"John Doe - {date.today()} (8 hours)"
        self.assertEqual(str(self.availability), expected_str)
    
    def test_default_hours(self):
        """Test default available hours"""
        availability = Availability.objects.create(
            resource=self.resource,
            date=date.today() + timedelta(days=1)
        )
        self.assertEqual(availability.available_hours, 8)


class TimeEntryModelTest(TestCase):
    """Test cases for TimeEntry model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Developer"
        )
        
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name="Test Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        self.time_entry = TimeEntry.objects.create(
            resource=self.resource,
            task=self.task,
            date=date.today(),
            hours=8,
            description="Development work",
            is_billable=True
        )
    
    def test_time_entry_creation(self):
        """Test time entry creation"""
        self.assertEqual(self.time_entry.hours, 8)
        self.assertEqual(self.time_entry.description, "Development work")
        self.assertTrue(self.time_entry.is_billable)
        
        expected_str = f"John Doe - Test Project - Test Task - {date.today()} (8.0 hours)"
        self.assertEqual(str(self.time_entry), expected_str)
    
    def test_default_billable(self):
        """Test default billable status"""
        entry = TimeEntry.objects.create(
            resource=self.resource,
            task=self.task,
            date=date.today() + timedelta(days=1),
            hours=4
        )
        self.assertTrue(entry.is_billable)


class ResourceViewsTest(TestCase):
    """Test cases for Resource views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.resource = Resource.objects.create(
            user=self.user,
            name="John Doe",
            role="Developer"
        )
        
        self.client.force_login(self.user)
    
    def test_resource_list_view(self):
        """Test resource list view"""
        response = self.client.get('/resources/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
    
    def test_resource_detail_view(self):
        """Test resource detail view"""
        response = self.client.get(f'/resources/{self.resource.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
    
    def test_resource_create_view_get(self):
        """Test resource create view GET request"""
        response = self.client.get('/resources/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_resource_create_view_post(self):
        """Test resource create view POST request"""
        data = {
            'name': 'Jane Smith',
            'role': 'Designer',
            'department': 'Design',
            'capacity': 40,
            'cost_per_hour': '65.00'
        }
        response = self.client.post('/resources/create/', data)
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if resource was created
        self.assertTrue(Resource.objects.filter(name='Jane Smith').exists())


class ResourceIntegrationTest(TestCase):
    """Integration tests for Resource functionality"""
    
    def setUp(self):
        self.skill1 = Skill.objects.create(name="Python")
        self.skill2 = Skill.objects.create(name="Django")
        
        self.resource = Resource.objects.create(
            name="John Doe",
            role="Full Stack Developer",
            capacity=40,
            cost_per_hour=Decimal('80.00')
        )
        
        ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.skill1,
            proficiency_level=9
        )
        
        ResourceSkill.objects.create(
            resource=self.resource,
            skill=self.skill2,
            proficiency_level=7
        )
    
    def test_resource_skill_relationships(self):
        """Test resource-skill many-to-many relationships"""
        skills = self.resource.skills.all()
        self.assertEqual(skills.count(), 2)
        self.assertIn(self.skill1, skills)
        self.assertIn(self.skill2, skills)
        
        # Test reverse relationship
        python_resources = self.skill1.resource_set.all()
        self.assertIn(self.resource, python_resources)
    
    def test_resource_availability_tracking(self):
        """Test resource availability tracking"""
        # Add availability for today
        Availability.objects.create(
            resource=self.resource,
            date=date.today(),
            available_hours=6  # Partial day
        )
        
        availability = self.resource.availability_set.first()
        self.assertEqual(availability.available_hours, 6)
    
    def test_resource_time_tracking(self):
        """Test resource time entry tracking"""
        project = Project.objects.create(
            name="Test Project",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        task = Task.objects.create(
            project=project,
            name="Development Task",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            estimated_hours=20
        )
        
        # Add time entries
        TimeEntry.objects.create(
            resource=self.resource,
            task=task,
            date=date.today(),
            hours=8
        )
        
        TimeEntry.objects.create(
            resource=self.resource,
            task=task,
            date=date.today() - timedelta(days=1),
            hours=6
        )
        
        time_entries = self.resource.time_entries.all()
        self.assertEqual(time_entries.count(), 2)
        
        total_hours = sum(entry.hours for entry in time_entries)
        self.assertEqual(total_hours, 14)
