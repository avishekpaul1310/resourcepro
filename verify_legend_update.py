#!/usr/bin/env python3
"""
Verification script for legend positioning update
"""

import os
import re

def verify_legend_positioning():
    """Verify that the legend positioning is updated to right side"""
    
    print("🔍 Verifying Legend Positioning Update...")
    
    # Files to check
    files_to_check = [
        "dashboard/static/js/charts.js",
        "dashboard/templates/dashboard/dashboard.html",
        "staticfiles/js/charts.js"
    ]
    
    improvements_found = {
        'legend_right_position': False,
        'legend_styling': False,
        'maintained_tooltips': False
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
            
            # Check for right positioned legend
            if "position: 'right'" in content:
                print("   ✅ Legend positioned to the right")
                improvements_found['legend_right_position'] = True
            else:
                print("   ❌ Legend position not updated to right")
            
            # Check for enhanced legend styling
            legend_styling_checks = [
                'boxWidth: 12',
                'padding: 15', 
                'usePointStyle: true',
                'align: \'center\''
            ]
            
            styling_found = sum(1 for check in legend_styling_checks if check in content)
            if styling_found >= 3:
                print("   ✅ Enhanced legend styling found")
                improvements_found['legend_styling'] = True
            else:
                print(f"   ❌ Legend styling incomplete ({styling_found}/4 features)")
            
            # Check that tooltips are still maintained
            if 'tooltip:' in content and 'toFixed(1)' in content and "'%'" in content:
                print("   ✅ Tooltip functionality maintained")
                improvements_found['maintained_tooltips'] = True
            else:
                print("   ❌ Tooltip functionality may be broken")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 LEGEND POSITIONING UPDATE SUMMARY")
    print("="*50)
    
    if improvements_found['legend_right_position']:
        print("✅ UPDATED: Legend moved to right side")
        print("   • Better utilization of horizontal space")
        print("   • More balanced chart layout")
    else:
        print("❌ Legend positioning update not found")
    
    if improvements_found['legend_styling']:
        print("✅ ENHANCED: Legend styling improved")
        print("   • Smaller, more compact legend boxes")
        print("   • Better spacing with proper padding")
        print("   • Point-style indicators for better appearance")
    else:
        print("❌ Legend styling enhancements not found")
    
    if improvements_found['maintained_tooltips']:
        print("✅ MAINTAINED: Tooltip functionality preserved")
        print("   • Percentage units still working")
        print("   • Previous improvements intact")
    else:
        print("❌ Tooltip functionality may be compromised")
    
    print("\n" + "="*50)
    
    # Overall status
    if all(improvements_found.values()):
        print("🎉 LEGEND POSITIONING UPDATE SUCCESSFUL!")
        print("\n📈 Expected Result:")
        print("   • Legend now appears on the right side of the chart")
        print("   • Better use of available horizontal space")
        print("   • More balanced and professional layout")
        print("   • All previous improvements maintained")
    else:
        print("⚠️  Some updates may need attention")

if __name__ == "__main__":
    verify_legend_positioning()
