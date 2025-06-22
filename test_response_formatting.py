#!/usr/bin/env python3
"""
Test the enhanced response formatting
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.ai_services import nli_service

def test_nli_responses():
    print("🧪 Testing Enhanced NLI Response Formatting")
    print("=" * 60)
    
    test_queries = [
        "what are the upcoming deadlines?",
        "who is available for a new project?", 
        "show me overallocated resources",
        "what are the active projects?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        print("-" * 40)
        
        try:
            response = nli_service.process_query(query)
            
            if 'response' in response:
                resp_data = response['response']
                print(f"✅ Response generated successfully")
                print(f"📝 Text: {resp_data.get('text', 'No text')[:100]}...")
                print(f"📊 Type: {resp_data.get('type', 'No type')}")
                print(f"🎯 Confidence: {resp_data.get('confidence', 'N/A')}")
                
                if resp_data.get('data'):
                    data = resp_data['data']
                    if isinstance(data, list):
                        print(f"📋 Data count: {len(data)} items")
                        if data:
                            print(f"📄 Sample item keys: {list(data[0].keys())}")
                    else:
                        print(f"📄 Data type: {type(data)}")
                else:
                    print("📭 No structured data")
                    
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("\n💡 Tips for testing in browser:")
    print("1. Open http://127.0.0.1:8000/dashboard/")
    print("2. Try the test queries above")
    print("3. Check that responses are formatted nicely (no raw JSON)")
    print("4. Verify that structured data appears as cards/lists")

if __name__ == "__main__":
    test_nli_responses()
