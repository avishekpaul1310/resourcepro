#!/usr/bin/env python3
"""
Test script to verify the intervention simulation functionality
"""
import os
import sys
import django
import requests
import json

# Setup Django environment
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

def test_simulation_api():
    """Test the simulation API endpoint"""
    print("🔍 Testing Intervention Simulation API...")
    
    # Test data
    test_data = {
        'scenario_type': 'reassignment',
        'title': 'Test Problem',
        'description': 'Test problem description',
        'project_id': 1,
        'sourceResource': 1,
        'targetResource': 2,
        'workloadPercentage': 25
    }
    
    try:
        # Test the API endpoint
        response = requests.post(
            'http://127.0.0.1:8000/dashboard/api/simulate-intervention/',
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test'  # This might need to be handled differently
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint is working!")
            print(f"Success: {data.get('success', 'Unknown')}")
            if 'result' in data:
                print(f"Result type: {type(data['result'])}")
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server. Make sure it's running on http://127.0.0.1:8000/")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_javascript_functions():
    """Test that the JavaScript functions are properly defined"""
    print("\n🔍 Testing JavaScript Function Availability...")
    
    # Check if the JavaScript file exists and is readable
    js_file_path = os.path.join(project_root, 'static', 'js', 'ai_dashboard.js')
    
    if os.path.exists(js_file_path):
        print("✅ JavaScript file exists")
        
        # Read the file and check for function definitions
        with open(js_file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
            
        if 'function runSimulation()' in js_content:
            print("✅ runSimulation function is defined")
        else:
            print("❌ runSimulation function not found")
            
        if 'window.runSimulation = runSimulation' in js_content:
            print("✅ runSimulation is assigned to window object")
        else:
            print("❌ runSimulation not assigned to window object")
            
        if 'runSimulationBtn' in js_content:
            print("✅ Event listener for runSimulationBtn is set up")
        else:
            print("❌ Event listener for runSimulationBtn not found")
            
    else:
        print(f"❌ JavaScript file not found at {js_file_path}")

def main():
    print("🧪 Running Intervention Simulation Tests...")
    test_javascript_functions()
    test_simulation_api()
    print("\n✨ Test complete!")

if __name__ == '__main__':
    main()
