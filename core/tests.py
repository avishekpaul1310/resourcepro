from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch

from .utils import (
    get_week_date_range, 
    get_month_date_range, 
    format_datetime, 
    calculate_date_difference, 
    is_past_due
)


class CoreViewsTest(TestCase):
    """Test cases for core views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_view_unauthenticated(self):
        """Test home view for unauthenticated users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/welcome.html')
    
    def test_home_view_authenticated_redirects_to_dashboard(self):
        """Test home view redirects authenticated users to dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_welcome_view(self):
        """Test welcome view displays correctly"""
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/welcome.html')
    
    def test_welcome_view_authenticated(self):
        """Test welcome view works for authenticated users too"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/welcome.html')


class CoreUtilsTest(TestCase):
    """Test cases for core utility functions"""
    
    def test_get_week_date_range(self):
        """Test get_week_date_range function"""
        with patch('core.utils.timezone.now') as mock_now:
            # Mock a Wednesday (weekday 2)
            mock_now.return_value.date.return_value = date(2023, 6, 14)  # Wednesday
            
            start_date, end_date = get_week_date_range()
            
            # Start should be Monday (2 days before)
            self.assertEqual(start_date, date(2023, 6, 12))
            # End should be Sunday (4 days after)
            self.assertEqual(end_date, date(2023, 6, 18))
    
    def test_get_week_date_range_monday(self):
        """Test get_week_date_range when today is Monday"""
        with patch('core.utils.timezone.now') as mock_now:
            mock_now.return_value.date.return_value = date(2023, 6, 12)  # Monday
            
            start_date, end_date = get_week_date_range()
            
            # Start should be the same day (Monday)
            self.assertEqual(start_date, date(2023, 6, 12))
            # End should be Sunday
            self.assertEqual(end_date, date(2023, 6, 18))
    
    def test_get_month_date_range(self):
        """Test get_month_date_range function"""
        with patch('core.utils.timezone.now') as mock_now:
            # Mock a date in June 2023
            mock_now.return_value.date.return_value = date(2023, 6, 15)
            
            start_date, end_date = get_month_date_range()
            
            # Start should be first day of June
            self.assertEqual(start_date, date(2023, 6, 1))
            # End should be last day of June
            self.assertEqual(end_date, date(2023, 6, 30))
    
    def test_get_month_date_range_december(self):
        """Test get_month_date_range for December (year boundary)"""
        with patch('core.utils.timezone.now') as mock_now:
            mock_now.return_value.date.return_value = date(2023, 12, 15)
            
            start_date, end_date = get_month_date_range()
            
            # Start should be first day of December
            self.assertEqual(start_date, date(2023, 12, 1))
            # End should be last day of December
            self.assertEqual(end_date, date(2023, 12, 31))
    
    def test_get_month_date_range_february_leap_year(self):
        """Test get_month_date_range for February in a leap year"""
        with patch('core.utils.timezone.now') as mock_now:
            mock_now.return_value.date.return_value = date(2024, 2, 15)  # 2024 is leap year
            
            start_date, end_date = get_month_date_range()
            
            # Start should be first day of February
            self.assertEqual(start_date, date(2024, 2, 1))
            # End should be 29th (leap year)
            self.assertEqual(end_date, date(2024, 2, 29))
    
    def test_format_datetime_with_datetime(self):
        """Test format_datetime function with datetime object"""
        test_datetime = timezone.datetime(2023, 6, 15, 14, 30, 0)
        formatted = format_datetime(test_datetime)
        self.assertEqual(formatted, "15 Jun 2023, 14:30")
    
    def test_format_datetime_with_custom_format(self):
        """Test format_datetime function with custom format"""
        test_datetime = timezone.datetime(2023, 6, 15, 14, 30, 0)
        formatted = format_datetime(test_datetime, '%Y-%m-%d %H:%M')
        self.assertEqual(formatted, "2023-06-15 14:30")
    
    def test_format_datetime_with_none(self):
        """Test format_datetime function with None value"""
        formatted = format_datetime(None)
        self.assertEqual(formatted, '')
    
    def test_calculate_date_difference(self):
        """Test calculate_date_difference function"""
        start_date = date(2023, 6, 10)
        end_date = date(2023, 6, 15)
        difference = calculate_date_difference(start_date, end_date)
        self.assertEqual(difference, 5)
    
    def test_calculate_date_difference_negative(self):
        """Test calculate_date_difference with negative difference"""
        start_date = date(2023, 6, 15)
        end_date = date(2023, 6, 10)
        difference = calculate_date_difference(start_date, end_date)
        self.assertEqual(difference, -5)
    
    def test_calculate_date_difference_same_date(self):
        """Test calculate_date_difference with same dates"""
        test_date = date(2023, 6, 15)
        difference = calculate_date_difference(test_date, test_date)
        self.assertEqual(difference, 0)
    
    def test_calculate_date_difference_with_none_start(self):
        """Test calculate_date_difference with None start date"""
        end_date = date(2023, 6, 15)
        difference = calculate_date_difference(None, end_date)
        self.assertEqual(difference, 0)
    
    def test_calculate_date_difference_with_none_end(self):
        """Test calculate_date_difference with None end date"""
        start_date = date(2023, 6, 10)
        difference = calculate_date_difference(start_date, None)
        self.assertEqual(difference, 0)
    
    def test_is_past_due_true(self):
        """Test is_past_due function returns True for past dates"""
        with patch('core.utils.timezone.now') as mock_now:
            mock_now.return_value.date.return_value = date(2023, 6, 15)
            
            past_date = date(2023, 6, 10)
            result = is_past_due(past_date)
            self.assertTrue(result)
    
    def test_is_past_due_false_future(self):
        """Test is_past_due function returns False for future dates"""
        with patch('core.utils.timezone.now') as mock_now:
            mock_now.return_value.date.return_value = date(2023, 6, 15)
            
            future_date = date(2023, 6, 20)
            result = is_past_due(future_date)
            self.assertFalse(result)
    
    def test_is_past_due_false_today(self):
        """Test is_past_due function returns False for today's date"""
        with patch('core.utils.timezone.now') as mock_now:
            mock_now.return_value.date.return_value = date(2023, 6, 15)
            
            today_date = date(2023, 6, 15)
            result = is_past_due(today_date)
            self.assertFalse(result)


class CoreURLsTest(TestCase):
    """Test cases for core URL routing"""
    
    def test_home_url_resolves(self):
        """Test that home URL resolves correctly"""
        url = reverse('home')
        self.assertEqual(url, '/')
    
    def test_welcome_url_resolves(self):
        """Test that welcome URL resolves correctly"""
        url = reverse('welcome')
        self.assertEqual(url, '/welcome/')


class CoreIntegrationTest(TestCase):
    """Integration tests for core functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_journey_unauthenticated(self):
        """Test typical user journey for unauthenticated users"""
        # Visit home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/welcome.html')
        
        # Visit welcome page directly
        response = self.client.get('/welcome/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/welcome.html')
    
    def test_user_journey_authenticated(self):
        """Test typical user journey for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        # Visit home page - should redirect to dashboard
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        
        # Can still access welcome page directly
        response = self.client.get('/welcome/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/welcome.html')
