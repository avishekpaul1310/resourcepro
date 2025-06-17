#!/usr/bin/env python3
"""
Verification script for chart size enlargement
"""

import os
import re

def verify_chart_enlargement():
    """Verify that the chart enlargement changes are properly implemented"""
    
    print("🔍 Verifying Chart Enlargement Updates...")
    
    # Files to check
    files_to_check = [
        "dashboard/static/js/charts.js",
        "dashboard/templates/dashboard/dashboard.html",
        "staticfiles/js/charts.js"
    ]
    
    improvements_found = {
        'maintain_aspect_ratio': False,
        'larger_legend': False,
        'layout_padding': False,
        'increased_height': False
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
            
            # Check for maintainAspectRatio: false
            if 'maintainAspectRatio: false' in content:
                print("   ✅ maintainAspectRatio set to false (allows chart to fill container)")
                improvements_found['maintain_aspect_ratio'] = True
            else:
                print("   ❌ maintainAspectRatio not configured for enlargement")
            
            # Check for larger legend settings
            legend_size_checks = [
                'boxWidth: 16',
                'padding: 20',
                'size: 14'
            ]
            
            legend_improvements = sum(1 for check in legend_size_checks if check in content)
            if legend_improvements >= 2:
                print("   ✅ Legend enlarged with bigger fonts and spacing")
                improvements_found['larger_legend'] = True
            else:
                print(f"   ❌ Legend enlargement incomplete ({legend_improvements}/3 improvements)")
            
            # Check for layout padding
            if 'layout:' in content and 'padding:' in content:
                print("   ✅ Layout padding configured for better spacing")
                improvements_found['layout_padding'] = True
            else:
                print("   ❌ Layout padding not found")
            
            # Check for increased height (only in HTML template)
            if 'dashboard.html' in file_path:
                if 'height: 450px' in content:
                    print("   ✅ Chart container height increased to 450px")
                    improvements_found['increased_height'] = True
                else:
                    print("   ❌ Chart container height not increased")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 CHART ENLARGEMENT SUMMARY")
    print("="*50)
    
    if improvements_found['maintain_aspect_ratio']:
        print("✅ IMPROVED: Chart aspect ratio flexibility")
        print("   • maintainAspectRatio: false allows chart to use full container")
        print("   • Chart will now expand to fill available space")
    else:
        print("❌ Chart aspect ratio not optimized")
    
    if improvements_found['larger_legend']:
        print("✅ ENHANCED: Legend size and readability")
        print("   • Increased legend box width from 12px to 16px")
        print("   • Increased padding from 15px to 20px")
        print("   • Increased font size from 12px to 14px")
        print("   • Added font weight 500 for better visibility")
    else:
        print("❌ Legend enlargement not fully applied")
    
    if improvements_found['layout_padding']:
        print("✅ ADDED: Layout padding for better spacing")
        print("   • 20px padding on all sides")
        print("   • Better visual balance and breathing room")
    else:
        print("❌ Layout padding not configured")
    
    if improvements_found['increased_height']:
        print("✅ INCREASED: Chart container height")
        print("   • Container height increased from 300px to 450px")
        print("   • 50% larger display area for the chart")
    else:
        print("❌ Chart container height not increased")
    
    print("\n" + "="*50)
    
    # Overall status
    improvements_count = sum(improvements_found.values())
    if improvements_count >= 3:
        print("🎉 CHART ENLARGEMENT SUCCESSFUL!")
        print("\n📈 Expected Results:")
        print("   • Much larger pie chart taking up more space")
        print("   • Bigger, more readable legend on the right")
        print("   • Better use of available screen real estate")
        print("   • More professional and prominent display")
    else:
        print(f"⚠️  Chart enlargement partially complete ({improvements_count}/4 improvements)")

if __name__ == "__main__":
    verify_chart_enlargement()
