#!/usr/bin/env python3
"""
Test script to verify the skill demand analysis page works correctly.
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_skill_analysis_page():
    """Test the skill demand analysis page"""
    client = Client()
    
    # Get or create admin user
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print("Created admin user")
    
    # Login
    login_success = client.login(username='admin', password='admin')
    if not login_success:
        # Try with a known password
        admin_user.set_password('admin123')
        admin_user.save()
        login_success = client.login(username='admin', password='admin123')
    
    print(f"Login successful: {login_success}")
    
    if login_success:
        # Test the skill analysis page
        response = client.get('/analytics/skills/')
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Skill demand analysis page loads successfully!")
            
            # Check if context data is being passed
            context = response.context
            if context:
                print(f"Context variables: {list(context.keys())}")
                print(f"Skill demand count: {len(context.get('skill_demand', []))}")
                print(f"Total skills: {context.get('total_skills', 0)}")
                print(f"High demand skills: {context.get('high_demand_skills', 0)}")
            else:
                print("❌ No context data found")
        else:
            print(f"❌ Page failed to load with status {response.status_code}")
            if hasattr(response, 'content'):
                print("Response content preview:", response.content[:500])
    else:
        print("❌ Login failed")

if __name__ == "__main__":
    test_skill_analysis_page()
