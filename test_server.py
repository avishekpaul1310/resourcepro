#!/usr/bin/env python
"""
Simple test to check Django server connectivity
"""
import requests

def test_server():
    print("Testing Django server connectivity...")
    
    try:
        # Test main page
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"Main page status: {response.status_code}")
        
        # Test dashboard page  
        response = requests.get("http://127.0.0.1:8000/dashboard/", timeout=5)
        print(f"Dashboard page status: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_server()
