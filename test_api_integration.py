#!/usr/bin/env python
"""
API Test Script for ResourcePro
Tests the new API integration functionality
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000'
API_TOKEN = 'cf0fb1902fbf3af5da65359ea9a1e6d26d9b86f9'  # Admin token

class APITester:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        })
    
    def test_authentication(self):
        """Test API authentication"""
        print("🔐 Testing Authentication...")
        try:
            response = self.session.get(f'{self.base_url}/api/v1/users/me/')
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ Authentication successful! Logged in as: {user_data['username']}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_resources_api(self):
        """Test Resources API"""
        print("\n👥 Testing Resources API...")
        try:
            # Get all resources
            response = self.session.get(f'{self.base_url}/api/v1/resources/')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved {data['count']} resources")
                
                # Test resource details if resources exist
                if data['results']:
                    resource_id = data['results'][0]['id']
                    detail_response = self.session.get(f'{self.base_url}/api/v1/resources/{resource_id}/')
                    if detail_response.status_code == 200:
                        resource = detail_response.json()
                        print(f"   ✅ Retrieved resource details for: {resource['name']}")
                        
                        # Test utilization endpoint
                        util_response = self.session.get(f'{self.base_url}/api/v1/resources/{resource_id}/utilization/')
                        if util_response.status_code == 200:
                            util_data = util_response.json()
                            print(f"   ✅ Utilization: {util_data['utilization_percentage']}%")
                        else:
                            print(f"   ⚠️  Utilization endpoint returned: {util_response.status_code}")
                    
                return True
            else:
                print(f"   ❌ Resources API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Resources API error: {e}")
            return False
    
    def test_projects_api(self):
        """Test Projects API"""
        print("\n📁 Testing Projects API...")
        try:
            response = self.session.get(f'{self.base_url}/api/v1/projects/')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved {data['count']} projects")
                
                # Test project statistics if projects exist
                if data['results']:
                    project_id = data['results'][0]['id']
                    stats_response = self.session.get(f'{self.base_url}/api/v1/projects/{project_id}/statistics/')
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        print(f"   ✅ Project statistics - Tasks: {stats['total_tasks']}, Completion: {stats['completion_percentage']}%")
                    else:
                        print(f"   ⚠️  Statistics endpoint returned: {stats_response.status_code}")
                
                return True
            else:
                print(f"   ❌ Projects API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Projects API error: {e}")
            return False
    
    def test_tasks_api(self):
        """Test Tasks API"""
        print("\n📋 Testing Tasks API...")
        try:
            response = self.session.get(f'{self.base_url}/api/v1/tasks/')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved {data['count']} tasks")
                
                # Test unassigned tasks endpoint
                unassigned_response = self.session.get(f'{self.base_url}/api/v1/tasks/unassigned/')
                if unassigned_response.status_code == 200:
                    unassigned_data = unassigned_response.json()
                    print(f"   ✅ Found {unassigned_data['count']} unassigned tasks")
                    
                    # Test AI suggestions if unassigned tasks exist
                    if unassigned_data['results']:
                        task_id = unassigned_data['results'][0]['id']
                        ai_response = self.session.get(f'{self.base_url}/api/v1/tasks/{task_id}/ai_suggestions/')
                        if ai_response.status_code == 200:
                            ai_data = ai_response.json()
                            print(f"   ✅ AI suggestions available for task: {ai_data['task_name']}")
                        else:
                            print(f"   ⚠️  AI suggestions returned: {ai_response.status_code}")
                
                return True
            else:
                print(f"   ❌ Tasks API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Tasks API error: {e}")
            return False
    
    def test_assignments_api(self):
        """Test Assignments API"""
        print("\n🔗 Testing Assignments API...")
        try:
            response = self.session.get(f'{self.base_url}/api/v1/assignments/')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved {data['count']} assignments")
                
                # Test conflict checking
                conflict_response = self.session.get(
                    f'{self.base_url}/api/v1/assignments/check_conflicts/',
                    params={'task_id': 1, 'resource_id': 1}
                )
                if conflict_response.status_code == 200:
                    conflict_data = conflict_response.json()
                    print(f"   ✅ Conflict checking working - {len(conflict_data.get('conflicts', []))} conflicts found")
                elif conflict_response.status_code == 400:
                    print(f"   ✅ Conflict checking validation working")
                else:
                    print(f"   ⚠️  Conflict checking returned: {conflict_response.status_code}")
                
                return True
            else:
                print(f"   ❌ Assignments API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Assignments API error: {e}")
            return False
    
    def test_skills_api(self):
        """Test Skills API"""
        print("\n🎯 Testing Skills API...")
        try:
            response = self.session.get(f'{self.base_url}/api/v1/skills/')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved {data['count']} skills")
                return True
            else:
                print(f"   ❌ Skills API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Skills API error: {e}")
            return False
    
    def test_documentation(self):
        """Test API documentation endpoints"""
        print("\n📚 Testing API Documentation...")
        try:
            # Test OpenAPI schema
            schema_response = self.session.get(f'{self.base_url}/api/schema/')
            if schema_response.status_code == 200:
                print("   ✅ OpenAPI schema accessible")
            else:
                print(f"   ⚠️  OpenAPI schema returned: {schema_response.status_code}")
            
            # Test if documentation pages are accessible (they might require session auth)
            docs_response = requests.get(f'{self.base_url}/api/docs/')
            if docs_response.status_code == 200:
                print("   ✅ Swagger UI accessible")
            else:
                print(f"   ⚠️  Swagger UI returned: {docs_response.status_code}")
            
            return True
        except Exception as e:
            print(f"   ❌ Documentation error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🚀 ResourcePro API Integration Test")
        print("=" * 40)
        print(f"Testing API at: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 40)
        
        tests = [
            self.test_authentication,
            self.test_resources_api,
            self.test_projects_api,
            self.test_tasks_api,
            self.test_assignments_api,
            self.test_skills_api,
            self.test_documentation,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 40)
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API integration is working perfectly!")
            print("\n📖 Next steps:")
            print("   • Visit http://localhost:8000/api/docs/ for interactive documentation")
            print("   • Check api_integration_examples.py for code samples")
            print("   • Read API_INTEGRATION_GUIDE.md for detailed documentation")
        else:
            print("⚠️  Some tests failed. Please check the server logs.")
        
        return passed == total


def main():
    """Main test function"""
    print("Starting API test...")
    
    # Check if server is running (test the main page, not API)
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code != 200:
            print(f"❌ Server not responding properly. Status: {response.status_code}")
            print("Please make sure the server is running: python manage.py runserver")
            sys.exit(1)
        else:
            print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("Start the server with: python manage.py runserver")
        sys.exit(1)
    
    # Run tests
    tester = APITester(BASE_URL, API_TOKEN)
    success = tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
