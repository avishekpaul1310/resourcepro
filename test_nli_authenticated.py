#!/usr/bin/env python
"""
Test the NLI functionality using Django's test client with authentication
"""
import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_nli_with_auth():
    print("Testing NLI API with Django test client (authenticated)...")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='admin')
        print(f"Using existing user: {user.username}")
    except User.DoesNotExist:
        print("No admin user found. Please create one first with: python manage.py createsuperuser")
        return
    
    # Login the client
    login_success = client.force_login(user)
    print(f"Login successful: {login_success}")
    
    test_queries = [
        "who is the most active resource in all projects?",
        "Who is available for a new project?",
        "Show me overallocated resources",
        "What are the upcoming deadlines?"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 40)
        
        try:
            response = client.post(
                '/dashboard/api/nli-query/',
                data=json.dumps({"query": query}),
                content_type='application/json'
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Response:")
                    print(json.dumps(data, indent=2, default=str))
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {e}")
                    print(f"Raw Response: {response.content.decode()[:500]}...")
            else:
                print(f"Error: {response.content.decode()}")
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed.")

if __name__ == "__main__":
    test_nli_with_auth()
