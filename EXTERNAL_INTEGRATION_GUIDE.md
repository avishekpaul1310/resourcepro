# External Integration Guide for ResourcePro

This guide explains how to integrate ResourcePro with external project management tools, using Jira as a practical example. The concepts and patterns shown here can be applied to integrate with any external system.

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [Authentication Setup](#authentication-setup)
3. [Jira Integration Example](#jira-integration-example)
4. [Common Integration Patterns](#common-integration-patterns)
5. [Error Handling & Best Practices](#error-handling--best-practices)
6. [Testing Your Integration](#testing-your-integration)

## Integration Overview

ResourcePro provides a comprehensive REST API that allows external tools to:

- **Sync Resources**: Import/export team members and their skills
- **Manage Projects**: Create, update, and track project information
- **Handle Assignments**: Allocate resources to projects and tasks
- **Track Time**: Monitor work hours and utilization
- **Generate Reports**: Get analytics and insights

### Key Integration Components

1. **API Authentication**: Token-based or session-based authentication
2. **Data Synchronization**: Bidirectional sync between systems
3. **Webhook Support**: Real-time notifications for changes
4. **Conflict Resolution**: Handle data conflicts gracefully
5. **Error Recovery**: Robust error handling and retry mechanisms

## Authentication Setup

### 1. Create API Token

First, create an API token for your integration:

```bash
# Using Django management command
python manage.py create_api_token username=your_username
```

### 2. Test Authentication

```python
import requests

# Test your token
headers = {
    'Authorization': 'Token YOUR_API_TOKEN_HERE',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/users/me/', headers=headers)
print(f"Authentication test: {response.status_code}")
```

## Jira Integration Example

Here's a complete example showing how to integrate ResourcePro with Jira:

### 1. Jira to ResourcePro Sync

```python
import requests
from jira import JIRA
from datetime import datetime
import logging

class JiraResourceProIntegration:
    def __init__(self, jira_url, jira_user, jira_token, resourcepro_url, resourcepro_token):
        # Initialize Jira client
        self.jira = JIRA(
            server=jira_url,
            basic_auth=(jira_user, jira_token)
        )
        
        # ResourcePro API settings
        self.resourcepro_url = resourcepro_url
        self.headers = {
            'Authorization': f'Token {resourcepro_token}',
            'Content-Type': 'application/json'
        }
        
        self.logger = logging.getLogger(__name__)
    
    def sync_projects_from_jira(self):
        """Sync Jira projects to ResourcePro"""
        try:
            # Get all Jira projects
            jira_projects = self.jira.projects()
            
            for jira_project in jira_projects:
                # Map Jira project to ResourcePro format
                project_data = {
                    'name': jira_project.name,
                    'description': getattr(jira_project, 'description', ''),
                    'external_id': jira_project.key,
                    'status': 'active',
                    'start_date': datetime.now().date().isoformat(),
                    'priority': 'medium'
                }
                
                # Check if project already exists
                existing = self.get_resourcepro_project_by_external_id(jira_project.key)
                
                if existing:
                    # Update existing project
                    self.update_resourcepro_project(existing['id'], project_data)
                else:
                    # Create new project
                    self.create_resourcepro_project(project_data)
                    
        except Exception as e:
            self.logger.error(f"Error syncing projects: {e}")
            raise
    
    def sync_issues_as_tasks(self, project_key):
        """Sync Jira issues as ResourcePro tasks"""
        try:
            # Get issues from Jira project
            issues = self.jira.search_issues(f'project={project_key}')
            
            # Get corresponding ResourcePro project
            rp_project = self.get_resourcepro_project_by_external_id(project_key)
            if not rp_project:
                self.logger.warning(f"No ResourcePro project found for Jira key: {project_key}")
                return
            
            for issue in issues:
                task_data = {
                    'title': issue.fields.summary,
                    'description': getattr(issue.fields, 'description', ''),
                    'project': rp_project['id'],
                    'external_id': issue.key,
                    'status': self.map_jira_status_to_resourcepro(issue.fields.status.name),
                    'priority': self.map_jira_priority_to_resourcepro(
                        getattr(issue.fields, 'priority', None)
                    ),
                    'estimated_hours': self.extract_time_estimate(issue),
                    'due_date': self.extract_due_date(issue)
                }
                
                # Check if task already exists
                existing_task = self.get_resourcepro_task_by_external_id(issue.key)
                
                if existing_task:
                    self.update_resourcepro_task(existing_task['id'], task_data)
                else:
                    self.create_resourcepro_task(task_data)
                    
        except Exception as e:
            self.logger.error(f"Error syncing issues: {e}")
            raise
    
    def sync_work_logs(self, issue_key):
        """Sync Jira work logs to ResourcePro time entries"""
        try:
            issue = self.jira.issue(issue_key)
            worklogs = self.jira.worklogs(issue)
            
            # Get corresponding ResourcePro task
            rp_task = self.get_resourcepro_task_by_external_id(issue_key)
            if not rp_task:
                return
            
            for worklog in worklogs:
                # Map Jira user to ResourcePro user
                rp_user = self.get_resourcepro_user_by_jira_email(worklog.author.emailAddress)
                if not rp_user:
                    continue
                
                time_entry_data = {
                    'user': rp_user['id'],
                    'task': rp_task['id'],
                    'project': rp_task['project'],
                    'date': worklog.started.split('T')[0],  # Extract date
                    'hours': worklog.timeSpentSeconds / 3600,  # Convert to hours
                    'description': worklog.comment or '',
                    'external_id': worklog.id
                }
                
                # Check if time entry already exists
                existing_entry = self.get_resourcepro_time_entry_by_external_id(worklog.id)
                
                if not existing_entry:
                    self.create_resourcepro_time_entry(time_entry_data)
                    
        except Exception as e:
            self.logger.error(f"Error syncing work logs: {e}")
    
    # ResourcePro API Helper Methods
    def get_resourcepro_project_by_external_id(self, external_id):
        """Get ResourcePro project by external ID"""
        url = f"{self.resourcepro_url}/api/projects/"
        params = {'external_id': external_id}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return results[0] if results else None
        return None
    
    def create_resourcepro_project(self, project_data):
        """Create new project in ResourcePro"""
        url = f"{self.resourcepro_url}/api/projects/"
        response = requests.post(url, headers=self.headers, json=project_data)
        
        if response.status_code == 201:
            self.logger.info(f"Created project: {project_data['name']}")
            return response.json()
        else:
            self.logger.error(f"Failed to create project: {response.text}")
            return None
    
    def update_resourcepro_project(self, project_id, project_data):
        """Update existing project in ResourcePro"""
        url = f"{self.resourcepro_url}/api/projects/{project_id}/"
        response = requests.patch(url, headers=self.headers, json=project_data)
        
        if response.status_code == 200:
            self.logger.info(f"Updated project: {project_data['name']}")
            return response.json()
        else:
            self.logger.error(f"Failed to update project: {response.text}")
            return None
    
    # Mapping Helper Methods
    def map_jira_status_to_resourcepro(self, jira_status):
        """Map Jira status to ResourcePro status"""
        mapping = {
            'To Do': 'pending',
            'In Progress': 'in_progress',
            'Done': 'completed',
            'Closed': 'completed',
            'Open': 'pending'
        }
        return mapping.get(jira_status, 'pending')
    
    def map_jira_priority_to_resourcepro(self, jira_priority):
        """Map Jira priority to ResourcePro priority"""
        if not jira_priority:
            return 'medium'
        
        mapping = {
            'Highest': 'critical',
            'High': 'high',
            'Medium': 'medium',
            'Low': 'low',
            'Lowest': 'low'
        }
        return mapping.get(jira_priority.name, 'medium')
    
    def extract_time_estimate(self, issue):
        """Extract time estimate from Jira issue"""
        if hasattr(issue.fields, 'timeoriginalestimate') and issue.fields.timeoriginalestimate:
            return issue.fields.timeoriginalestimate / 3600  # Convert to hours
        return None
    
    def extract_due_date(self, issue):
        """Extract due date from Jira issue"""
        if hasattr(issue.fields, 'duedate') and issue.fields.duedate:
            return issue.fields.duedate
        return None

# Usage Example
def main():
    # Initialize integration
    integration = JiraResourceProIntegration(
        jira_url='https://your-company.atlassian.net',
        jira_user='your-email@company.com',
        jira_token='your-jira-api-token',
        resourcepro_url='http://localhost:8000',
        resourcepro_token='your-resourcepro-token'
    )
    
    # Sync data
    integration.sync_projects_from_jira()
    integration.sync_issues_as_tasks('PROJECT-KEY')
    integration.sync_work_logs('PROJECT-123')

if __name__ == '__main__':
    main()
```

### 2. ResourcePro to Jira Sync

```python
class ResourceProToJiraSync:
    def __init__(self, integration):
        self.integration = integration
    
    def sync_assignments_to_jira(self, project_id):
        """Sync ResourcePro assignments back to Jira"""
        # Get ResourcePro assignments
        assignments = self.get_resourcepro_assignments(project_id)
        
        for assignment in assignments:
            # Get corresponding Jira issue
            jira_issue_key = assignment['task']['external_id']
            if not jira_issue_key:
                continue
            
            try:
                # Update Jira issue assignee
                jira_user = self.get_jira_user_by_email(assignment['resource']['email'])
                if jira_user:
                    self.integration.jira.assign_issue(jira_issue_key, jira_user.accountId)
                    
                # Add comment about ResourcePro assignment
                comment = f"Assigned in ResourcePro to {assignment['resource']['name']} "
                comment += f"for {assignment['allocated_hours']} hours"
                self.integration.jira.add_comment(jira_issue_key, comment)
                
            except Exception as e:
                self.integration.logger.error(f"Failed to sync assignment: {e}")
    
    def update_jira_time_tracking(self, time_entry):
        """Update Jira time tracking from ResourcePro time entries"""
        jira_issue_key = time_entry['task']['external_id']
        if not jira_issue_key:
            return
        
        try:
            # Log work in Jira
            self.integration.jira.add_worklog(
                issue=jira_issue_key,
                timeSpent=f"{time_entry['hours']}h",
                comment=time_entry['description'],
                started=datetime.fromisoformat(time_entry['date'])
            )
        except Exception as e:
            self.integration.logger.error(f"Failed to log work in Jira: {e}")
```

## Common Integration Patterns

### 1. Bidirectional Sync

```python
class BidirectionalSync:
    def __init__(self, external_system, resourcepro):
        self.external = external_system
        self.resourcepro = resourcepro
        self.last_sync = self.get_last_sync_timestamp()
    
    def sync_all(self):
        """Perform full bidirectional sync"""
        try:
            # Sync from external system to ResourcePro
            self.sync_from_external()
            
            # Sync from ResourcePro to external system
            self.sync_to_external()
            
            # Update last sync timestamp
            self.update_last_sync_timestamp()
            
        except Exception as e:
            self.handle_sync_error(e)
    
    def sync_from_external(self):
        """Sync changes from external system"""
        changes = self.external.get_changes_since(self.last_sync)
        
        for change in changes:
            try:
                if change['type'] == 'project':
                    self.sync_project_from_external(change)
                elif change['type'] == 'task':
                    self.sync_task_from_external(change)
                elif change['type'] == 'user':
                    self.sync_user_from_external(change)
                    
            except Exception as e:
                self.log_sync_error(change, e)
    
    def handle_conflicts(self, resourcepro_item, external_item):
        """Handle sync conflicts"""
        # Strategy 1: Last modified wins
        if resourcepro_item['modified'] > external_item['modified']:
            return 'use_resourcepro'
        else:
            return 'use_external'
        
        # Strategy 2: Manual resolution (store conflicts for review)
        # self.store_conflict_for_manual_resolution(resourcepro_item, external_item)
        # return 'manual'
```

### 2. Webhook Integration

```python
# ResourcePro webhook handler
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def external_webhook_handler(request):
    """Handle webhooks from external systems"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        payload = json.loads(request.body)
        event_type = payload.get('event_type')
        
        if event_type == 'project_updated':
            handle_external_project_update(payload['data'])
        elif event_type == 'task_created':
            handle_external_task_creation(payload['data'])
        elif event_type == 'user_assigned':
            handle_external_assignment(payload['data'])
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def handle_external_project_update(data):
    """Handle project updates from external system"""
    external_id = data['external_id']
    
    # Find ResourcePro project
    try:
        project = Project.objects.get(external_id=external_id)
        
        # Update project data
        project.name = data['name']
        project.description = data['description']
        project.status = map_external_status(data['status'])
        project.save()
        
        # Trigger ResourcePro webhook to notify other systems
        trigger_resourcepro_webhook('project_updated', project)
        
    except Project.DoesNotExist:
        # Create new project if it doesn't exist
        create_project_from_external_data(data)
```

### 3. Real-time Sync with WebSockets

```python
import asyncio
import websockets
import json

class RealTimeSync:
    def __init__(self, resourcepro_url, external_ws_url):
        self.resourcepro_url = resourcepro_url
        self.external_ws_url = external_ws_url
    
    async def start_real_time_sync(self):
        """Start real-time synchronization"""
        # Connect to external system WebSocket
        async with websockets.connect(self.external_ws_url) as websocket:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_real_time_update(data)
                except Exception as e:
                    print(f"Error processing real-time update: {e}")
    
    async def process_real_time_update(self, data):
        """Process real-time updates from external system"""
        update_type = data.get('type')
        
        if update_type == 'assignment_changed':
            await self.sync_assignment_change(data)
        elif update_type == 'project_status_changed':
            await self.sync_project_status(data)
```

## Error Handling & Best Practices

### 1. Robust Error Handling

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            
        return wrapper
    return decorator

class IntegrationErrorHandler:
    def __init__(self, integration_name):
        self.integration_name = integration_name
        self.error_log = []
    
    def log_error(self, operation, error, data=None):
        """Log integration errors for analysis"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'integration': self.integration_name,
            'operation': operation,
            'error': str(error),
            'data': data
        }
        self.error_log.append(error_entry)
        
        # Also log to file or database
        self.persist_error(error_entry)
    
    def get_error_summary(self):
        """Get summary of recent errors"""
        return {
            'total_errors': len(self.error_log),
            'recent_errors': self.error_log[-10:],
            'error_types': self.group_errors_by_type()
        }
```

### 2. Data Validation

```python
from marshmallow import Schema, fields, ValidationError

class ProjectSyncSchema(Schema):
    """Schema for validating project sync data"""
    name = fields.Str(required=True, validate=lambda x: len(x) <= 200)
    description = fields.Str(missing='')
    external_id = fields.Str(required=True)
    status = fields.Str(validate=lambda x: x in ['active', 'inactive', 'completed'])
    start_date = fields.Date()
    end_date = fields.Date()

def validate_sync_data(data, schema_class):
    """Validate data before syncing"""
    schema = schema_class()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as e:
        return None, e.messages

# Usage
validated_data, errors = validate_sync_data(project_data, ProjectSyncSchema)
if errors:
    handle_validation_errors(errors)
else:
    sync_project(validated_data)
```

### 3. Performance Optimization

```python
class BatchSyncManager:
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        self.pending_operations = []
    
    def add_operation(self, operation_type, data):
        """Add operation to batch"""
        self.pending_operations.append({
            'type': operation_type,
            'data': data
        })
        
        if len(self.pending_operations) >= self.batch_size:
            self.execute_batch()
    
    def execute_batch(self):
        """Execute all pending operations in batch"""
        if not self.pending_operations:
            return
        
        # Group operations by type
        operations_by_type = {}
        for op in self.pending_operations:
            op_type = op['type']
            if op_type not in operations_by_type:
                operations_by_type[op_type] = []
            operations_by_type[op_type].append(op['data'])
        
        # Execute each operation type in batch
        for op_type, operations in operations_by_type.items():
            try:
                self.execute_batch_operation(op_type, operations)
            except Exception as e:
                self.handle_batch_error(op_type, operations, e)
        
        self.pending_operations.clear()
    
    def execute_batch_operation(self, operation_type, operations):
        """Execute a batch of operations of the same type"""
        if operation_type == 'create_projects':
            self.batch_create_projects(operations)
        elif operation_type == 'update_assignments':
            self.batch_update_assignments(operations)
        # Add more operation types as needed
```

## Testing Your Integration

### 1. Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
from your_integration import JiraResourceProIntegration

class TestJiraIntegration(unittest.TestCase):
    def setUp(self):
        self.integration = JiraResourceProIntegration(
            jira_url='https://test.atlassian.net',
            jira_user='test@test.com',
            jira_token='test-token',
            resourcepro_url='http://localhost:8000',
            resourcepro_token='test-rp-token'
        )
    
    @patch('requests.get')
    def test_get_resourcepro_project(self, mock_get):
        """Test getting ResourcePro project by external ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{'id': 1, 'name': 'Test Project'}]
        }
        mock_get.return_value = mock_response
        
        result = self.integration.get_resourcepro_project_by_external_id('TEST-1')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test Project')
    
    def test_status_mapping(self):
        """Test Jira to ResourcePro status mapping"""
        self.assertEqual(
            self.integration.map_jira_status_to_resourcepro('To Do'),
            'pending'
        )
        self.assertEqual(
            self.integration.map_jira_status_to_resourcepro('Done'),
            'completed'
        )
```

### 2. Integration Tests

```python
class IntegrationTestRunner:
    def __init__(self, config):
        self.config = config
        self.test_results = []
    
    def run_full_integration_test(self):
        """Run complete integration test suite"""
        tests = [
            self.test_authentication,
            self.test_project_sync,
            self.test_task_sync,
            self.test_assignment_sync,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                result = test()
                self.test_results.append({
                    'test': test.__name__,
                    'status': 'passed',
                    'result': result
                })
            except Exception as e:
                self.test_results.append({
                    'test': test.__name__,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return self.test_results
    
    def test_authentication(self):
        """Test API authentication"""
        # Test ResourcePro authentication
        headers = {'Authorization': f'Token {self.config["resourcepro_token"]}'}
        response = requests.get(f'{self.config["resourcepro_url"]}/api/users/me/', headers=headers)
        assert response.status_code == 200, "ResourcePro authentication failed"
        
        # Test external system authentication
        # Add your external system auth test here
        
        return "Authentication successful"
    
    def test_project_sync(self):
        """Test project synchronization"""
        # Create test project in external system
        # Sync to ResourcePro
        # Verify sync worked correctly
        pass
```

## Integration with Other PM Tools

### Asana Integration

```python
import asana

class AsanaIntegration:
    def __init__(self, access_token, resourcepro_url, resourcepro_token):
        self.client = asana.Client.access_token(access_token)
        self.resourcepro_url = resourcepro_url
        self.headers = {
            'Authorization': f'Token {resourcepro_token}',
            'Content-Type': 'application/json'
        }
    
    def sync_projects_from_asana(self, workspace_gid):
        """Sync Asana projects to ResourcePro"""
        projects = self.client.projects.get_projects({
            'workspace': workspace_gid
        })
        
        for asana_project in projects:
            project_data = {
                'name': asana_project['name'],
                'external_id': asana_project['gid'],
                'status': 'active'
            }
            # Create or update in ResourcePro
            self.create_or_update_resourcepro_project(project_data)
```

### Monday.com Integration

```python
import requests

class MondayIntegration:
    def __init__(self, api_token, resourcepro_url, resourcepro_token):
        self.api_token = api_token
        self.monday_url = "https://api.monday.com/v2"
        self.resourcepro_url = resourcepro_url
        self.resourcepro_headers = {
            'Authorization': f'Token {resourcepro_token}',
            'Content-Type': 'application/json'
        }
    
    def query_monday(self, query):
        """Execute GraphQL query against Monday.com API"""
        headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            self.monday_url,
            json={'query': query},
            headers=headers
        )
        
        return response.json()
    
    def sync_boards_as_projects(self):
        """Sync Monday.com boards as ResourcePro projects"""
        query = '''
        {
            boards {
                id
                name
                description
                state
            }
        }
        '''
        
        result = self.query_monday(query)
        boards = result['data']['boards']
        
        for board in boards:
            project_data = {
                'name': board['name'],
                'description': board['description'] or '',
                'external_id': board['id'],
                'status': 'active' if board['state'] == 'active' else 'inactive'
            }
            # Create or update in ResourcePro
            self.create_or_update_resourcepro_project(project_data)
```

## Conclusion

This guide provides a comprehensive framework for integrating ResourcePro with external project management tools. The Jira example demonstrates:

1. **Authentication** setup and token management
2. **Bidirectional sync** between systems
3. **Data mapping** and transformation
4. **Error handling** and retry mechanisms
5. **Real-time integration** with webhooks and WebSockets
6. **Testing strategies** for reliable integrations

You can adapt these patterns for any external system by:

1. Replacing Jira-specific API calls with your target system's API
2. Adjusting data mappings for your system's data structure
3. Implementing your system's authentication method
4. Customizing conflict resolution strategies
5. Adding system-specific error handling

The key is to start simple with basic CRUD operations and gradually add more sophisticated features like real-time sync and advanced conflict resolution.

### Next Steps

1. **Choose your integration approach**: Start with unidirectional sync, then move to bidirectional
2. **Set up authentication**: Create API tokens for both systems
3. **Implement basic sync**: Start with projects, then add tasks and assignments
4. **Add error handling**: Implement robust error handling and logging
5. **Test thoroughly**: Create comprehensive test suites
6. **Monitor and maintain**: Set up monitoring and alerting for your integration

Remember to always test integrations in a development environment before deploying to production, and consider the data privacy and security implications of syncing data between systems.
