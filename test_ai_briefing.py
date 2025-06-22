#!/usr/bin/env python
"""
Test the AI briefing functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from dashboard.ai_services import dashboard_ai_service

def test_ai_briefing():
    """Test AI briefing generation"""
    print("🧪 Testing AI Briefing Generation")
    print("=" * 50)
    
    try:
        # Generate briefing with force refresh
        result = dashboard_ai_service.generate_daily_briefing(force_refresh=True)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print("✅ AI Briefing Generated Successfully!")
        print(f"\n📊 Summary: {result.get('summary', 'No summary')}")
        
        risks = result.get('risks', [])
        print(f"\n🚨 Risks Found: {len(risks)}")
        for i, risk in enumerate(risks[:3], 1):  # Show first 3 risks
            print(f"   {i}. {risk.get('title', 'Unknown Risk')} ({risk.get('priority', 'medium')} priority)")
        
        recommendations = result.get('recommendations', [])
        print(f"\n💡 Recommendations: {len(recommendations)}")
        for i, rec in enumerate(recommendations[:3], 1):  # Show first 3 recommendations
            print(f"   {i}. {rec.get('title', 'Unknown Recommendation')}")
        
        comprehensive_risks = result.get('comprehensive_risks', [])
        print(f"\n🔍 Comprehensive Risk Analysis: {len(comprehensive_risks)} risks detected")
        
        risk_categories = result.get('risk_categories', {})
        print(f"📂 Risk Categories: {', '.join(risk_categories.keys())}")
        
        print(f"\n🎯 Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"🕒 Generated At: {result.get('created_at')}")
        print(f"🔄 Is Fresh: {result.get('is_fresh', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ai_briefing()
    if success:
        print("\n🎉 AI Briefing test completed successfully!")
    else:
        print("\n💥 AI Briefing test failed!")
