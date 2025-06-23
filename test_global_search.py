#!/usr/bin/env python
"""
Test script to verify that AI search functionality is now available on all pages
"""
import os
import sys
import django
import webbrowser
import time

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

def test_global_search():
    print("🔍 GLOBAL AI SEARCH TEST")
    print("=" * 60)
    
    # Test URLs - pages where search should now work
    test_pages = [
        {
            "name": "Dashboard",
            "url": "http://127.0.0.1:8000/dashboard/",
            "description": "Original working page"
        },
        {
            "name": "Projects",
            "url": "http://127.0.0.1:8000/projects/",
            "description": "Should now have AI search"
        },
        {
            "name": "Resources",
            "url": "http://127.0.0.1:8000/resources/",
            "description": "Should now have AI search"
        },
        {
            "name": "Allocation",
            "url": "http://127.0.0.1:8000/allocation/",
            "description": "Should now have AI search"
        },
        {
            "name": "Analytics",
            "url": "http://127.0.0.1:8000/analytics/",
            "description": "Should now have AI search"
        }
    ]
    
    print("📋 MANUAL TEST INSTRUCTIONS:")
    print("After opening each page, test the following:")
    print("1. ✅ Search bar is visible in the header")
    print("2. ✅ Microphone icon is present and clickable")
    print("3. ✅ Type a query like 'Who is available for a new project?'")
    print("4. ✅ Press Enter and verify you get AI results")
    print("5. ✅ Click microphone icon and test voice search")
    print("6. ✅ Check browser console (F12) for JavaScript errors")
    print()
    
    # Check if server is running
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("Please start the Django server with: python manage.py runserver")
        return
    
    print("\n🌐 Opening test pages...")
    
    for i, page in enumerate(test_pages):
        print(f"\n📖 Opening {page['name']} ({page['description']})")
        print(f"🔗 URL: {page['url']}")
        
        try:
            webbrowser.open(page['url'])
            print(f"✅ Opened {page['name']}")
            
            if i < len(test_pages) - 1:
                print("⏱️  Waiting 3 seconds before opening next page...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Failed to open {page['name']}: {e}")
    
    print("\n" + "=" * 60)
    print("🧪 TESTING CHECKLIST")
    print("=" * 60)
    
    print("\nFor EACH page you just opened, verify:")
    print("□ Search bar appears in header")
    print("□ Microphone icon is visible")
    print("□ Text search works (try: 'show me available resources')")
    print("□ Voice search works (click mic, speak query)")
    print("□ Results appear in dropdown below search bar")
    print("□ No JavaScript errors in browser console")
    
    print("\n🎯 SUCCESS CRITERIA:")
    print("✅ All 5 pages should have identical search functionality")
    print("✅ Voice and text search should work on every page")
    print("✅ Same AI responses regardless of which page you're on")
    
    print("\n📝 WHAT WAS FIXED:")
    print("- Added ai_dashboard.js to base template (global loading)")
    print("- Removed duplicate loading from dashboard template")
    print("- Search interface was already global via header.html")
    print("- Now JavaScript functionality matches global availability")
    
    print("\n✅ Test completed! Please verify functionality on all pages.")

if __name__ == "__main__":
    test_global_search()
