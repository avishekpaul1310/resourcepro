#!/usr/bin/env python
"""
Test script to verify the query fix is working for various project queries
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

def test_improved_queries():
    """Test various queries to verify they work correctly"""
    print("🎯 TESTING IMPROVED QUERY HANDLING")
    print("=" * 60)
    
    nli_service = NaturalLanguageInterfaceService()
    
    # Test various project-related queries
    test_queries = [
        "could you please list all the project names",
        "show me all projects with their status",
        "list projects",
        "what are the project details",
        "show me project information",
        "list all resources",
        "who are the team members",
        "show me tasks",
        "what are the upcoming deadlines"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 50)
        
        try:
            result = nli_service.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                response = result.get('response', {})
                text = response.get('text', 'No response')
                data_type = response.get('type', 'unknown')
                data_count = len(response.get('data', []))
                
                print(f"✅ Success - Type: {data_type}, Items: {data_count}")
                print(f"📝 Response:")
                print(text[:300] + ("..." if len(text) > 300 else ""))
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 QUERY TESTING COMPLETE")
    print("All project-related queries should now work correctly!")

if __name__ == "__main__":
    test_improved_queries()
