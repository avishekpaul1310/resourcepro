#!/usr/bin/env python3
"""
Comprehensive test script to verify page-agnostic search functionality
"""
import requests
import time
import json
from urllib.parse import urljoin
import os

def test_search_on_all_pages():
    print("🔍 Testing Page-Agnostic Search Functionality")
    print("=" * 70)
    
    base_url = 'http://127.0.0.1:8000'
    
    # Test server availability
    try:
        response = requests.get(base_url, timeout=10)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Pages to test
    pages_to_test = [
        ('/dashboard/', 'Dashboard'),
        ('/allocation/', 'Allocation'),
        ('/projects/', 'Projects'),
        ('/resources/', 'Resources'),
        ('/analytics/', 'Analytics')
    ]
    
    all_pages_working = True
    
    for page_url, page_name in pages_to_test:
        print(f"\n🔍 Testing {page_name} page...")
        
        try:
            full_url = urljoin(base_url, page_url)
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {page_name} page accessible")
                
                # Check for search elements in the HTML
                html_content = response.text
                
                search_elements = [
                    'id="nliSearchInput"',
                    'id="voiceBtn"',
                    'id="clearBtn"',
                    'class="nli-search-container"',
                    'ai_dashboard.js'
                ]
                
                page_working = True
                for element in search_elements:
                    if element in html_content:
                        print(f"   ✅ {element}")
                    else:
                        print(f"   ❌ Missing: {element}")
                        page_working = False
                        all_pages_working = False
                
                if page_working:
                    print(f"   ✅ {page_name} has all search elements")
                else:
                    print(f"   ❌ {page_name} missing search elements")
                    
            else:
                print(f"❌ {page_name} returned status: {response.status_code}")
                all_pages_working = False
                
        except Exception as e:
            print(f"❌ Error accessing {page_name}: {e}")
            all_pages_working = False
    
    # Test API functionality
    print(f"\n🔧 Testing API functionality...")
    
    try:
        # Get CSRF token
        session = requests.Session()
        response = session.get(base_url)
        csrf_token = session.cookies.get('csrftoken')
        
        if csrf_token:
            print("✅ CSRF token obtained")
            
            # Test API with different query types
            test_queries = [
                'Who is available for a new project?',
                'Show me overallocated resources',
                'What are the upcoming deadlines?',
                'List all projects'
            ]
            
            nli_url = urljoin(base_url, '/dashboard/api/nli-query/')
            
            for query in test_queries:
                test_data = {
                    'query': query,
                    'csrfmiddlewaretoken': csrf_token
                }
                
                headers = {
                    'X-CSRFToken': csrf_token,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': base_url
                }
                
                api_response = session.post(nli_url, data=test_data, headers=headers, timeout=10)
                
                if api_response.status_code == 200:
                    try:
                        response_json = api_response.json()
                        if 'response' in response_json:
                            print(f"   ✅ Query: '{query[:30]}...' - Working")
                        else:
                            print(f"   ❌ Query: '{query[:30]}...' - Invalid response")
                            all_pages_working = False
                    except json.JSONDecodeError:
                        print(f"   ❌ Query: '{query[:30]}...' - Invalid JSON")
                        all_pages_working = False
                else:
                    print(f"   ❌ Query: '{query[:30]}...' - Status {api_response.status_code}")
                    all_pages_working = False
        else:
            print("❌ Could not obtain CSRF token")
            all_pages_working = False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        all_pages_working = False
    
    print("\n" + "=" * 70)
    
    if all_pages_working:
        print("🎉 SUCCESS: Search functionality is working on all pages!")
        print("\n✅ Page-Agnostic Search Status: WORKING")
        print("\nThe search bar should now work consistently across:")
        print("   • Dashboard")
        print("   • Allocation")
        print("   • Projects")
        print("   • Resources")
        print("   • Analytics")
        print("\nBoth text and voice search should function properly.")
        
    else:
        print("❌ ISSUES DETECTED: Some pages have search problems")
        print("\n🔧 Recommended actions:")
        print("   1. Check browser console for JavaScript errors")
        print("   2. Verify static files are properly collected")
        print("   3. Ensure no page-specific conflicts exist")
        print("   4. Test manually in browser")
    
    return all_pages_working

def create_debug_instructions():
    """Create debugging instructions for manual testing"""
    print("\n" + "=" * 70)
    print("🔧 MANUAL TESTING INSTRUCTIONS")
    print("=" * 70)
    
    print("\n1. 📱 TEST EACH PAGE:")
    print("   • Open each page in browser")
    print("   • Look for search bar at top")
    print("   • Verify microphone icon is present")
    
    print("\n2. 🔍 TEST TEXT SEARCH:")
    print("   • Type: 'Who is available?'")
    print("   • Press Enter or wait for results")
    print("   • Verify results appear below search bar")
    
    print("\n3. 🎤 TEST VOICE SEARCH:")
    print("   • Click microphone icon")
    print("   • Allow microphone permissions")
    print("   • Speak: 'Show me all projects'")
    print("   • Verify speech is converted to text and results appear")
    
    print("\n4. 🚨 TROUBLESHOOTING:")
    print("   • Open Browser Console (F12)")
    print("   • Look for JavaScript errors")
    print("   • Check Network tab for failed requests")
    print("   • Verify microphone permissions in browser settings")
    
    print("\n5. 📋 BROWSER CONSOLE TESTS:")
    print("   Run these commands in console:")
    print("   • typeof initializeNLISearch")
    print("   • document.getElementById('nliSearchInput')")
    print("   • document.getElementById('voiceBtn')")
    print("   • nliInitialized")

if __name__ == "__main__":
    success = test_search_on_all_pages()
    create_debug_instructions()
    
    if success:
        print(f"\n🎯 RESULT: Page-agnostic search is working correctly!")
    else:
        print(f"\n⚠️  RESULT: Issues detected, manual verification recommended.")
