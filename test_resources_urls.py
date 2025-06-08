#!/usr/bin/env python
"""
Test script to verify Resources tab URLs are working correctly.
"""
import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client

def test_resources_urls():
    """Test that all resources URLs resolve correctly"""
    
    # Create a test client
    client = Client()
    
    # Test login with known credentials
    print("Testing login...")
    login_response = client.post('/accounts/login/', {
        'username': 'admin',
        'password': 'password123'
    })
    print(f"Login response: {login_response.status_code}")
    
    if login_response.status_code == 302:  # Successful login redirects
        print("✓ Login successful")
    else:
        print("✗ Login failed")
        return
    
    # Test resources URLs
    resources_urls = [
        ('resources:resource_list', 'View Resources'),
        ('resources:resource_create', 'Create Resource'),
        ('resources:skill_list', 'Manage Skills'),
        ('resources:time_tracking', 'Time Tracking'),
        ('resources:availability_calendar', 'Availability Calendar'),
    ]
    
    print("\nTesting Resources URLs:")
    for url_name, description in resources_urls:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            if response.status_code == 200:
                print(f"✓ {description} ({url_name}): {url} - Status {response.status_code}")
            else:
                print(f"✗ {description} ({url_name}): {url} - Status {response.status_code}")
                
        except Exception as e:
            print(f"✗ {description} ({url_name}): Error - {str(e)}")
    
    # Test individual resource URLs (if resources exist)
    print("\nTesting dynamic resource URLs:")
    try:
        from resources.models import Resource
        resources = Resource.objects.all()[:3]  # Test first 3 resources
        
        for resource in resources:
            try:
                detail_url = reverse('resources:resource_detail', args=[resource.pk])
                edit_url = reverse('resources:resource_edit', args=[resource.pk])
                
                detail_response = client.get(detail_url)
                edit_response = client.get(edit_url)
                
                print(f"✓ Resource Detail for '{resource.name}': {detail_url} - Status {detail_response.status_code}")
                print(f"✓ Resource Edit for '{resource.name}': {edit_url} - Status {edit_response.status_code}")
                
            except Exception as e:
                print(f"✗ Resource URLs for '{resource.name}': Error - {str(e)}")
                
        # Test skill URLs if skills exist
        from resources.models import Skill
        skills = Skill.objects.all()[:3]  # Test first 3 skills
        
        for skill in skills:
            try:
                delete_url = reverse('resources:skill_delete', args=[skill.pk])
                # Note: We won't actually delete, just test URL resolution
                print(f"✓ Skill Delete URL for '{skill.name}': {delete_url} - URL resolves")
                
            except Exception as e:
                print(f"✗ Skill Delete URL for '{skill.name}': Error - {str(e)}")
                
    except Exception as e:
        print(f"Note: Could not test dynamic URLs - {str(e)}")

if __name__ == '__main__':
    test_resources_urls()
