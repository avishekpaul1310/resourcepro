#!/usr/bin/env python
"""
Test NLI API and show raw response
"""
import requests
import re

def get_csrf_token():
    """Get CSRF token from the dashboard page"""
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard/")
        if response.status_code == 200:
            csrf_match = re.search(r'name=[\'"]csrfmiddlewaretoken[\'"] value=[\'"]([^\'"]+)[\'"]', response.text)
            if csrf_match:
                return csrf_match.group(1)
        return None
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
        return None

def test_raw_response():
    """Test NLI API and show raw response"""
    csrf_token = get_csrf_token()
    
    if not csrf_token:
        print("Could not get CSRF token")
        return
        
    session = requests.Session()
    session.get("http://127.0.0.1:8000/dashboard/")
    
    query = "who is the most active resource in all projects?"
    
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
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Raw Response: {repr(response.text[:500])}")
        print(f"Full Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_response()
