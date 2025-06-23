#!/usr/bin/env python
"""
Final test for the original query that was failing
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

def test_original_query():
    """Test the exact original query that was failing"""
    print("🎯 TESTING ORIGINAL FAILING QUERY")
    print("=" * 60)
    
    nli_service = NaturalLanguageInterfaceService()
    
    # The exact query that was failing
    original_query = "could you please list all the project names"
    
    print(f"🔍 Testing: '{original_query}'")
    print("-" * 50)
    
    result = nli_service.process_query(original_query)
    
    if "error" in result:
        print(f"❌ Still failing: {result['error']}")
        return False
    
    response = result.get('response', {})
    text = response.get('text', '')
    data = response.get('data', [])
    response_type = response.get('type', 'unknown')
    
    print(f"✅ SUCCESS!")
    print(f"📊 Response Type: {response_type}")
    print(f"📝 Text Length: {len(text)} characters")
    print(f"📋 Data Items: {len(data)}")
    print(f"💬 Full Response:")
    print(text)
    
    if data:
        print(f"\n📊 Data Array: {data}")
    
    # Verify it contains project names
    expected_projects = ["test project", "API Integration", "Website Redesign"]
    found_projects = [name for name in expected_projects if name in text]
    
    print(f"\n🔍 Verification:")
    print(f"   Expected some of: {expected_projects}")
    print(f"   Found in response: {found_projects}")
    
    if len(found_projects) > 0:
        print("✅ Query is working correctly - project names are being returned!")
        return True
    else:
        print("❌ Query response doesn't contain expected project names")
        return False

if __name__ == "__main__":
    success = test_original_query()
    if success:
        print("\n🎉 ISSUE FIXED! The AI search now responds to project listing queries.")
    else:
        print("\n⚠️ Issue may still need more work.")
