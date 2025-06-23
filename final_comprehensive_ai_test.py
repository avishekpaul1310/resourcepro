#!/usr/bin/env python3
"""
Final comprehensive test of AI search functionality across all pages
"""
import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model
from bs4 import BeautifulSoup

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def test_ai_search_across_all_pages():
    """Test AI search functionality on all major pages"""
    client = Client()
    User = get_user_model()
    
    # Get admin user
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No admin user found")
            return
        print(f"Found admin user: {admin_user.username}")
    except Exception as e:
        print(f"❌ Error getting admin user: {e}")
        return
    
    # Login
    login_success = client.login(username=admin_user.username, password='admin')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Login failed")
        return
    
    # Pages to test
    pages = [
        ('Dashboard', '/'),
        ('Projects', '/projects/'),
        ('Resources', '/resources/'),
        ('Allocation', '/allocation/'),
        ('Analytics', '/analytics/')
    ]
    
    print("\n🔍 Testing AI search elements on all pages:")
    print("=" * 60)
    
    for page_name, url in pages:
        print(f"\n📄 {page_name} ({url}):")
        try:
            response = client.get(url)
            if response.status_code != 200:
                print(f"  ❌ Page not accessible (status: {response.status_code})")
                continue
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for AI search elements
            elements = {
                'Search Input': soup.find('input', {'id': 'nliSearchInput'}),
                'Results Container': soup.find('div', {'id': 'nliResults'}),
                'Voice Button': soup.find('button', {'id': 'voiceBtn'}),
                'Clear Button': soup.find('button', {'id': 'clearBtn'}),
                'AI Dashboard JS': 'ai_dashboard.js' in response.content.decode(),
                'NLI Search Template': 'nli_search.html' in response.content.decode() or soup.find('input', {'id': 'nliSearchInput'}) is not None
            }
            
            for element_name, found in elements.items():
                status = "✅" if found else "❌"
                print(f"  {status} {element_name}")
            
            # Check for potential conflicts
            js_scripts = soup.find_all('script', src=True)
            ai_scripts = [script for script in js_scripts if 'ai_dashboard.js' in script.get('src', '')]
            multiple_ai_scripts = len(ai_scripts) > 1
            
            print(f"  {'❌' if multiple_ai_scripts else '✅'} Multiple AI scripts: {multiple_ai_scripts}")
            
        except Exception as e:
            print(f"  ❌ Error testing {page_name}: {e}")
    
    print("\n🔍 Testing AI query responses from different page contexts:")
    print("=" * 60)
    
    # Test queries from each page context
    test_queries = [
        "list all projects",
        "show available resources", 
        "what tasks need assignment"
    ]
    
    for page_name, url in pages:
        print(f"\n📄 Testing queries from {page_name} context:")
        
        # Set session context by visiting the page first
        try:
            page_response = client.get(url)
            if page_response.status_code != 200:
                print(f"  ❌ Cannot access {page_name}")
                continue
        except Exception as e:
            print(f"  ❌ Error accessing {page_name}: {e}")
            continue
        
        for query in test_queries:
            try:
                # Test the AI query endpoint
                ai_response = client.post('/ai-query/', {
                    'query': query
                }, content_type='application/x-www-form-urlencoded')
                
                if ai_response.status_code == 200:
                    response_data = ai_response.json()
                    
                    # Check response structure
                    has_text = 'text' in response_data.get('response', {})
                    has_data = 'data' in response_data.get('response', {})
                    has_type = 'type' in response_data.get('response', {})
                    
                    print(f"  ✅ '{query}': text={has_text}, data={has_data}, type={has_type}")
                    
                    if has_text:
                        text_preview = response_data['response']['text'][:50] + "..." if len(response_data['response']['text']) > 50 else response_data['response']['text']
                        print(f"     Preview: {text_preview}")
                else:
                    print(f"  ❌ '{query}': Status {ai_response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ '{query}': Error - {e}")
    
    print("\n🎉 AI Search Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_ai_search_across_all_pages()
