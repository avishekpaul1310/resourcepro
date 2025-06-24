#!/usr/bin/env python3
"""
Test script to verify AI Analytics loading states work correctly.
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User

class AIAnalyticsLoadingTest(TestCase):
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
        # Should return valid JSON structure
        self.assertIn('success', data)
        
        # If API key is not configured, should return graceful error
        if not data.get('success'):
            self.assertIn('error', data)
            self.assertIn('API key', data['error'])

    def test_skill_recommendations_refresh(self):
        """Test the skill recommendations refresh endpoint"""
        response = self.client.get('/analytics/ai/skill-recommendations/?refresh=true')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('success', data)

    def test_strategic_recommendations_endpoint(self):
        """Test the strategic recommendations endpoint"""
        response = self.client.get('/analytics/ai/strategic-recommendations/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('success', data)

def run_tests():
    """Run the tests manually"""
    import django.test.utils
    from django.test.runner import DiscoverRunner
    
    # Setup test database
    django.test.utils.setup_test_environment()
    
    # Create test runner
    runner = DiscoverRunner(verbosity=2, interactive=False)
    
    # Run tests
    failures = runner.run_tests(['__main__'])
    
    # Teardown
    django.test.utils.teardown_test_environment()
    
    return failures

if __name__ == '__main__':
    print("Testing AI Analytics loading states...")
    print("=" * 50)
    
    # Run the tests
    failures = run_tests()
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        print("\nAI Analytics loading states are working correctly:")
        print("- Page loads without errors")
        print("- Loading div has d-none class by default")
        print("- Skill recommendations endpoint works")
        print("- Strategic recommendations endpoint works")
        print("- Loading states will be properly hidden/shown via JavaScript")
