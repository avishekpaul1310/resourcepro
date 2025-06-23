#!/usr/bin/env python3
"""
Test AI search functionality using requests to live server
"""
import requests
import json
from bs4 import BeautifulSoup

def test_live_server():
    """Test AI search on live Django server"""
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    print("🔍 Testing AI Search Functionality on Live Server")
    print("=" * 60)
    
    # Get CSRF token from login page
    try:
        login_page = session.get(f"{base_url}/admin/login/")
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        print(f"✅ Got CSRF token: {csrf_token[:20]}...")
    except Exception as e:
        print(f"❌ Error getting CSRF token: {e}")
        return
    
    # Login as admin
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin',
            'csrfmiddlewaretoken': csrf_token,
            'next': '/'
        }
        login_response = session.post(f"{base_url}/admin/login/", data=login_data)
        if login_response.status_code == 200 and 'login' not in login_response.url:
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test pages
    pages = [
        ('Dashboard', '/'),
        ('Projects', '/projects/'),
        ('Resources', '/resources/'),
        ('Allocation', '/allocation/'),
        ('Analytics', '/analytics/')
    ]
    
    print("\n🔍 Testing AI search elements on all pages:")
    
    for page_name, url in pages:
        print(f"\n📄 {page_name} ({url}):")
        try:
            response = session.get(f"{base_url}{url}")
            if response.status_code != 200:
                print(f"  ❌ Page not accessible (status: {response.status_code})")
                continue
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for AI search elements
            search_input = soup.find('input', {'id': 'nliSearchInput'}) is not None
            results_container = soup.find('div', {'id': 'nliResults'}) is not None
            voice_btn = soup.find('button', {'id': 'voiceBtn'}) is not None
            clear_btn = soup.find('button', {'id': 'clearBtn'}) is not None
            has_ai_js = 'ai_dashboard.js' in response.text
            
            print(f"  {'✅' if search_input else '❌'} Search Input")
            print(f"  {'✅' if results_container else '❌'} Results Container")
            print(f"  {'✅' if voice_btn else '❌'} Voice Button")
            print(f"  {'✅' if clear_btn else '❌'} Clear Button")
            print(f"  {'✅' if has_ai_js else '❌'} AI Dashboard JS")
            
        except Exception as e:
            print(f"  ❌ Error testing {page_name}: {e}")
    
    print("\n🔍 Testing AI query responses:")
    
    # Get CSRF token for API calls
    try:
        csrf_response = session.get(f"{base_url}/")
        csrf_soup = BeautifulSoup(csrf_response.content, 'html.parser')
        csrf_input = csrf_soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            api_csrf_token = csrf_input['value']
        else:
            # Try to get from cookie
            api_csrf_token = session.cookies.get('csrftoken', csrf_token)
        print(f"✅ Got API CSRF token: {api_csrf_token[:20]}...")
    except Exception as e:
        print(f"❌ Error getting API CSRF token: {e}")
        api_csrf_token = csrf_token
    
    test_queries = [
        "list all projects",
        "show available resources", 
        "what tasks need assignment"
    ]
    
    for query in test_queries:
        try:
            headers = {
                'X-CSRFToken': api_csrf_token,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"{base_url}/"
            }
            
            ai_response = session.post(f"{base_url}/ai-query/", 
                                     data={'query': query}, 
                                     headers=headers)
            
            if ai_response.status_code == 200:
                response_data = ai_response.json()
                
                # Check response structure
                response_obj = response_data.get('response', {})
                has_text = 'text' in response_obj
                has_data = 'data' in response_obj
                has_type = 'type' in response_obj
                
                print(f"  ✅ '{query}': text={has_text}, data={has_data}, type={has_type}")
                
                if has_text and response_obj['text']:
                    text_preview = response_obj['text'][:80] + "..." if len(response_obj['text']) > 80 else response_obj['text']
                    print(f"     Preview: {text_preview}")
            else:
                print(f"  ❌ '{query}': Status {ai_response.status_code}")
                print(f"     Response: {ai_response.text[:200]}...")
                
        except Exception as e:
            print(f"  ❌ '{query}': Error - {e}")
    
    print("\n🎉 Live Server AI Search Test Complete!")

if __name__ == "__main__":
    import time
    print("Waiting for server to start...")
    time.sleep(3)
    test_live_server()
