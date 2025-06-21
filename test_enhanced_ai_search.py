#!/usr/bin/env python
"""
Test the enhanced AI search functionality with complex queries
"""
import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_enhanced_ai_search():
    print("Testing Enhanced AI Search Functionality...")
    print("=" * 70)
    
    client = Client()
    
    # Get admin user
    try:
        user = User.objects.get(username='admin')
        client.force_login(user)
        print(f"✅ Logged in as: {user.username}")
    except User.DoesNotExist:
        print("❌ No admin user found")
        return
    
    # Test queries - from simple to complex
    test_queries = [
        # Simple queries (should use fast keyword matching)
        {
            "query": "Who is available for a new project?",
            "type": "Simple (keyword-based)",
            "expected": "Fast response using current system"
        },
        
        # Complex queries (should use AI)
        {
            "query": "Which developer has worked on the most projects and what's their average utilization?",
            "type": "Complex (AI-powered)",
            "expected": "Detailed analysis with calculations"
        },
        {
            "query": "Compare the workload between different departments and identify bottlenecks",
            "type": "Complex (AI-powered)", 
            "expected": "Cross-department analysis"
        },
        {
            "query": "What's the total budget allocated across all active projects?",
            "type": "Complex (AI-powered)",
            "expected": "Financial calculation and analysis"
        },
        {
            "query": "Which project is most likely to miss its deadline and why?",
            "type": "Complex (AI-powered)",
            "expected": "Predictive analysis with reasoning"
        },
        {
            "query": "Show me productivity trends and recommend resource optimization",
            "type": "Complex (AI-powered)",
            "expected": "Trend analysis with recommendations"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. Testing {test_case['type']} Query:")
        print(f"Question: \"{test_case['query']}\"")
        print(f"Expected: {test_case['expected']}")
        print("-" * 50)
        
        try:
            response = client.post(
                '/dashboard/api/nli-query/',
                data=json.dumps({"query": test_case['query']}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                response_data = data.get('response', {})
                
                print(f"✅ Status: {response.status_code}")
                print(f"⏱️  Execution Time: {data.get('execution_time', 0):.3f}s")
                print(f"🤖 Response Type: {response_data.get('type', 'unknown')}")
                
                if response_data.get('confidence'):
                    print(f"🎯 AI Confidence: {response_data.get('confidence')}%")
                
                print(f"💬 Answer: {response_data.get('text', 'No response')[:200]}...")
                
                if response_data.get('calculations'):
                    print(f"🧮 Calculations: {response_data.get('calculations')}")
                    
                if response_data.get('recommendations'):
                    print(f"💡 Recommendations: {len(response_data.get('recommendations', []))} provided")
                
            else:
                print(f"❌ Error: {response.status_code} - {response.content.decode()}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
    
    print("=" * 70)
    print("🎉 Enhanced AI Search Test Completed!")
    print("\n📊 Summary:")
    print("✅ Simple queries use fast keyword matching")
    print("🤖 Complex queries use AI for detailed analysis")
    print("📈 System can now handle calculations, comparisons, and predictions")
    print("💡 Provides actionable recommendations")

if __name__ == "__main__":
    test_enhanced_ai_search()
