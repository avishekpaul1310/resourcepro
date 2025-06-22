#!/usr/bin/env python
"""
Test script to verify the current AI search functionality with concise responses
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.ai_services import NaturalLanguageInterfaceService

def test_ai_search_responses():
    """Test AI search with various queries to verify concise responses"""
    nli_service = NaturalLanguageInterfaceService()
    
    test_queries = [
        "Who is available for a new project?",
        "Show me overallocated resources",
        "What are the upcoming deadlines?",
        "Who is the most active resource?",
        "What skills do we have in the team?",
        "Help me understand what you can do"
    ]
    
    print("🔍 Testing AI Search Responses")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        print("-" * 40)
        
        try:
            result = nli_service.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            response = result.get('response', {})
            text = response.get('text', 'No text response')
            data_type = response.get('type', 'unknown')
            data_count = len(response.get('data', []))
            
            print(f"✅ Response type: {data_type}")
            print(f"📊 Data items: {data_count}")
            print(f"💬 Response text:")
            print(f"   {text}")
            
            # Check if response is concise (under 500 characters)
            if len(text) < 500:
                print(f"✅ Response is concise ({len(text)} characters)")
            else:
                print(f"⚠️  Response might be too long ({len(text)} characters)")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Search Testing Complete!")

if __name__ == "__main__":
    test_ai_search_responses()
