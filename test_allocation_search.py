#!/usr/bin/env python3

import os
import sys

# Setup Django first
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_allocation_page_ai_search():
    """Test AI search functionality on the allocation page"""
    client = Client()    # Use existing admin user
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Found admin user: {admin_user.username}")
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        return
    
    # Login as admin - we'll force login since we don't know the password
    client.force_login(admin_user)
    print(f"Login successful: True")
    
    # Test allocation page access
    print("\n🔍 Testing Allocation page access...")
    response = client.get('/allocation/')
    print(f"Allocation page status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for required AI search elements
        print("\n🔍 Checking for AI search elements in Allocation page:")
        elements_to_check = [
            ('nliSearchInput', 'id="nliSearchInput"'),
            ('nliResults', 'id="nliResults"'),
            ('voiceBtn', 'id="voiceBtn"'),
            ('clearBtn', 'id="clearBtn"'),
            ('ai_dashboard.js', 'ai_dashboard.js'),
            ('nli_search.html', 'nli-search-container')
        ]
        
        for element_name, search_pattern in elements_to_check:
            found = search_pattern in content
            status = "✅" if found else "❌"
            print(f"{status} {element_name}: {found}")
        
        # Check for JavaScript conflicts
        print("\n🔍 Checking for potential JavaScript conflicts:")
        js_checks = [
            ('ai-allocation-debug.js', 'ai-allocation-debug.js'),
            ('Multiple AI scripts', content.count('ai_dashboard.js') > 1),
            ('CSRF token', 'csrfmiddlewaretoken' in content)        ]
        
        for check_name, condition in js_checks:
            if check_name == 'Multiple AI scripts':
                found = condition
                status = "⚠️" if found else "✅"
                print(f"{status} {check_name}: {found}")
            elif isinstance(condition, str):
                found = condition in content
                status = "✅" if found else "❌"
                print(f"{status} {check_name}: {found}")
            else:
                found = condition
                status = "✅" if found else "❌"
                print(f"{status} {check_name}: {found}")
    
    # Test AI query endpoint from allocation context
    print("\n🔍 Testing AI query endpoint from allocation context...")
    test_queries = [
        "list all projects",
        "show available resources",
        "what tasks need assignment"
    ]
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        response = client.post('/dashboard/api/nli-query/', 
                             {'query': query},
                             content_type='application/json',
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response type: {data.get('response', {}).get('type', 'unknown')}")
                print(f"Has text: {'text' in data.get('response', {})}")
                print(f"Has data: {'data' in data.get('response', {})}")
                print(f"Raw response keys: {list(data.keys())}")
                print(f"Response structure: {data}")
                if 'response' in data and 'text' in data['response']:
                    text_preview = data['response']['text'][:100] + "..." if len(data['response']['text']) > 100 else data['response']['text']
                    print(f"Text preview: {text_preview}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Raw response: {response.content.decode('utf-8')[:200]}...")

if __name__ == "__main__":
    test_allocation_page_ai_search()
