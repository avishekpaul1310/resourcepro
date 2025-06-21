#!/usr/bin/env python
"""
Test NLI API with login
"""
import requests
import re
import json

def login_and_test_nli():
    """Login and test NLI API"""
    session = requests.Session()
    
    # Get login page to get CSRF token
    response = session.get("http://127.0.0.1:8000/accounts/login/")
    if response.status_code != 200:
        print(f"Could not access login page: {response.status_code}")
        return
    
    # Extract CSRF token
    csrf_match = re.search(r'name=[\'"]csrfmiddlewaretoken[\'"] value=[\'"]([^\'"]+)[\'"]', response.text)
    if not csrf_match:
        print("Could not find CSRF token on login page")
        return
    
    csrf_token = csrf_match.group(1)
    print(f"Login CSRF token: {csrf_token[:20]}...")
    
    # Login with admin credentials
    login_data = {
        'username': 'admin',
        'password': 'admin123',  # Assuming this is the admin password
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post("http://127.0.0.1:8000/accounts/login/", data=login_data)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200 and "login" in response.url:
        print("Login failed - check credentials")
        return
    
    # Now test the NLI API
    print("Testing NLI API after login...")
    query = "who is the most active resource in all projects?"
    
    try:
        response = session.post(
            "http://127.0.0.1:8000/dashboard/api/nli-query/",
            json={"query": query},
            headers={
                "Content-Type": "application/json",
                "Referer": "http://127.0.0.1:8000/dashboard/"
            },
            timeout=10
        )
        
        print(f"NLI API Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print("Response:")
                print(json.dumps(data, indent=2))
            else:
                print("Non-JSON response:")
                print(response.text[:500])
        else:
            print(f"Error response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    login_and_test_nli()
