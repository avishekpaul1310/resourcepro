#!/usr/bin/env python3
"""
Debug script to check allocation page search functionality in detail
"""
import requests
import time
from bs4 import BeautifulSoup
import re

def debug_allocation_search():
    print("🔍 DEBUGGING ALLOCATION PAGE SEARCH")
    print("=" * 60)
    
    base_url = 'http://127.0.0.1:8000'
    
    # Test login first
    session = requests.Session()
      # Get login page to extract CSRF token
    login_page = session.get(f'{base_url}/login/')
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    csrf_token = csrf_input['value'] if csrf_input else None
      # Login
    if csrf_token:
        login_data = {
            'username': 'admin',
            'password': 'admin',
            'csrfmiddlewaretoken': csrf_token
        }
        login_response = session.post(f'{base_url}/login/', data=login_data)
    else:
        # Try direct access to allocation page
        print("⚠️ No CSRF token found, trying direct access")
        login_response = session.get(f'{base_url}/allocation/')
    
    if login_response.status_code == 200:
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    # Get allocation page
    allocation_response = session.get(f'{base_url}/allocation/')
    
    if allocation_response.status_code != 200:
        print(f"❌ Allocation page error: {allocation_response.status_code}")
        return
    
    print("✅ Allocation page loaded")
    
    # Parse HTML
    soup = BeautifulSoup(allocation_response.content, 'html.parser')
    
    # Check for search elements
    print("\n🔍 Checking Search Elements:")
    
    search_input = soup.find('input', {'id': 'nliSearchInput'})
    voice_btn = soup.find('button', {'id': 'voiceBtn'})
    clear_btn = soup.find('button', {'id': 'clearBtn'})
    nli_container = soup.find('div', {'class': 'nli-search-container'})
    
    print(f"Search Input: {'✅ Found' if search_input else '❌ Missing'}")
    print(f"Voice Button: {'✅ Found' if voice_btn else '❌ Missing'}")
    print(f"Clear Button: {'✅ Found' if clear_btn else '❌ Missing'}")
    print(f"NLI Container: {'✅ Found' if nli_container else '❌ Missing'}")
    
    # Check JavaScript files
    print("\n🔍 Checking JavaScript Files:")
    script_tags = soup.find_all('script', {'src': True})
    
    js_files = []
    for script in script_tags:
        src = script.get('src')
        if src:
            js_files.append(src)
    
    ai_dashboard_found = any('ai_dashboard.js' in js for js in js_files)
    ai_allocation_found = any('ai-allocation-debug.js' in js for js in js_files)
    
    print(f"ai_dashboard.js: {'✅ Found' if ai_dashboard_found else '❌ Missing'}")
    print(f"ai-allocation-debug.js: {'✅ Found' if ai_allocation_found else '❌ Missing'}")
    
    print("\nAll JavaScript files loaded:")
    for js_file in js_files:
        print(f"  - {js_file}")
    
    # Check for potential conflicts in HTML
    print("\n🔍 Checking for JavaScript Conflicts:")
    
    # Get all script content
    inline_scripts = soup.find_all('script', string=True)
    all_script_content = ""
    for script in inline_scripts:
        if script.string:
            all_script_content += script.string + "\n"
    
    # Check for function definitions
    conflicts = []
    if 'function initializeAIFeatures' in all_script_content:
        conflicts.append("initializeAIFeatures function defined inline")
    if 'function initializeNLISearch' in all_script_content:
        conflicts.append("initializeNLISearch function defined inline")
    
    if conflicts:
        print("⚠️ Potential conflicts found:")
        for conflict in conflicts:
            print(f"  - {conflict}")
    else:
        print("✅ No obvious JavaScript conflicts detected")
    
    # Test if the search API endpoint works
    print("\n🔍 Testing Search API:")
    
    csrf_token = session.cookies.get('csrftoken')
    if csrf_token:
        test_data = {
            'query': 'test query',
            'csrfmiddlewaretoken': csrf_token
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{base_url}/allocation/'
        }
        
        api_response = session.post(f'{base_url}/dashboard/api/nli-query/', 
                                  data=test_data, headers=headers)
        
        if api_response.status_code == 200:
            print("✅ Search API responding")
            try:
                response_json = api_response.json()
                print(f"✅ Valid JSON response received")
            except:
                print("❌ Invalid JSON response")
        else:
            print(f"❌ Search API error: {api_response.status_code}")
    else:
        print("❌ No CSRF token available")
    
    # Extract and examine the actual HTML structure
    print("\n🔍 HTML Structure Analysis:")
    
    if nli_container:
        print("NLI Container HTML:")
        print(str(nli_container)[:500] + "..." if len(str(nli_container)) > 500 else str(nli_container))
    
    # Check if search input has proper attributes
    if search_input:
        print(f"\nSearch Input attributes:")
        for attr, value in search_input.attrs.items():
            print(f"  {attr}: {value}")
    
    print("\n" + "=" * 60)
    print("🔧 RECOMMENDATIONS:")
    print("1. Open browser console (F12) on allocation page")
    print("2. Check for JavaScript errors")
    print("3. Test: typeof initializeNLISearch")
    print("4. Test: document.getElementById('nliSearchInput')")
    print("5. Test: nliInitialized")

if __name__ == "__main__":
    debug_allocation_search()
