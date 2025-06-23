#!/usr/bin/env python
"""
Test script to debug why specific queries don't return responses
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

def test_specific_query():
    """Test the specific query that's not working"""
    print("🔍 DEBUGGING SPECIFIC QUERY")
    print("=" * 60)
    
    nli_service = NaturalLanguageInterfaceService()
    
    # Test the problematic query
    test_queries = [
        "could you please list all the project names",
        "list all project names",
        "show me all projects",
        "what projects do we have",
        "list projects",
        "show projects",
        "project names",
        "all projects"
    ]
    
    for query in test_queries:
        print(f"\n🧪 Testing Query: '{query}'")
        print("-" * 40)
        
        try:
            # Analyze intent first
            intent_data = nli_service._analyze_query_intent(query)
            print(f"📋 Intent Analysis:")
            print(f"   Intent: {intent_data.get('intent', 'unknown')}")
            print(f"   Entities: {intent_data.get('entities', {})}")
            
            # Check if it's complex
            is_complex = nli_service._is_complex_query(query, intent_data)
            print(f"🤔 Is Complex Query: {is_complex}")
            
            # Process the full query
            result = nli_service.process_query(query)
            print(f"📊 Result:")
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                response = result.get('response', {})
                text = response.get('text', 'No response text')
                data_type = response.get('type', 'unknown')
                data_count = len(response.get('data', []))
                
                print(f"   ✅ Success: {len(text)} chars")
                print(f"   📝 Response Type: {data_type}")
                print(f"   📊 Data Items: {data_count}")
                print(f"   💬 Text: {text[:200]}{'...' if len(text) > 200 else ''}")
                
                if data_count > 0:
                    print(f"   📋 Sample Data: {response.get('data', [])[:2]}")
        
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🧪 DETAILED DEBUGGING")
    print("=" * 60)
    
    # Test the comprehensive context gathering
    try:
        print("\n📊 Testing Context Gathering...")
        context = nli_service._gather_comprehensive_context()
        
        print(f"✅ Context gathered successfully:")
        print(f"   Resources: {len(context.get('resources', []))}")
        print(f"   Projects: {len(context.get('projects', []))}")
        print(f"   Tasks: {len(context.get('tasks', []))}")
        
        # Show sample project data
        projects = context.get('projects', [])
        if projects:
            print(f"\n📋 Sample Project Data:")
            for i, project in enumerate(projects[:3]):
                print(f"   {i+1}. {project.get('name', 'Unknown')} (Status: {project.get('status', 'Unknown')})")
        else:
            print("   ⚠️  No project data found")
    
    except Exception as e:
        print(f"❌ Context gathering failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test AI query processing directly
    print("\n🤖 Testing AI Query Processing...")
    try:
        ai_response = nli_service._process_ai_query("list all project names")
        print(f"✅ AI Response: {ai_response}")
    except Exception as e:
        print(f"❌ AI Query failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_query()
