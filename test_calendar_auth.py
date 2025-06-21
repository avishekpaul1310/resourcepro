#!/usr/bin/env python
"""
Test the Availability Calendar with proper authentication
"""
import os
import sys
import django
import requests
from requests.sessions import Session

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User
from resources.models import Resource, ResourceAvailability

def test_availability_calendar_with_auth():
    """Test availability calendar with authentication"""
    print("🧪 Testing Availability Calendar with Authentication")
    print("="*60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Create a session to handle cookies/authentication
    session = Session()
    
    try:
        # Step 1: Get login page and CSRF token
        print("📝 Step 1: Getting login page...")
        login_url = f"{base_url}/accounts/login/"
        login_page = session.get(login_url)
        
        if login_page.status_code == 200:
            print("✅ Login page accessible")
            
            # Extract CSRF token
            csrf_token = None
            for line in login_page.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if csrf_token:
                print(f"✅ CSRF token obtained")
                
                # Step 2: Login with admin credentials
                print("🔐 Step 2: Attempting login...")
                login_data = {
                    'username': 'admin',
                    'password': 'admin123',  # Common admin password
                    'csrfmiddlewaretoken': csrf_token
                }
                
                login_response = session.post(login_url, data=login_data)
                
                if login_response.status_code == 302 or "dashboard" in login_response.url:
                    print("✅ Login successful")
                    
                    # Step 3: Access availability calendar
                    print("📅 Step 3: Accessing availability calendar...")
                    calendar_url = f"{base_url}/resources/availability/"
                    calendar_response = session.get(calendar_url)
                    
                    if calendar_response.status_code == 200:
                        print("✅ Availability calendar accessible")
                        
                        content = calendar_response.text
                        
                        # Detailed content analysis
                        print("\n🔍 Calendar Content Analysis:")
                        
                        # Check for FullCalendar
                        if "fullcalendar" in content.lower():
                            print("✅ FullCalendar library loaded")
                        else:
                            print("❌ FullCalendar library missing")
                        
                        # Check for calendar container
                        if 'id="calendar"' in content:
                            print("✅ Calendar container present")
                        else:
                            print("❌ Calendar container missing")
                        
                        # Check for legend
                        if "legend" in content.lower():
                            print("✅ Legend present")
                        else:
                            print("❌ Legend missing")
                        
                        # Check for resource filter
                        if "resourceFilter" in content:
                            print("✅ Resource filter present")
                        else:
                            print("❌ Resource filter missing")
                        
                        # Check for event data
                        if "events: [" in content:
                            print("✅ Event data present")
                        else:
                            print("❌ Event data missing")
                        
                        # Check for upcoming events
                        if "upcoming" in content.lower() and "events" in content.lower():
                            print("✅ Upcoming events section present")
                        else:
                            print("❌ Upcoming events section missing")
                        
                        # Check for modal
                        if "availabilityModal" in content:
                            print("✅ Add availability modal present")
                        else:
                            print("❌ Add availability modal missing")
                        
                        # Save the content for inspection
                        with open("calendar_page_content.html", "w", encoding="utf-8") as f:
                            f.write(content)
                        print("💾 Page content saved to calendar_page_content.html")
                        
                        # Check available data
                        print(f"\n📊 Database Status:")
                        resources_count = Resource.objects.count()
                        availability_count = ResourceAvailability.objects.count()
                        print(f"   Resources: {resources_count}")
                        print(f"   Availability records: {availability_count}")
                        
                        if availability_count > 0:
                            print("\n📋 Sample Availability Records:")
                            for record in ResourceAvailability.objects.all()[:5]:
                                print(f"   • {record.resource.name}: {record.availability_type} ({record.start_date} to {record.end_date})")
                        
                        return True
                    else:
                        print(f"❌ Calendar page error: {calendar_response.status_code}")
                        return False
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    # Try with different password
                    print("🔄 Trying alternative admin credentials...")
                    login_data['password'] = 'password'
                    login_response2 = session.post(login_url, data=login_data)
                    
                    if login_response2.status_code == 302:
                        print("✅ Login successful with alternative password")
                        calendar_url = f"{base_url}/resources/availability/"
                        calendar_response = session.get(calendar_url)
                        print(f"📅 Calendar access: {calendar_response.status_code}")
                        return calendar_response.status_code == 200
                    return False
            else:
                print("❌ Could not extract CSRF token")
                return False
        else:
            print(f"❌ Login page error: {login_page.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_availability_calendar_with_auth()
    if success:
        print("\n🎉 Availability Calendar test completed successfully!")
    else:
        print("\n⚠️ Issues detected with Availability Calendar access.")
