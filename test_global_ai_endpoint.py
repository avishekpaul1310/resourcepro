#!/usr/bin/env python3
"""
Test the new global AI search endpoint
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_global_ai_endpoint():
    """Test the new global AI search endpoint"""
    client = Client()
    
    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Found admin user: {admin_user.username}")
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        return
    
    # Login
    client.force_login(admin_user)
    print("✅ Login successful")
    
    # Test the new global endpoint
    print("\n🔍 Testing new global AI search endpoint /api/ai-search/:")
    
    test_queries = [
        "list all projects",
        "show available resources",
        "what tasks need assignment"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing query: '{query}'")
        try:
            response = client.post('/api/ai-search/', 
                                 {'query': query},
                                 content_type='application/json',
                                 HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                response_obj = data.get('response', {})
                
                has_text = 'text' in response_obj
                has_data = 'data' in response_obj
                has_type = 'type' in response_obj
                
                print(f"  ✅ Structure: text={has_text}, data={has_data}, type={has_type}")
                
                if has_text and response_obj['text']:
                    text_preview = response_obj['text'][:60] + "..." if len(response_obj['text']) > 60 else response_obj['text']
                    print(f"  📄 Preview: {text_preview}")
                    
            else:
                print(f"  ❌ Error: {response.status_code}")
                print(f"  Content: {response.content.decode()[:200]}...")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    print("\n🎉 Global AI endpoint test complete!")

if __name__ == "__main__":
    test_global_ai_endpoint()
