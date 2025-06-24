"""
Simple test to verify AI Analytics page functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
import json

class AIAnalyticsTest(TestCase):
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_ai_analytics_page_loads(self):
        """Test that the AI Analytics page loads without errors"""
        response = self.client.get('/analytics/ai/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Skill Recommendations')
        self.assertContains(response, 'skill-recommendations-loading')
        # Check that loading div has d-none class by default
        self.assertContains(response, 'id="skill-recommendations-loading" class="text-center d-none"')

    def test_skill_recommendations_endpoint(self):
        """Test the skill recommendations endpoint"""
        response = self.client.get('/analytics/ai/skill-recommendations/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('success', data)

    def test_strategic_recommendations_endpoint(self):
        """Test the strategic recommendations endpoint"""
        response = self.client.get('/analytics/ai/strategic-recommendations/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('success', data)
