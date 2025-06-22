#!/usr/bin/env python3
"""
Test script to verify voice search functionality
"""
import subprocess
import time
import webbrowser
import os

def test_voice_search():
    print("🎤 Voice Search Test Script")
    print("=" * 50)
    
    # Check if server is running
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/')
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("Please make sure the Django server is running with: python manage.py runserver")
        return
    
    # Open test page
    test_file = os.path.join(os.getcwd(), 'voice_search_test.html')
    if os.path.exists(test_file):
        print(f"🌐 Opening test page: {test_file}")
        webbrowser.open(f'file://{test_file}')
    else:
        print("❌ Test file not found")
    
    # Open dashboard
    print("🌐 Opening dashboard: http://127.0.0.1:8000/dashboard/")
    webbrowser.open('http://127.0.0.1:8000/dashboard/')
    
    print("\n📋 Manual Test Steps:")
    print("1. Check if the microphone icon appears in the search bar")
    print("2. Click the microphone icon")
    print("3. Allow microphone permissions if prompted")
    print("4. Speak a query like 'Who is available for a new project?'")
    print("5. Check if the speech is recognized and processed")
    print("6. Verify that search results appear")
    
    print("\n🔧 Troubleshooting:")
    print("- Ensure you're using HTTPS or localhost")
    print("- Check browser microphone permissions")
    print("- Use Chrome, Edge, or Firefox (best support)")
    print("- Check browser console for JavaScript errors")
    
    print("\n✅ Test completed. Check the browser windows that opened.")

if __name__ == "__main__":
    test_voice_search()
