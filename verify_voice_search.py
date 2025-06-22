#!/usr/bin/env python3
"""
Comprehensive voice search verification script
"""
import os
import json
import re

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_file_contains(file_path, pattern, description):
    """Check if a file contains a specific pattern"""
    if not os.path.exists(file_path):
        print(f"❌ {description}: File {file_path} not found")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content, re.IGNORECASE):
                print(f"✅ {description}: Found in {file_path}")
                return True
            else:
                print(f"❌ {description}: Not found in {file_path}")
                return False
    except Exception as e:
        print(f"❌ {description}: Error reading {file_path} - {e}")
        return False

def main():
    print("🔍 Voice Search Verification Script")
    print("=" * 60)
    
    base_path = os.getcwd()
    
    # Check essential files
    print("\n📁 File Existence Check:")
    files_to_check = [
        ("static/js/ai_dashboard.js", "Main AI Dashboard JavaScript"),
        ("dashboard/templates/dashboard/nli_search.html", "NLI Search Template"),
        ("dashboard/templates/dashboard/dashboard.html", "Dashboard Template"),
        ("templates/includes/header.html", "Header Template"),
        ("dashboard/views.py", "Dashboard Views"),
        ("dashboard/urls.py", "Dashboard URLs"),
        ("dashboard/ai_services.py", "AI Services")
    ]
    
    all_files_exist = True
    for file_path, description in files_to_check:
        full_path = os.path.join(base_path, file_path)
        if not check_file_exists(full_path, description):
            all_files_exist = False
    
    # Check JavaScript functions
    print("\n🔧 JavaScript Function Check:")
    js_file = os.path.join(base_path, "static/js/ai_dashboard.js")
    js_functions = [
        (r"function toggleVoiceSearch", "Voice Search Toggle Function"),
        (r"function initializeNLISearch", "NLI Search Initialization"),
        (r"function processNLIQuery", "NLI Query Processing"),
        (r"function showQuickSuggestions", "Quick Suggestions"),
        (r"function clearNLISearch", "Clear Search Function"),
        (r"SpeechRecognition", "Speech Recognition API Usage"),
        (r"webkitSpeechRecognition", "WebKit Speech Recognition")
    ]
    
    js_functions_ok = True
    for pattern, description in js_functions:
        if not check_file_contains(js_file, pattern, description):
            js_functions_ok = False
    
    # Check HTML elements
    print("\n🏷️  HTML Element Check:")
    nli_template = os.path.join(base_path, "dashboard/templates/dashboard/nli_search.html")
    html_elements = [
        (r'id="nliSearchInput"', "Search Input Element"),
        (r'id="voiceBtn"', "Voice Button Element"),
        (r'id="clearBtn"', "Clear Button Element"),
        (r'id="nliResults"', "Results Container"),
        (r'fa-microphone', "Microphone Icon"),
        (r'btn-voice', "Voice Button Class"),
        (r'@keyframes pulse', "Pulse Animation for Recording State")
    ]
    
    html_elements_ok = True
    for pattern, description in html_elements:
        if not check_file_contains(nli_template, pattern, description):
            html_elements_ok = False
    
    # Check backend
    print("\n🗄️  Backend Check:")
    backend_files = [
        ("dashboard/views.py", r"def process_nli_query", "NLI Query View"),
        ("dashboard/urls.py", r"nli-query", "NLI Query URL"),
        ("dashboard/ai_services.py", r"class NaturalLanguageInterfaceService", "NLI Service Class")
    ]
    
    backend_ok = True
    for file_path, pattern, description in backend_files:
        full_path = os.path.join(base_path, file_path)
        if not check_file_contains(full_path, pattern, description):
            backend_ok = False
    
    # Check template inclusion
    print("\n📄 Template Inclusion Check:")
    header_file = os.path.join(base_path, "templates/includes/header.html")
    template_inclusion_ok = check_file_contains(header_file, r"nli_search\.html", "NLI Search Template Inclusion")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY:")
    print(f"📁 Files: {'✅ All found' if all_files_exist else '❌ Missing files'}")
    print(f"🔧 JavaScript: {'✅ All functions present' if js_functions_ok else '❌ Missing functions'}")
    print(f"🏷️  HTML Elements: {'✅ All elements present' if html_elements_ok else '❌ Missing elements'}")
    print(f"🗄️  Backend: {'✅ All components present' if backend_ok else '❌ Missing components'}")
    print(f"📄 Template: {'✅ Properly included' if template_inclusion_ok else '❌ Not included'}")
    
    overall_status = all_files_exist and js_functions_ok and html_elements_ok and backend_ok and template_inclusion_ok
    
    if overall_status:
        print("\n🎉 OVERALL STATUS: ✅ Voice search should be working!")
        print("\n🎯 Next Steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Open http://127.0.0.1:8000/dashboard/")
        print("3. Look for the microphone icon in the search bar")
        print("4. Click it and test voice recognition")
    else:
        print("\n⚠️  OVERALL STATUS: ❌ Issues detected that may prevent voice search from working")
        print("\n🔧 Recommended Actions:")
        print("1. Fix the missing components identified above")
        print("2. Run this script again to verify fixes")
        print("3. Check browser console for JavaScript errors")
    
    print("\n💡 Troubleshooting Tips:")
    print("- Voice search requires HTTPS or localhost")
    print("- Browser must support Web Speech API")
    print("- User must grant microphone permissions")
    print("- Works best in Chrome, Edge, and Firefox")

if __name__ == "__main__":
    main()
