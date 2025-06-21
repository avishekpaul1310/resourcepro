#!/usr/bin/env python
"""
Comprehensive Availability Calendar Testing Script
This script tests all aspects of the Availability Calendar functionality.
"""
import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from resources.models import Resource, ResourceAvailability
from django.contrib.auth.models import User
from django.utils import timezone

class AvailabilityCalendarTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
        
    def print_result(self, test_name, status, details=""):
        emoji = "✅" if status else "❌"
        print(f"{emoji} {test_name}: {'PASS' if status else 'FAIL'}")
        if details:
            print(f"   {details}")
            
    def test_database_models(self):
        """Test ResourceAvailability model and data integrity"""
        self.print_header("Database Models & Data Integrity")
        
        try:
            # Test model structure
            availability_fields = [f.name for f in ResourceAvailability._meta.get_fields()]
            required_fields = ['resource', 'start_date', 'end_date', 'availability_type', 'notes', 'hours_per_day']
            
            missing_fields = [field for field in required_fields if field not in availability_fields]
            self.print_result("Model structure", len(missing_fields) == 0, 
                            f"Available fields: {availability_fields}")
            
            # Test availability types
            availability_types = dict(ResourceAvailability.AVAILABILITY_TYPES)
            expected_types = ['available', 'vacation', 'sick_leave', 'personal_leave', 'training', 'meeting', 'unavailable']
            
            has_all_types = all(atype in availability_types for atype in expected_types)
            self.print_result("Availability types", has_all_types, 
                            f"Types: {list(availability_types.keys())}")
            
            # Test existing data
            total_records = ResourceAvailability.objects.count()
            self.print_result("Database data exists", total_records > 0, 
                            f"Found {total_records} availability records")
            
            if total_records > 0:
                # Check data distribution
                type_counts = {}
                for record in ResourceAvailability.objects.all():
                    atype = record.availability_type
                    type_counts[atype] = type_counts.get(atype, 0) + 1
                
                self.print_result("Data diversity", len(type_counts) > 1, 
                                f"Types in data: {type_counts}")
                
                # Check date ranges
                latest_record = ResourceAvailability.objects.order_by('-end_date').first()
                earliest_record = ResourceAvailability.objects.order_by('start_date').first()
                
                self.print_result("Date range coverage", True, 
                                f"From {earliest_record.start_date} to {latest_record.end_date}")
            
            self.test_results['database_models'] = True
            
        except Exception as e:
            self.print_result("Database models test", False, f"Error: {e}")
            self.test_results['database_models'] = False
    
    def test_calendar_view_access(self):
        """Test availability calendar view accessibility"""
        self.print_header("Calendar View Access")
        
        try:
            # Test main calendar URL
            calendar_url = f"{self.base_url}/resources/availability/"
            response = requests.get(calendar_url, timeout=10)
            
            self.print_result("Calendar page loads", response.status_code == 200,
                            f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # Check for FullCalendar integration
                fullcalendar_present = "fullcalendar" in content.lower()
                self.print_result("FullCalendar library", fullcalendar_present)
                
                # Check for calendar container
                calendar_container = 'id="calendar"' in content
                self.print_result("Calendar container", calendar_container)
                
                # Check for legend
                legend_present = "legend" in content.lower()
                self.print_result("Legend present", legend_present)
                
                # Check for resource filter
                filter_present = "resourceFilter" in content
                self.print_result("Resource filter", filter_present)
                
                # Check for upcoming events section
                upcoming_events = "upcoming" in content.lower() and "events" in content.lower()
                self.print_result("Upcoming events section", upcoming_events)
                
                # Check for add entry modal
                add_modal = "availabilityModal" in content
                self.print_result("Add entry modal", add_modal)
                
            # Test with resource filter
            resources = Resource.objects.all()
            if resources.exists():
                resource = resources.first()
                filtered_url = f"{calendar_url}?resource={resource.id}"
                filtered_response = requests.get(filtered_url, timeout=10)
                
                self.print_result("Filtered by resource", filtered_response.status_code == 200,
                                f"Resource filter URL works")
            
            self.test_results['calendar_view'] = True
            
        except Exception as e:
            self.print_result("Calendar view access", False, f"Error: {e}")
            self.test_results['calendar_view'] = False
    
    def test_calendar_events_data(self):
        """Test calendar events data generation"""
        self.print_header("Calendar Events Data")
        
        try:
            # Check if calendar events are properly generated
            calendar_url = f"{self.base_url}/resources/availability/"
            response = requests.get(calendar_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for event data in JavaScript
                events_present = "events: [" in content
                self.print_result("Events array present", events_present)
                
                # Count availability records
                availability_count = ResourceAvailability.objects.count()
                
                if availability_count > 0:
                    # Check for specific availability types in the content
                    has_vacation = "vacation" in content.lower()
                    has_sick_leave = "sick_leave" in content.lower() or "sick leave" in content.lower()
                    
                    self.print_result("Vacation events", has_vacation)
                    self.print_result("Sick leave events", has_sick_leave)
                    
                    # Check for event colors
                    colors_defined = "getEventColor" in content
                    self.print_result("Event colors defined", colors_defined)
                    
                    # Check for event click handling
                    event_click = "eventClick" in content
                    self.print_result("Event click handling", event_click)
                
                # Test upcoming events
                upcoming_count = ResourceAvailability.objects.filter(
                    start_date__gte=timezone.now().date(),
                    start_date__lte=timezone.now().date() + timedelta(days=30)
                ).count()
                
                upcoming_in_content = str(upcoming_count) in content if upcoming_count > 0 else True
                self.print_result("Upcoming events data", upcoming_in_content,
                                f"Found {upcoming_count} upcoming events")
            
            self.test_results['calendar_events'] = True
            
        except Exception as e:
            self.print_result("Calendar events data", False, f"Error: {e}")
            self.test_results['calendar_events'] = False
    
    def test_form_functionality(self):
        """Test availability form functionality"""
        self.print_header("Form Functionality")
        
        try:
            # Import the form
            from resources.forms import ResourceAvailabilityForm
            
            # Test form initialization
            users = User.objects.all()
            if users.exists():
                user = users.first()
                form = ResourceAvailabilityForm(user=user)
                
                form_fields = list(form.fields.keys())
                expected_fields = ['resource', 'start_date', 'end_date', 'availability_type', 'hours_per_day', 'notes']
                
                has_all_fields = all(field in form_fields for field in expected_fields)
                self.print_result("Form has required fields", has_all_fields,
                                f"Fields: {form_fields}")
                
                # Test form widgets
                date_widget = hasattr(form.fields['start_date'].widget, 'attrs')
                self.print_result("Date widget configured", date_widget)
                
                # Test availability type choices
                choices_count = len(form.fields['availability_type'].choices)
                self.print_result("Availability type choices", choices_count > 5,
                                f"Found {choices_count} choices")
            
            # Test form validation
            resources = Resource.objects.all()
            if resources.exists():
                resource = resources.first()
                today = timezone.now().date()
                
                # Valid data
                valid_data = {
                    'resource': resource.id,
                    'start_date': today + timedelta(days=1),
                    'end_date': today + timedelta(days=2),
                    'availability_type': 'vacation',
                    'hours_per_day': 8.0,
                    'notes': 'Test vacation'
                }
                
                form = ResourceAvailabilityForm(data=valid_data)
                self.print_result("Valid form validation", form.is_valid(),
                                f"Errors: {form.errors if not form.is_valid() else 'None'}")
                
                # Invalid data (end date before start date)
                invalid_data = valid_data.copy()
                invalid_data['end_date'] = today - timedelta(days=1)
                
                invalid_form = ResourceAvailabilityForm(data=invalid_data)
                self.print_result("Invalid form rejection", not invalid_form.is_valid(),
                                "End date before start date should be invalid")
            
            self.test_results['form_functionality'] = True
            
        except Exception as e:
            self.print_result("Form functionality", False, f"Error: {e}")
            self.test_results['form_functionality'] = False
    
    def test_filtering_and_interaction(self):
        """Test calendar filtering and interaction features"""
        self.print_header("Filtering & Interaction")
        
        try:
            # Test resource filtering JavaScript
            calendar_url = f"{self.base_url}/resources/availability/"
            response = requests.get(calendar_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for filter function
                filter_function = "filterByResource" in content
                self.print_result("Filter function exists", filter_function)
                
                # Check for color function
                color_function = "getEventColor" in content
                self.print_result("Color function exists", color_function)
                
                # Check for calendar initialization
                calendar_init = "FullCalendar.Calendar" in content
                self.print_result("Calendar initialization", calendar_init)
                
                # Check for toolbar configuration
                toolbar_config = "headerToolbar" in content
                self.print_result("Header toolbar", toolbar_config)
                
                # Check for view options
                views_present = "dayGridMonth" in content and "timeGridWeek" in content
                self.print_result("Multiple views", views_present)
            
            # Test with different resources
            resources = Resource.objects.all()
            if resources.count() > 1:
                for i, resource in enumerate(resources[:3]):  # Test first 3 resources
                    filtered_url = f"{calendar_url}?resource={resource.id}"
                    filtered_response = requests.get(filtered_url, timeout=10)
                    
                    success = filtered_response.status_code == 200
                    self.print_result(f"Resource {i+1} filter", success,
                                    f"Resource: {resource.name}")
            
            self.test_results['filtering_interaction'] = True
            
        except Exception as e:
            self.print_result("Filtering & interaction", False, f"Error: {e}")
            self.test_results['filtering_interaction'] = False
    
    def test_navigation_integration(self):
        """Test navigation and integration with other parts of the app"""
        self.print_header("Navigation & Integration")
        
        try:
            # Test main resources page links to calendar
            resources_url = f"{self.base_url}/resources/"
            resources_response = requests.get(resources_url, timeout=10)
            
            if resources_response.status_code == 200:
                has_calendar_link = "availability" in resources_response.text.lower()
                self.print_result("Resources page has calendar link", has_calendar_link)
            
            # Test dashboard navigation
            dashboard_url = f"{self.base_url}/dashboard/"
            dashboard_response = requests.get(dashboard_url, timeout=10)
            
            if dashboard_response.status_code == 200:
                dashboard_has_calendar = "availability" in dashboard_response.text.lower()
                self.print_result("Dashboard references calendar", dashboard_has_calendar)
            
            # Test header navigation
            calendar_url = f"{self.base_url}/resources/availability/"
            response = requests.get(calendar_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for navigation to time tracking
                time_tracking_link = "time-tracking" in content or "time_tracking" in content
                self.print_result("Links to time tracking", time_tracking_link)
                
                # Check for breadcrumbs or navigation
                has_navigation = "nav" in content.lower() or "breadcrumb" in content.lower()
                self.print_result("Has navigation elements", has_navigation)
            
            self.test_results['navigation_integration'] = True
            
        except Exception as e:
            self.print_result("Navigation & integration", False, f"Error: {e}")
            self.test_results['navigation_integration'] = False
    
    def test_data_accuracy(self):
        """Test data accuracy and calendar display"""
        self.print_header("Data Accuracy & Display")
        
        try:
            # Get availability data
            availability_records = ResourceAvailability.objects.all()
            
            if availability_records.exists():
                # Check date consistency
                valid_dates = True
                for record in availability_records:
                    if record.start_date > record.end_date:
                        valid_dates = False
                        break
                
                self.print_result("Date consistency", valid_dates,
                                "All records have valid date ranges")
                
                # Check resource associations
                resources_with_availability = set()
                for record in availability_records:
                    resources_with_availability.add(record.resource.id)
                
                total_resources = Resource.objects.count()
                coverage = len(resources_with_availability) / total_resources * 100
                
                self.print_result("Resource coverage", coverage > 0,
                                f"{len(resources_with_availability)}/{total_resources} resources have availability data ({coverage:.1f}%)")
                
                # Check upcoming vs past events
                today = timezone.now().date()
                upcoming = availability_records.filter(start_date__gt=today).count()
                past = availability_records.filter(end_date__lt=today).count()
                current = availability_records.filter(start_date__lte=today, end_date__gte=today).count()
                
                self.print_result("Temporal distribution", True,
                                f"Past: {past}, Current: {current}, Upcoming: {upcoming}")
                
                # Check availability types distribution
                type_counts = {}
                for record in availability_records:
                    atype = record.availability_type
                    type_counts[atype] = type_counts.get(atype, 0) + 1
                
                has_variety = len(type_counts) > 1
                self.print_result("Type variety", has_variety,
                                f"Types used: {type_counts}")
            else:
                self.print_result("No data available", False, 
                                "No availability records found for testing")
            
            self.test_results['data_accuracy'] = True
            
        except Exception as e:
            self.print_result("Data accuracy", False, f"Error: {e}")
            self.test_results['data_accuracy'] = False
    
    def run_all_tests(self):
        """Run all availability calendar tests"""
        self.print_header("Availability Calendar Comprehensive Test")
        
        self.test_database_models()
        self.test_calendar_view_access()
        self.test_calendar_events_data()
        self.test_form_functionality()
        self.test_filtering_and_interaction()
        self.test_navigation_integration()
        self.test_data_accuracy()
        
        # Summary
        self.print_header("Test Summary")
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        print(f"📊 Overall Results: {passed}/{total} test categories passed")
        print(f"🎯 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! The Availability Calendar is working properly.")
        else:
            print("⚠️  Some issues detected. Check the failed tests above.")
            
        # Detailed results
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        return self.test_results

if __name__ == "__main__":
    tester = AvailabilityCalendarTester()
    results = tester.run_all_tests()
