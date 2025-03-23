from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AuthenticationTests(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_valid(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_invalid(self):
        """Test that invalid login credentials don't allow access"""
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        
        # Just check that the response is a 200 (login page) and not a redirect to dashboard
        self.assertEqual(response.status_code, 200)
        
        # Optional: verify we're still on the login page by checking the URL doesn't redirect
        self.assertNotEqual(response.url if hasattr(response, 'url') else None, reverse('dashboard'))

    def test_logout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))