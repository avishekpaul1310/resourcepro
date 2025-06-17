#!/usr/bin/env python3
"""
Test script to verify dashboard chart improvements
"""

import requests
from bs4 import BeautifulSoup
import re

def test_dashboard_chart_improvements():
    """Test that the dashboard chart has improved colors and units"""
    
    print("🧪 Testing Dashboard Chart Improvements...")
    
    # Test URL
    url = "http://127.0.0.1:8000/dashboard/"
    
    try:
        # Make request to dashboard
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if the page loaded successfully
        title = soup.find('title')
        if title and 'Dashboard' in title.text:
            print("✅ Dashboard page loaded successfully")
        else:
            print("❌ Dashboard page failed to load")
            return False
        
        # Check for Chart.js script
        scripts = soup.find_all('script')
        chart_script_found = False
        improved_colors_found = False
        tooltip_config_found = False
        
        for script in scripts:
            if script.string:
                # Check for improved color palette
                if '#2563EB' in script.string and '#DC2626' in script.string and '#059669' in script.string:
                    improved_colors_found = True
                    print("✅ Improved color palette found in chart configuration")
                
                # Check for tooltip configuration with units
                if 'tooltip:' in script.string and 'toFixed(1)' in script.string and "'%'" in script.string:
                    tooltip_config_found = True
                    print("✅ Tooltip configuration with percentage units found")
                
                # Check for Chart.js usage
                if 'new Chart(' in script.string and 'doughnut' in script.string:
                    chart_script_found = True
                    print("✅ Chart.js doughnut chart configuration found")
        
        # Check for Chart.js CDN
        chart_cdn_found = False
        for script in soup.find_all('script', src=True):
            if 'chart.js' in script['src'].lower():
                chart_cdn_found = True
                print("✅ Chart.js CDN found")
                break
        
        # Summary of findings
        print("\n📊 Chart Improvement Summary:")
        print(f"   • Dashboard loaded: {'✅' if title else '❌'}")
        print(f"   • Chart.js CDN: {'✅' if chart_cdn_found else '❌'}")
        print(f"   • Chart configuration: {'✅' if chart_script_found else '❌'}")
        print(f"   • Improved colors: {'✅' if improved_colors_found else '❌'}")
        print(f"   • Tooltip with units: {'✅' if tooltip_config_found else '❌'}")
        
        # Overall result
        if all([chart_script_found, improved_colors_found, tooltip_config_found]):
            print("\n🎉 All chart improvements successfully implemented!")
            return True
        else:
            print("\n⚠️  Some improvements may not be fully applied")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server. Make sure it's running on http://127.0.0.1:8000/")
        return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    test_dashboard_chart_improvements()
