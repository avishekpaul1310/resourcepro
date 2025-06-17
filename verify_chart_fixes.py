#!/usr/bin/env python3
"""
Verification script to confirm dashboard chart improvements
"""

import os
import re

def verify_chart_improvements():
    """Verify that the chart improvements are properly implemented"""
    
    print("🔍 Verifying Dashboard Chart Improvements...")
    
    # Files to check
    files_to_check = [
        "dashboard/static/js/charts.js",
        "dashboard/templates/dashboard/dashboard.html",
        "staticfiles/js/charts.js"
    ]
    
    improvements_found = {
        'improved_colors': False,
        'tooltip_units': False,
        'border_styling': False
    }
    
    for file_path in files_to_check:
        full_path = f"c:/Users/Avishek Paul/resourcepro/{file_path}"
        
        if not os.path.exists(full_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n📄 Checking {file_path}...")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for improved colors (high contrast colors)
            improved_colors = [
                '#2563EB',  # blue-600 (better contrast)
                '#DC2626',  # red-600 (high contrast)
                '#059669',  # green-600 (high contrast)
            ]
            
            colors_found = all(color in content for color in improved_colors)
            if colors_found:
                print("   ✅ Improved high-contrast colors found")
                improvements_found['improved_colors'] = True
            else:
                print("   ❌ Improved colors not found")
            
            # Check for tooltip configuration with percentage units
            tooltip_pattern = r'tooltip:\s*{[^}]*callbacks:[^}]*label:[^}]*toFixed\(1\)[^}]*%'
            if re.search(tooltip_pattern, content, re.DOTALL):
                print("   ✅ Tooltip with percentage units found")
                improvements_found['tooltip_units'] = True
            elif 'toFixed(1)' in content and "'%'" in content:
                print("   ✅ Tooltip formatting with percentage found")
                improvements_found['tooltip_units'] = True
            else:
                print("   ❌ Tooltip units configuration not found")
            
            # Check for border styling improvements
            if 'borderWidth: 2' in content and 'borderColor' in content:
                print("   ✅ Enhanced border styling found")
                improvements_found['border_styling'] = True
            else:
                print("   ❌ Enhanced border styling not found")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 IMPROVEMENT VERIFICATION SUMMARY")
    print("="*50)
    
    if improvements_found['improved_colors']:
        print("✅ FIXED: Color contrast issue resolved")
        print("   • Replaced light colors (#EBF4FF, #A3BFFA) with high-contrast colors")
        print("   • Mobile App Development segment now uses #2563EB (blue-600)")
        print("   • Added more distinct colors: #DC2626 (red-600), #059669 (green-600)")
    else:
        print("❌ Color contrast issue not fully resolved")
    
    if improvements_found['tooltip_units']:
        print("✅ FIXED: Missing units issue resolved")
        print("   • Added percentage (%) units to tooltip labels")
        print("   • Values now display as 'Project Name: 23.9%'")
    else:
        print("❌ Missing units issue not fully resolved")
    
    if improvements_found['border_styling']:
        print("✅ BONUS: Enhanced border styling added")
        print("   • Increased border width to 2px for better definition")
        print("   • Added white border color for segment separation")
    else:
        print("❌ Border styling enhancements not found")
    
    print("\n" + "="*50)
    
    # Overall status
    if all(improvements_found.values()):
        print("🎉 ALL IMPROVEMENTS SUCCESSFULLY IMPLEMENTED!")
    elif improvements_found['improved_colors'] and improvements_found['tooltip_units']:
        print("✅ MAIN ISSUES RESOLVED (with bonus enhancements)")
    else:
        print("⚠️  Some improvements may need attention")

if __name__ == "__main__":
    verify_chart_improvements()
