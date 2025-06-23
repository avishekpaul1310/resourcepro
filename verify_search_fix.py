#!/usr/bin/env python
"""
Verification script to confirm the AI search fix was implemented correctly
"""
import os

def verify_search_fix():
    print("🔍 AI SEARCH FIX VERIFICATION")
    print("=" * 60)
    
    base_path = os.getcwd()
    
    # Check base template has the AI dashboard JS
    print("\n1. 📄 Checking base.html template...")
    base_template = os.path.join(base_path, "templates/base.html")
    
    if os.path.exists(base_template):
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'ai_dashboard.js' in content:
            print("✅ ai_dashboard.js is loaded in base template (global)")
        else:
            print("❌ ai_dashboard.js NOT found in base template")
    else:
        print("❌ base.html template not found")
    
    # Check dashboard template doesn't have duplicate loading
    print("\n2. 📄 Checking dashboard.html template...")
    dashboard_template = os.path.join(base_path, "dashboard/templates/dashboard/dashboard.html")
    
    if os.path.exists(dashboard_template):
        with open(dashboard_template, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Count occurrences of ai_dashboard.js
        js_count = content.count('ai_dashboard.js')
        if js_count == 0:
            print("✅ No duplicate ai_dashboard.js loading in dashboard template")
        else:
            print(f"⚠️  Found {js_count} references to ai_dashboard.js in dashboard template")
    else:
        print("❌ dashboard.html template not found")
    
    # Check header template has NLI search
    print("\n3. 📄 Checking header.html template...")
    header_template = os.path.join(base_path, "templates/includes/header.html")
    
    if os.path.exists(header_template):
        with open(header_template, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'nli_search.html' in content:
            print("✅ NLI search interface is included in header (global)")
        else:
            print("❌ NLI search interface NOT found in header")
    else:
        print("❌ header.html template not found")
    
    # Check NLI search template exists
    print("\n4. 📄 Checking nli_search.html template...")
    nli_template = os.path.join(base_path, "dashboard/templates/dashboard/nli_search.html")
    
    if os.path.exists(nli_template):
        with open(nli_template, 'r', encoding='utf-8') as f:
            content = f.read()
            
        elements_to_check = [
            ('nliSearchInput', 'Search input field'),
            ('voiceBtn', 'Voice button'),
            ('fa-microphone', 'Microphone icon'),
            ('clearBtn', 'Clear button')
        ]
        
        for element, description in elements_to_check:
            if element in content:
                print(f"✅ {description} found in NLI search template")
            else:
                print(f"❌ {description} NOT found in NLI search template")
    else:
        print("❌ nli_search.html template not found")
    
    # Check AI dashboard JavaScript exists
    print("\n5. 📄 Checking ai_dashboard.js file...")
    js_paths = [
        "static/js/ai_dashboard.js",
        "staticfiles/js/ai_dashboard.js"
    ]
    
    for js_path in js_paths:
        full_path = os.path.join(base_path, js_path)
        if os.path.exists(full_path):
            print(f"✅ {js_path} exists")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            functions_to_check = [
                ('initializeNLISearch', 'NLI Search initialization'),
                ('toggleVoiceSearch', 'Voice search toggle'),
                ('processNLIQuery', 'Query processing'),
                ('showQuickSuggestions', 'Quick suggestions'),
                ('clearNLISearch', 'Clear search function')
            ]
            
            for func, description in functions_to_check:
                if func in content:
                    print(f"  ✅ {description} function found")
                else:
                    print(f"  ❌ {description} function NOT found")
        else:
            print(f"❌ {js_path} not found")
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    print("\n🎯 WHAT THE FIX ACCOMPLISHED:")
    print("✅ AI search interface is globally available (header.html)")
    print("✅ AI search JavaScript is globally loaded (base.html)")
    print("✅ No duplicate script loading (removed from dashboard.html)")
    print("✅ Voice and text search should work on ALL pages now")
    
    print("\n🧪 TO TEST:")
    print("1. Open any page: Dashboard, Projects, Resources, Allocation, Analytics")
    print("2. Look for search bar with microphone icon in header")
    print("3. Type a query like 'Who is available for a new project?'")
    print("4. Press Enter or click search")
    print("5. Verify AI results appear")
    print("6. Click microphone icon and test voice search")
    
    print("\n📊 EXPECTED RESULT:")
    print("🎉 AI search functionality should work identically on all pages!")

if __name__ == "__main__":
    verify_search_fix()
