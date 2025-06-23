#!/usr/bin/env python3
"""
Simple test script to check if allocation search is now working
"""
import time
import webbrowser
import os

def test_allocation_search():
    print("🔍 Testing Allocation Page Search")
    print("=" * 50)
    
    # Open allocation page
    allocation_url = 'http://127.0.0.1:8000/allocation/'
    print(f"Opening: {allocation_url}")
    
    webbrowser.open(allocation_url)
    
    print("\n📋 MANUAL TEST INSTRUCTIONS:")
    print("=" * 50)
    
    print("\n1. 🔍 LOOK FOR SEARCH BAR:")
    print("   • Check if search bar appears at the top of page")
    print("   • Verify microphone icon is visible")
    print("   • Ensure search input field is present")
    
    print("\n2. 🧪 TEST TEXT SEARCH:")
    print("   • Type: 'Who is available?'")
    print("   • Press Enter or wait a moment")
    print("   • Check if results appear below search bar")
    
    print("\n3. 🎤 TEST VOICE SEARCH:")
    print("   • Click the microphone icon")
    print("   • Allow microphone permissions if prompted")
    print("   • Speak: 'Show me all projects'")
    print("   • Verify speech converts to text and results appear")
    
    print("\n4. 🔧 CHECK BROWSER CONSOLE:")
    print("   • Press F12 to open Developer Tools")
    print("   • Go to Console tab")
    print("   • Look for these messages:")
    print("     - 'NLI Search initialized successfully'")
    print("     - 'Allocation Page: Checking NLI Search'")
    print("   • Check for any red error messages")
    
    print("\n5. 🧪 CONSOLE TESTS:")
    print("   Run these commands in console:")
    print("   • typeof initializeNLISearch")
    print("   • nliInitialized")
    print("   • document.getElementById('nliSearchInput')")
    
    print("\n📝 EXPECTED RESULTS:")
    print("=" * 30)
    print("✅ Search bar visible and functional")
    print("✅ Text search returns AI responses")
    print("✅ Voice search converts speech to text")
    print("✅ No JavaScript errors in console")
    print("✅ Consistent behavior with other pages")
    
    print(f"\n🚨 IF SEARCH STILL NOT WORKING:")
    print("1. Hard refresh the page (Ctrl+F5)")
    print("2. Clear browser cache")
    print("3. Check if Django server is running")
    print("4. Try in different browser (Chrome/Edge)")
    print("5. Check console for specific error messages")

if __name__ == "__main__":
    test_allocation_search()
