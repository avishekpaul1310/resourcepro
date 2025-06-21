#!/usr/bin/env python
"""
Test script for Enhanced Modern UI in ResourcePro
Tests the new modern styling for AI features and remove buttons
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from projects.models import Task
from allocation.models import Assignment
from resources.models import Resource
import json

def test_modern_ui_features():
    """Test the enhanced modern UI features"""
    print("🎨 Testing Enhanced Modern UI Features")
    print("=" * 50)
    
    # Get test data
    client = Client()
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No admin user found")
        return
    
    client.force_login(user)
    print(f"✅ Logged in as {user.username}")
    
    # Test UI components
    print("\n🖥️  Testing Enhanced UI Components...")
    response = client.get('/allocation/')
    print(f"   Allocation board: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for enhanced UI elements
        ui_checks = [
            ('Main AI button with enhanced styling', 'ai-suggestions-main-btn' in content),
            ('AI icon span', 'ai-icon' in content),
            ('AI text span', 'ai-text' in content),
            ('AI badge (SMART)', 'ai-badge' in content),
            ('Robot emoji in button', '🤖' in content),
            ('Enhanced remove button', 'fa-trash-alt' in content),
            ('Modern CSS classes', 'assignment-remove' in content),
            ('Enhanced task cards', 'task-card' in content),
            ('Modern assignment cards', 'assignment-card' in content),
        ]
        
        for check_name, check_result in ui_checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
    
    # Check data for visual testing
    print(f"\n📊 Data Status:")
    unassigned_count = Task.objects.filter(assignments__isnull=True).count()
    assigned_count = Assignment.objects.count()
    resources_count = Resource.objects.count()
    
    print(f"   📋 Unassigned tasks: {unassigned_count}")
    print(f"   ✅ Assigned tasks: {assigned_count}")
    print(f"   👥 Resources: {resources_count}")
    
    if unassigned_count > 0:
        print(f"   ✨ Perfect! You have unassigned tasks to see the enhanced AI buttons")
    if assigned_count > 0:
        print(f"   🗑️  Great! You have assignments to test the modern remove buttons")
    
    print("\n🎉 Enhanced Modern UI Test Complete!")
    print("\n🎨 New Modern Features:")
    print("  🤖 Main AI button with gradient, animations, and SMART badge")
    print("  🔥 Individual task AI buttons with robot emoji and hover effects")
    print("  🗑️  Modern trash can remove buttons with smooth animations")
    print("  ✨ Floating animations and gradient backgrounds")
    print("  🎯 Enhanced task and assignment cards with hover effects")
    print("  📱 Responsive design for mobile devices")
    print("  🌟 Professional color schemes and typography")
    print("  ⚡ Smooth transitions and micro-interactions")

if __name__ == '__main__':
    test_modern_ui_features()
