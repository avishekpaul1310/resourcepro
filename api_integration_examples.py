"""
ResourcePro API Integration Examples
Complete examples for integrating with external applications

NOTE: This file contains examples that require additional packages:
- Flask example requires: pip install flask
- Async batch processing requires: pip install aiohttp

The code is structured to handle missing dependencies gracefully.
"""

# Example 1: Python Integration with Django
class ResourceProIntegration:
    """
    Example integration class for Python/Django applications
    """
    
    def __init__(self, base_url, token):
        import requests
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        })
    
    def get_available_resources(self, skills=None, start_date=None, end_date=None):
        """Get available resources for a time period"""
        params = {}
        if skills:
            params['required_skills'] = ','.join(map(str, skills))
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = self.session.get(
            f'{self.base_url}/api/v1/resources/available/',
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_project_with_tasks(self, project_data, tasks_data):
        """Create a project with multiple tasks"""
        # Create project
        project_response = self.session.post(
            f'{self.base_url}/api/v1/projects/',
            json=project_data
        )
        project_response.raise_for_status()
        project = project_response.json()
        
        # Create tasks
        created_tasks = []
        for task_data in tasks_data:
            task_data['project'] = project['id']
            task_response = self.session.post(
                f'{self.base_url}/api/v1/tasks/',
                json=task_data
            )
            task_response.raise_for_status()
            created_tasks.append(task_response.json())
        
        return {
            'project': project,
            'tasks': created_tasks
        }
    
    def auto_assign_tasks(self, task_ids):
        """Automatically assign multiple tasks using AI"""
        response = self.session.post(
            f'{self.base_url}/api/v1/assignments/bulk_assign/',
            json={
                'task_ids': task_ids,
                'auto_assign': True,
                'force_reassign': False
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_project_dashboard_data(self, project_id):
        """Get comprehensive dashboard data for a project"""
        # Get project details
        project_response = self.session.get(
            f'{self.base_url}/api/v1/projects/{project_id}/'
        )
        project_response.raise_for_status()
        project = project_response.json()
        
        # Get project statistics
        stats_response = self.session.get(
            f'{self.base_url}/api/v1/projects/{project_id}/statistics/'
        )
        stats_response.raise_for_status()
        statistics = stats_response.json()
        
        # Get assignments for this project
        assignments_response = self.session.get(
            f'{self.base_url}/api/v1/assignments/',
            params={'project': project_id}
        )
        assignments_response.raise_for_status()
        assignments = assignments_response.json()
        
        return {
            'project': project,
            'statistics': statistics,
            'assignments': assignments
        }

# Example 2: JavaScript/React Integration
"""
// ResourcePro API Client for React applications
class ResourceProClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Authorization': `Token ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Resource methods
  async getResources(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/v1/resources/?${params}`);
  }

  async getResourceUtilization(resourceId, startDate, endDate) {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    return this.request(`/api/v1/resources/${resourceId}/utilization/?${params}`);
  }

  // Project methods
  async getProjects(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/v1/projects/?${params}`);
  }

  async createProject(projectData) {
    return this.request('/api/v1/projects/', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  // Task methods
  async getUnassignedTasks() {
    return this.request('/api/v1/tasks/unassigned/');
  }

  async getTaskAISuggestions(taskId) {
    return this.request(`/api/v1/tasks/${taskId}/ai_suggestions/`);
  }

  // Assignment methods
  async createAssignment(assignmentData) {
    return this.request('/api/v1/assignments/', {
      method: 'POST',
      body: JSON.stringify(assignmentData),
    });
  }

  async bulkAssignTasks(taskIds) {
    return this.request('/api/v1/assignments/bulk_assign/', {
      method: 'POST',
      body: JSON.stringify({
        task_ids: taskIds,
        auto_assign: true,
        force_reassign: false,
      }),
    });
  }

  // Real-time updates
  subscribeToUpdates(callback) {
    const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws/api/updates/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }
}

// React Hook for ResourcePro API
function useResourceProAPI(baseUrl, token) {
  const [client] = useState(() => new ResourceProClient(baseUrl, token));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = async (apiMethod, ...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiMethod.apply(client, args);
      setLoading(false);
      return result;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  return {
    client,
    loading,
    error,
    apiCall,
  };
}

// Example React Component
function ProjectDashboard({ projectId }) {
  const { client, loading, error, apiCall } = useResourceProAPI(
    process.env.REACT_APP_API_URL,
    localStorage.getItem('apiToken')
  );
  
  const [projectData, setProjectData] = useState(null);

  useEffect(() => {
    const loadProjectData = async () => {
      try {
        const [project, stats, assignments] = await Promise.all([
          apiCall(client.getProjects, { id: projectId }),
          apiCall(client.request, `/api/v1/projects/${projectId}/statistics/`),
          apiCall(client.request, `/api/v1/assignments/?project=${projectId}`)
        ]);
        
        setProjectData({ project, stats, assignments });
      } catch (err) {
        console.error('Failed to load project data:', err);
      }
    };

    loadProjectData();
  }, [projectId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!projectData) return null;

  return (
    <div className="project-dashboard">
      <h1>{projectData.project.name}</h1>
      <div className="stats">
        <div>Total Tasks: {projectData.stats.total_tasks}</div>
        <div>Completed: {projectData.stats.completed_tasks}</div>
        <div>Progress: {projectData.stats.completion_percentage}%</div>
      </div>
      <div className="assignments">
        {projectData.assignments.results.map(assignment => (
          <div key={assignment.id} className="assignment">
            {assignment.resource.name} → {assignment.task.name}
          </div>
        ))}
      </div>
    </div>
  );
}
"""

# Example 3: PHP Integration
"""
<?php

class ResourceProAPI {
    private $baseUrl;
    private $token;
    private $httpClient;

    public function __construct($baseUrl, $token) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->token = $token;
        $this->httpClient = new \GuzzleHttp\Client([
            'headers' => [
                'Authorization' => 'Token ' . $token,
                'Content-Type' => 'application/json',
            ]
        ]);
    }

    public function getResources($filters = []) {
        $response = $this->httpClient->get($this->baseUrl . '/api/v1/resources/', [
            'query' => $filters
        ]);
        return json_decode($response->getBody(), true);
    }

    public function createProject($projectData) {
        $response = $this->httpClient->post($this->baseUrl . '/api/v1/projects/', [
            'json' => $projectData
        ]);
        return json_decode($response->getBody(), true);
    }

    public function assignResource($taskId, $resourceId, $allocatedHours) {
        $response = $this->httpClient->post($this->baseUrl . '/api/v1/assignments/', [
            'json' => [
                'task_id' => $taskId,
                'resource_id' => $resourceId,
                'allocated_hours' => $allocatedHours
            ]
        ]);
        return json_decode($response->getBody(), true);
    }

    public function getProjectDashboard($projectId) {
        $project = $this->httpClient->get($this->baseUrl . "/api/v1/projects/{$projectId}/");
        $stats = $this->httpClient->get($this->baseUrl . "/api/v1/projects/{$projectId}/statistics/");
        
        return [
            'project' => json_decode($project->getBody(), true),
            'statistics' => json_decode($stats->getBody(), true)
        ];
    }
}

// Usage example
$api = new ResourceProAPI('http://your-domain.com', 'your-token-here');

// Get available developers
$developers = $api->getResources(['role' => 'Developer']);

// Create a new project
$project = $api->createProject([
    'name' => 'New Mobile App',
    'description' => 'iOS and Android application',
    'start_date' => '2025-07-01',
    'end_date' => '2025-12-31',
    'status' => 'planning',
    'priority' => 4
]);

?>
"""

# Example 4: Node.js/Express Integration
"""
// Node.js Express middleware for ResourcePro integration
const axios = require('axios');

class ResourceProIntegration {
  constructor(baseUrl, token) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    });
  }

  // Middleware for Express.js
  createMiddleware() {
    return (req, res, next) => {
      req.resourcePro = this;
      next();
    };
  }

  async syncProjectData(projectId) {
    try {
      const [project, tasks, assignments] = await Promise.all([
        this.client.get(`/api/v1/projects/${projectId}/`),
        this.client.get(`/api/v1/tasks/?project=${projectId}`),
        this.client.get(`/api/v1/assignments/?project=${projectId}`)
      ]);

      return {
        project: project.data,
        tasks: tasks.data.results,
        assignments: assignments.data.results
      };
    } catch (error) {
      throw new Error(`Failed to sync project data: ${error.message}`);
    }
  }

  async autoAssignTasks(taskIds) {
    try {
      const response = await this.client.post('/api/v1/assignments/bulk_assign/', {
        task_ids: taskIds,
        auto_assign: true,
        force_reassign: false
      });
      return response.data;
    } catch (error) {
      throw new Error(`Auto-assignment failed: ${error.message}`);
    }
  }
}

// Express.js route examples
const express = require('express');
const app = express();

const resourcePro = new ResourceProIntegration(
  process.env.RESOURCEPRO_API_URL,
  process.env.RESOURCEPRO_API_TOKEN
);

app.use(resourcePro.createMiddleware());

// Get project dashboard
app.get('/projects/:id/dashboard', async (req, res) => {
  try {
    const dashboardData = await req.resourcePro.syncProjectData(req.params.id);
    res.json(dashboardData);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Auto-assign tasks
app.post('/projects/:id/auto-assign', async (req, res) => {
  try {
    const tasks = await req.resourcePro.client.get(`/api/v1/tasks/unassigned/?project=${req.params.id}`);
    const taskIds = tasks.data.results.map(task => task.id);
    
    const result = await req.resourcePro.autoAssignTasks(taskIds);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
"""

# Example 5: Webhook Integration
"""
ResourcePro Webhook Integration Example

Set up webhooks to receive real-time notifications about changes:

1. Configure webhook endpoints in ResourcePro settings
2. Handle webhook events in your application

Example webhook payload for assignment creation:
{
  "event": "assignment.created",
  "timestamp": "2025-06-24T10:30:00Z",
  "data": {
    "assignment": {
      "id": 123,
      "task": {
        "id": 456,
        "name": "Implement user authentication",
        "project": {"id": 789, "name": "Mobile App"}
      },
      "resource": {
        "id": 101,
        "name": "John Doe",
        "role": "Senior Developer"
      },
      "allocated_hours": 40
    }
  }
}

Flask webhook handler example:
"""

# Note: Install flask with: pip install flask
try:
    from flask import Flask, request, jsonify
    import hmac
    import hashlib
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Install with: pip install flask")

if FLASK_AVAILABLE:
    app = Flask(__name__)

    # Example helper functions (implement these according to your needs)
    def send_slack_notification(message):
        """Send notification to Slack (implement with your Slack webhook)"""
        print(f"Slack notification: {message}")
        # Example implementation:
        # import requests
        # slack_webhook_url = "your-slack-webhook-url"
        # requests.post(slack_webhook_url, json={"text": message})
    
    def update_external_pm_tool(assignment):
        """Update external project management tool"""
        print(f"Updating external PM tool with assignment: {assignment}")
        # Example implementation for Jira, Asana, etc.
    
    def generate_project_report(project_id):
        """Generate project completion report"""
        print(f"Generating report for project {project_id}")
        # Example implementation for report generation
    
    def notify_project_stakeholders(project):
        """Notify project stakeholders"""
        print(f"Notifying stakeholders for project: {project['name']}")
        # Example implementation for email notifications
    
    def alert_managers(message):
        """Alert project managers"""
        print(f"Manager alert: {message}")
        # Example implementation for manager notifications

    @app.route('/webhooks/resourcepro', methods=['POST'])
    def handle_resourcepro_webhook():
        # Verify webhook signature
        signature = request.headers.get('X-ResourcePro-Signature')
        payload = request.get_data()
        
        expected_signature = hmac.new(
            'your-webhook-secret'.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Process webhook event
        event_data = request.json
        event_type = event_data['event']
        
        if event_type == 'assignment.created':
            handle_assignment_created(event_data['data'])
        elif event_type == 'project.completed':
            handle_project_completed(event_data['data'])
        elif event_type == 'resource.overallocated':
            handle_resource_overallocated(event_data['data'])
        
        return jsonify({'status': 'processed'})

    def handle_assignment_created(data):
        """Handle new assignment webhook"""
        assignment = data['assignment']
        
        # Send notification to team
        send_slack_notification(
            f"New assignment: {assignment['resource']['name']} "
            f"assigned to {assignment['task']['name']}"
        )
        
        # Update external project management tool
        update_external_pm_tool(assignment)

    def handle_project_completed(data):
        """Handle project completion webhook"""
        project = data['project']
        
        # Generate completion report
        generate_project_report(project['id'])
        
        # Notify stakeholders
        notify_project_stakeholders(project)

    def handle_resource_overallocated(data):
        """Handle resource overallocation webhook"""
        resource = data['resource']
        
        # Alert project managers
        alert_managers(
            f"Resource {resource['name']} is overallocated "
            f"({resource['utilization']}%)"
        )

# Example 6: Batch Processing Integration
"""
Batch processing example for large-scale operations:
"""

import asyncio
# Note: Install aiohttp with: pip install aiohttp
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("aiohttp not installed. Install with: pip install aiohttp")

from datetime import datetime, timedelta

if AIOHTTP_AVAILABLE:
    class BatchResourceProcessor:
        def __init__(self, base_url, token):
            self.base_url = base_url
            self.headers = {'Authorization': f'Token {token}'}
        
        async def process_monthly_utilization_report(self):
            """Generate utilization reports for all resources"""
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Get all resources
                async with session.get(f'{self.base_url}/api/v1/resources/') as resp:
                    resources_data = await resp.json()
                
                # Process utilization for each resource
                tasks = []
                for resource in resources_data['results']:
                    task = self.calculate_resource_utilization(session, resource)
                    tasks.append(task)
                
                utilization_data = await asyncio.gather(*tasks)
                
                # Generate report
                return self.generate_utilization_report(utilization_data)
        
        async def calculate_resource_utilization(self, session, resource):
            """Calculate utilization for a single resource"""
            start_date = datetime.now().replace(day=1).date()
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
            async with session.get(
                f'{self.base_url}/api/v1/resources/{resource["id"]}/utilization/',
                params=params
            ) as resp:
                utilization_data = await resp.json()
            
            return {
                'resource': resource,
                'utilization': utilization_data
            }
        
        def generate_utilization_report(self, utilization_data):
            """Generate comprehensive utilization report"""
            report = {
                'period': datetime.now().strftime('%Y-%m'),
                'total_resources': len(utilization_data),
                'average_utilization': sum(
                    data['utilization']['utilization_percentage'] 
                    for data in utilization_data
                ) / len(utilization_data),
                'overallocated_resources': [
                    data for data in utilization_data
                    if data['utilization']['utilization_percentage'] > 100
                ],
                'underutilized_resources': [
                    data for data in utilization_data
                    if data['utilization']['utilization_percentage'] < 60
                ]
            }
            
            return report

    # Usage
    async def main():
        processor = BatchResourceProcessor(
            'http://your-domain.com',
            'your-token-here'
        )
        
        report = await processor.process_monthly_utilization_report()
        print(f"Monthly utilization report: {report}")

    # Run batch processing
    # asyncio.run(main())
else:
    print("BatchResourceProcessor requires aiohttp. Install with: pip install aiohttp")

if __name__ == "__main__":
    print("ResourcePro API Integration Examples")
    print("See the code above for various integration patterns:")
    print("1. Python/Django Integration")
    print("2. JavaScript/React Integration")
    print("3. PHP Integration")
    print("4. Node.js/Express Integration")
    print("5. Webhook Integration")
    print("6. Batch Processing Integration")
