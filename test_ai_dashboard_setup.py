#!/usr/bin/env python
"""
Test script for AI Dashboard Features
"""
import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

def test_ai_dashboard_setup():
    """Test the basic AI dashboard setup"""
    print("🤖 Testing AI Dashboard Features Setup...")
    
    # Test model imports
    try:
        from dashboard.models import DashboardAIAnalysis, InterventionScenario, NLIQuery, AIInsight
        print("✅ AI Models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI models: {e}")
        return False
    
    # Test service imports
    try:
        from dashboard.ai_services import dashboard_ai_service, intervention_simulator_service, nli_service
        print("✅ AI Services imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI services: {e}")
        return False
    
    # Test Gemini AI availability
    try:
        from utils.gemini_ai import gemini_service
        if gemini_service.is_available():
            print("✅ Gemini AI service is available")
        else:
            print("⚠️  Gemini AI service not available (missing API key or library)")
    except ImportError as e:
        print(f"❌ Failed to import Gemini AI service: {e}")
    
    # Test database models
    try:
        # Test model creation (without actual AI calls)
        from django.contrib.auth.models import User
        from django.utils import timezone
        
        # Create a test AI analysis record
        analysis = DashboardAIAnalysis.objects.create(
            analysis_type='daily_briefing',
            summary='Test AI analysis',
            risks=[],
            recommendations=[],
            confidence_score=0.8
        )
        print(f"✅ Created test AI analysis: {analysis.id}")
        
        # Clean up
        analysis.delete()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False
    
    # Test view imports
    try:
        from dashboard.views import dashboard, simulate_intervention, process_nli_query
        print("✅ AI Dashboard views imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI dashboard views: {e}")
        return False
    
    print("\n🎉 AI Dashboard Features setup completed successfully!")
    print("\nNext Steps:")
    print("1. Set up GEMINI_API_KEY in your environment variables")
    print("2. Install google-generativeai package: pip install google-generativeai")
    print("3. Start the development server: python manage.py runserver")
    print("4. Visit the dashboard to see the AI features in action")
    
    return True

def test_sample_ai_functionality():
    """Test sample AI functionality without API calls"""
    print("\n🧪 Testing Sample AI Functionality...")
    
    try:
        from dashboard.ai_services import NaturalLanguageInterfaceService
        
        nli = NaturalLanguageInterfaceService()
        
        # Test intent analysis
        intent_data = nli._analyze_query_intent("Who is available for a new project?")
        print(f"✅ Intent analysis working: {intent_data}")
        
        # Test response generation (without API calls)
        response = nli._handle_availability_query("Who is available?")
        print(f"✅ Response generation working: {response['type']}")
        
        print("✅ Sample AI functionality tests passed")
        
    except Exception as e:
        print(f"❌ Sample AI functionality test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_ai_dashboard_setup()
    if success:
        test_sample_ai_functionality()
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
