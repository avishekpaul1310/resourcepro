#!/usr/bin/env python
"""
Test NLI API with proper CSRF handling
"""
import requests
import re
import json

def get_csrf_token():
    """Get CSRF token from the dashboard page"""
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard/")
        if response.status_code == 200:
            # Look for CSRF token in the response
            csrf_match = re.search(r'name=[\'"]csrfmiddlewaretoken[\'"] value=[\'"]([^\'"]+)[\'"]', response.text)
            if csrf_match:
                return csrf_match.group(1)
        return None
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
        return None

def test_nli_with_csrf():
    """Test NLI API with proper CSRF token"""
    print("Getting CSRF token...")
    csrf_token = get_csrf_token()
    
    if not csrf_token:
        print("Could not get CSRF token")
        return
        
    print(f"CSRF token: {csrf_token[:20]}...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First get the dashboard page to set session
    session.get("http://127.0.0.1:8000/dashboard/")
    
    # Test query
    query = "who is the most active resource in all projects?"
    print(f"\nTesting query: '{query}'")
    
    try:
        response = session.post(
            "http://127.0.0.1:8000/dashboard/api/nli-query/",
            json={"query": query},
            headers={
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token,
                "Referer": "http://127.0.0.1:8000/dashboard/"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nli_with_csrf()
