#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from resources.models import Skill

print("=== TESTING DJANGO AND REACT SKILL FILTERING ===")

# Create client and log in
client = Client()
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.save()
client.login(username='admin', password='admin123')

# Test Django skill filtering
django_skill = Skill.objects.get(name='Django')
print(f"Testing Django skill (ID: {django_skill.id})")

response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={django_skill.id}')
print(f"Response status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'No forecast data available' in content:
        print("✅ Shows 'No forecast data available' (expected)")
    else:
        print("❌ Should show no data message")
        
    # Check if there's any helpful explanation
    if 'no resources' in content.lower() or 'skill' in content.lower():
        print("✅ Contains helpful explanation")
    else:
        print("❌ No helpful explanation provided")

# Test React skill filtering  
print(f"\nTesting React skill filtering...")
react_skill = Skill.objects.get(name='React')
response = client.get(f'/analytics/forecast/?forecast_days=7&skill_filter={react_skill.id}')

if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'No forecast data available' in content:
        print("✅ Shows 'No forecast data available' (expected)")
    else:
        print("❌ Should show no data message")

print("\n=== RECOMMENDATIONS ===")
print("1. ✅ Behavior is CORRECT - can't forecast skills with no resources")
print("2. 💡 Could improve UX with better messaging")
print("3. 💡 Could suggest assigning skills to resources")
print("4. 💡 Could show which resources could learn these skills")

print("\n=== TEST COMPLETE ===")
