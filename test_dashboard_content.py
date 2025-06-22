#!/usr/bin/env python
"""
Direct test of the dashboard view to see the actual HTML content
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_dashboard_content():
    """Test the actual dashboard HTML content"""
    print("🧪 Testing Dashboard HTML Content")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Get or create a test user
    user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'testpass'})
    if created:
        user.set_password('testpass')
        user.save()
    
    # Login
    client.force_login(user)
    
    # Get the dashboard response
    response = client.get('/dashboard/')
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for AI features
        print("\n🔍 Checking HTML content:")
        
        if 'ai-analyst-widget' in content:
            print("✅ Found AI analyst widget")
        else:
            print("❌ No AI analyst widget found")
            
        if 'btn-recommendations' in content:
            print("✅ Found recommendation button")
        else:
            print("❌ No recommendation button found")
            if 'btn-simulate' in content:
                print("⚠️ Found old simulate button instead")
            
        if 'ai_dashboard.js' in content:
            print("✅ Found AI dashboard JavaScript")
        else:
            print("❌ No AI dashboard JavaScript found")
            
        # Check for specific AI content
        ai_section_start = content.find('ai-analyst-widget')
        if ai_section_start != -1:
            ai_section_end = content.find('</div>', ai_section_start + 500)
            if ai_section_end != -1:
                ai_section = content[ai_section_start:ai_section_end + 6]
                print(f"\n📄 AI Widget Content Sample:")
                print(ai_section[:500] + "..." if len(ai_section) > 500 else ai_section)
        
        # Check for risk items
        if 'ai-risk-item' in content:
            print("✅ Found AI risk items")
            
            # Count recommendation buttons
            rec_button_count = content.count('btn-recommendations')
            old_button_count = content.count('btn-simulate')
            
            print(f"   Recommendation buttons: {rec_button_count}")
            print(f"   Old simulate buttons: {old_button_count}")
        else:
            print("❌ No AI risk items found")
            
    else:
        print(f"❌ Dashboard request failed with status {response.status_code}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_dashboard_content()
