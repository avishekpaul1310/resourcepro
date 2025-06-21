#!/usr/bin/env python
"""
Test script for the Natural Language Interface API
"""
import requests
import json
import sys

def test_nli_api():
    url = "http://127.0.0.1:8000/dashboard/api/nli-query/"
    
    test_queries = [
        "who is the most active resource in all projects?",
        "Who is available for a new project?",
        "Show me overallocated resources",
        "What are the upcoming deadlines?"
    ]
    
    print("Testing NLI API endpoint...")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 30)
        
        try:
            response = requests.post(
                url,
                json={"query": query},
                headers={
                    "Content-Type": "application/json",
                    "X-CSRFToken": "test-token"  # This might need to be handled differently
                },
                timeout=10            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Raw Response: {response.text[:500]}...")  # Show first 500 chars
            
            if response.status_code == 200 and response.text.strip():
                try:
                    data = response.json()
                    print("Parsed JSON Response:")
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {e}")
            else:
                print(f"Error or Empty Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: Cannot connect to server. Make sure Django server is running.")
            break
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed.")

if __name__ == "__main__":
    test_nli_api()
