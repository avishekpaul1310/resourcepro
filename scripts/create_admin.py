#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User

# Create admin user if doesn't exist
username = 'admin'
password = 'admin123'
email = 'admin@example.com'

try:
    user = User.objects.get(username=username)
    print(f"User '{username}' already exists")
except User.DoesNotExist:
    user = User.objects.create_superuser(username=username, password=password, email=email)
    print(f"Created superuser '{username}' with password '{password}'")

print(f"You can login with:")
print(f"Username: {username}")
print(f"Password: {password}")
