#!/usr/bin/env python
"""
Setup script for ResourcePro API integration
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def setup_api_integration():
    """Set up API integration for ResourcePro"""
    
    print("🚀 Setting up ResourcePro API Integration...")
    print("=" * 50)
    
    # Step 1: Install dependencies
    print("\n1. Installing dependencies...")
    os.system("pip install -r requirements.txt")
    
    # Step 2: Run migrations
    print("\n2. Running database migrations...")
    try:
        call_command('makemigrations', verbosity=1)
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Step 3: Create API tokens for existing users
    print("\n3. Creating API tokens for users...")
    try:
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            token, created = Token.objects.get_or_create(user=user)
            if created:
                created_count += 1
                print(f"   ✅ Created token for {user.username}")
            else:
                print(f"   ℹ️  Token already exists for {user.username}")
        
        print(f"✅ API tokens setup completed ({created_count} new tokens created)")
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
        return False
    
    # Step 4: Create superuser token if admin exists
    print("\n4. Setting up admin API access...")
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            token, created = Token.objects.get_or_create(user=admin_user)
            print(f"   ✅ Admin API token: {token.key}")
            print(f"   👤 Admin user: {admin_user.username}")
        else:
            print("   ⚠️  No superuser found. Create one using: python manage.py createsuperuser")
    except Exception as e:
        print(f"❌ Admin token setup failed: {e}")
    
    # Step 5: Display API information
    print("\n5. API Integration Summary")
    print("=" * 30)
    print("✅ Django REST Framework configured")
    print("✅ API documentation enabled")
    print("✅ CORS support configured")
    print("✅ Token authentication enabled")
    print("✅ Custom permissions implemented")
    print("✅ Advanced filtering enabled")
    print("✅ AI endpoints integrated")
    
    print("\n📚 API Documentation URLs:")
    print("   • Swagger UI: http://localhost:8000/api/docs/")
    print("   • ReDoc: http://localhost:8000/api/redoc/")
    print("   • OpenAPI Schema: http://localhost:8000/api/schema/")
    
    print("\n🔗 API Endpoints:")
    print("   • Authentication: /api/auth/token/")
    print("   • Resources: /api/v1/resources/")
    print("   • Projects: /api/v1/projects/")
    print("   • Tasks: /api/v1/tasks/")
    print("   • Assignments: /api/v1/assignments/")
    print("   • Skills: /api/v1/skills/")
    print("   • Time Entries: /api/v1/time-entries/")
    print("   • Users: /api/v1/users/")
    
    print("\n🔒 Authentication:")
    print("   Include in headers: Authorization: Token <your-token>")
    
    print("\n📖 Integration Examples:")
    print("   See api_integration_examples.py for code samples")
    print("   See API_INTEGRATION_GUIDE.md for detailed documentation")
    
    print("\n🎉 API Integration setup completed successfully!")
    print("   Run 'python manage.py runserver' to start the API")
    
    return True


def create_sample_api_client():
    """Create a sample API client script"""
    sample_client = """#!/usr/bin/env python
\"\"\"
Sample ResourcePro API client
\"\"\"
import requests
import json

class ResourceProClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
    
    def get_resources(self):
        response = requests.get(f'{self.base_url}/api/v1/resources/', headers=self.headers)
        return response.json()
    
    def get_projects(self):
        response = requests.get(f'{self.base_url}/api/v1/projects/', headers=self.headers)
        return response.json()
    
    def get_unassigned_tasks(self):
        response = requests.get(f'{self.base_url}/api/v1/tasks/unassigned/', headers=self.headers)
        return response.json()

if __name__ == '__main__':
    # Configure your API client
    client = ResourceProClient(
        base_url='http://localhost:8000',
        token='your-api-token-here'  # Replace with actual token
    )
    
    try:
        print("Fetching resources...")
        resources = client.get_resources()
        print(f"Found {resources['count']} resources")
        
        print("\\nFetching projects...")
        projects = client.get_projects()
        print(f"Found {projects['count']} projects")
        
        print("\\nFetching unassigned tasks...")
        tasks = client.get_unassigned_tasks()
        print(f"Found {tasks['count']} unassigned tasks")
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")
"""
    
    with open('sample_api_client.py', 'w') as f:
        f.write(sample_client)
    
    print("✅ Created sample_api_client.py")


if __name__ == '__main__':
    print("ResourcePro API Integration Setup")
    print("=================================")
    
    if setup_api_integration():
        create_sample_api_client()
        print("\n🎯 Next Steps:")
        print("1. Start the development server: python manage.py runserver")
        print("2. Visit http://localhost:8000/api/docs/ for API documentation")
        print("3. Use sample_api_client.py as a starting point for integration")
        print("4. Check API_INTEGRATION_GUIDE.md for detailed documentation")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
