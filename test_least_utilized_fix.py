#!/usr/bin/env python
"""
Test the specific "least utilized" query that was having issues
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

def test_least_utilized_query():
    """Test the specific query that was failing"""
    nli_service = NaturalLanguageInterfaceService()
    
    print("🔍 Testing 'Least Utilized' Query Fix")
    print("=" * 50)
    
    # Test the exact query from the screenshot
    test_queries = [
        "who is the least utilized rest",  # Exact query from screenshot
        "who is the least utilized resource",  # Complete version
        "show me the least utilized employee",
        "who has the lowest utilization",
        "which resource is underutilized",
        "who is not busy"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 40)
        
        try:
            result = nli_service.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            response = result.get('response', {})
            text = response.get('text', 'No response')
            data_type = response.get('type', 'unknown')
            data_count = len(response.get('data', []))
            
            print(f"✅ Response type: {data_type}")
            print(f"📊 Data items: {data_count}")
            print(f"💬 Response:")
            print(f"   {text}")
            
            # Check if it's giving the expected response for least utilized queries
            if any(word in text.lower() for word in ["least", "lowest", "underutilized"]):
                print("✅ Correctly identified as least utilized query!")
            elif data_type == "help":
                print("⚠️  Still showing help message - intent not detected")
            else:
                print("✅ Providing relevant resource information")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Least Utilized Query Testing Complete!")

if __name__ == "__main__":
    test_least_utilized_query()
