"""
AI services for dashboard features
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import time

from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.contrib.auth.models import User

from resources.models import Resource
from projects.models import Task, Project
from allocation.models import Assignment
from dashboard.models import DashboardAIAnalysis, InterventionScenario, NLIQuery, AIInsight
from utils.gemini_ai import gemini_service

logger = logging.getLogger(__name__)

class DashboardAIService:
    """AI-powered dashboard analysis service"""
    
    def generate_daily_briefing(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Generate AI-powered daily briefing for dashboard
        
        Args:
            force_refresh: If True, regenerate even if recent analysis exists
            
        Returns:
            Dictionary containing briefing data
        """
        # Check if we have recent analysis (within last 2 hours)
        if not force_refresh:
            recent_analysis = DashboardAIAnalysis.objects.filter(
                analysis_type='daily_briefing',
                created_at__gte=timezone.now() - timedelta(hours=2),
                is_active=True
            ).first()
            
            if recent_analysis:
                return self._format_analysis_response(recent_analysis)
        
        if not gemini_service.is_available():
            logger.warning("Gemini AI not available for dashboard analysis")
            return {"error": "AI service not available"}
        
        try:
            # Gather dashboard data
            dashboard_data = self._gather_dashboard_data()
            
            # Create prompt for AI analysis
            prompt = self._create_dashboard_analysis_prompt(dashboard_data)
            
            # Get AI analysis
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
            
            if not ai_response:
                logger.warning("AI service returned no response")
                return {"error": "Failed to generate AI analysis"}
            
            # Store and return analysis
            analysis = self._store_analysis(ai_response, dashboard_data)
            return self._format_analysis_response(analysis)
            
        except Exception as e:
            logger.error(f"Error generating dashboard briefing: {e}")
            return {"error": f"Failed to generate briefing: {str(e)}"}
    
    def _gather_dashboard_data(self) -> Dict[str, Any]:
        """Gather all dashboard data for AI analysis"""
        today = timezone.now().date()
        
        # Get resources with utilization
        resources = Resource.objects.all()
        resource_data = []
        total_utilization = 0
        overallocated_count = 0
        
        for resource in resources:
            utilization = resource.current_utilization()
            total_utilization += utilization
            if utilization > 100:
                overallocated_count += 1
            
            resource_data.append({
                "name": resource.name,
                "role": resource.role,
                "department": resource.department,
                "utilization": utilization,
                "skills": [skill.name for skill in resource.skills.all()],
                "is_overallocated": utilization > 100
            })
        
        avg_utilization = total_utilization / len(resources) if resources else 0
        
        # Get active projects
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold'])
        project_data = []
        
        for project in projects:
            completion = project.get_completion_percentage()
            project_data.append({
                "name": project.name,
                "status": project.status,
                "completion": completion,
                "start_date": project.start_date.isoformat(),
                "end_date": project.end_date.isoformat(),
                "days_until_deadline": (project.end_date - today).days if project.end_date else None
            })
          # Get upcoming deadlines
        upcoming_deadlines = Task.objects.filter(
            end_date__gte=today,
            end_date__lte=today + timedelta(days=14),
            status__in=['not_started', 'in_progress', 'blocked']
        ).order_by('end_date')
        
        deadline_data = []
        for task in upcoming_deadlines:
            days_until = (task.end_date - today).days
            # Get assigned resources through assignments
            assigned_resources = [assignment.resource.name for assignment in task.assignments.all()]
            deadline_data.append({
                "task": task.name,
                "project": task.project.name,
                "due_date": task.end_date.isoformat(),
                "days_until": days_until,
                "status": task.status,
                "priority": task.priority,
                "assigned_resources": assigned_resources
            })
        
        # Get unassigned tasks
        unassigned_tasks = Task.objects.filter(
            assignments=None,
            status__in=['not_started', 'in_progress', 'blocked']
        )
        
        unassigned_data = []
        for task in unassigned_tasks:
            unassigned_data.append({
                "task": task.name,
                "project": task.project.name,
                "priority": task.priority,
                "status": task.status,
                "due_date": task.end_date.isoformat() if task.end_date else None,
                "required_skills": [skill.name for skill in task.skills_required.all()]
            })
        
        return {
            "analysis_date": today.isoformat(),
            "resources": {
                "total": len(resources),
                "overallocated": overallocated_count,
                "average_utilization": round(avg_utilization, 1),
                "details": resource_data
            },
            "projects": {
                "total": len(projects),
                "active": len([p for p in projects if p.status == 'active']),
                "details": project_data
            },
            "deadlines": {
                "upcoming_count": len(deadline_data),
                "critical_count": len([d for d in deadline_data if d['days_until'] <= 2]),
                "details": deadline_data
            },
            "unassigned_tasks": {
                "count": len(unassigned_data),
                "details": unassigned_data
            }
        }
    
    def _create_dashboard_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for dashboard analysis"""
        return f"""
You are an expert resource management analyst providing daily briefings for a project management dashboard.

Current Dashboard Data:
{json.dumps(data, indent=2)}

Analyze this data and provide insights in the following format:

1. SUMMARY: A concise overview of the current situation (2-3 sentences)
2. KEY RISKS: Identify the top 3 most critical risks that need immediate attention
3. RECOMMENDATIONS: Provide 3-5 specific, actionable recommendations

For each risk and recommendation, include:
- title: Brief descriptive title
- description: Detailed explanation
- priority: "high", "medium", or "low"
- affected_items: List of affected resources, projects, or tasks
- confidence: Decimal from 0.0-1.0 based on data certainty

Focus on:
- Resource overallocation and bottlenecks
- Approaching deadlines vs. current progress
- Unassigned tasks that could impact deadlines
- Skill gaps or resource availability issues
- Cross-project dependencies and conflicts

Respond with valid JSON in this exact format:
{{
    "summary": "string",
    "confidence_score": decimal,
    "risks": [
        {{
            "title": "string",
            "description": "string",
            "priority": "high|medium|low",
            "affected_items": ["string"],
            "confidence": decimal
        }}
    ],
    "recommendations": [
        {{
            "title": "string",
            "description": "string",
            "priority": "high|medium|low",
            "affected_items": ["string"],
            "confidence": decimal
        }}
    ]
}}
"""
    
    def _store_analysis(self, ai_response: Dict[str, Any], dashboard_data: Dict[str, Any]) -> DashboardAIAnalysis:
        """Store AI analysis in database"""
        analysis = DashboardAIAnalysis.objects.create(
            analysis_type='daily_briefing',
            analysis_data=dashboard_data,
            summary=ai_response.get('summary', ''),
            risks=ai_response.get('risks', []),
            recommendations=ai_response.get('recommendations', []),
            confidence_score=ai_response.get('confidence_score', 0.0)
        )
        
        # Create AI insights from risks
        for risk in ai_response.get('risks', []):
            if risk.get('priority') in ['high', 'critical']:
                self._create_ai_insight_from_risk(risk, analysis)
        
        return analysis
    
    def _create_ai_insight_from_risk(self, risk: Dict[str, Any], analysis: DashboardAIAnalysis):
        """Create AI insight from identified risk"""
        insight_type = self._determine_insight_type(risk)
        severity = 'critical' if risk.get('priority') == 'high' else 'high'
        
        AIInsight.objects.create(
            insight_type=insight_type,
            severity=severity,
            title=risk.get('title', ''),
            description=risk.get('description', ''),
            confidence_score=risk.get('confidence', 0.0),
            data_context={'source_analysis': analysis.id, 'risk_data': risk}
        )
    
    def _determine_insight_type(self, risk: Dict[str, Any]) -> str:
        """Determine insight type based on risk content"""
        title = risk.get('title', '').lower()
        description = risk.get('description', '').lower()
        
        if 'deadline' in title or 'due' in title:
            return 'deadline_risk'
        elif 'overallocation' in title or 'overallocated' in description:
            return 'overallocation'
        elif 'bottleneck' in title or 'bottleneck' in description:
            return 'bottleneck'
        elif 'skill' in title or 'skill' in description:
            return 'skill_gap'
        else:
            return 'opportunity'
    
    def _format_analysis_response(self, analysis: DashboardAIAnalysis) -> Dict[str, Any]:
        """Format analysis for frontend response"""
        return {
            "id": analysis.id,
            "summary": analysis.summary,
            "risks": analysis.risks,
            "recommendations": analysis.recommendations,
            "confidence_score": analysis.confidence_score,
            "created_at": analysis.created_at.isoformat(),
            "is_fresh": (timezone.now() - analysis.created_at).total_seconds() < 3600  # Less than 1 hour old
        }

class InterventionSimulatorService:
    """AI-powered intervention scenario simulation service"""
    
    def simulate_intervention(self, scenario_data: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
        """
        Simulate an intervention scenario
        
        Args:
            scenario_data: Dictionary containing scenario parameters
            user: User requesting the simulation
            
        Returns:
            Dictionary containing simulation results
        """
        if not gemini_service.is_available():
            return {"error": "AI service not available"}
        
        try:
            # Gather context data
            context_data = self._gather_intervention_context(scenario_data)
            
            # Create simulation prompt
            prompt = self._create_simulation_prompt(scenario_data, context_data)
            
            # Get AI simulation
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.4)
            
            if not ai_response:
                return {"error": "Failed to generate simulation"}
            
            # Store simulation
            scenario = self._store_simulation(scenario_data, ai_response, context_data, user)
            
            return self._format_simulation_response(scenario)
            
        except Exception as e:
            logger.error(f"Error simulating intervention: {e}")
            return {"error": f"Simulation failed: {str(e)}"}
    
    def _gather_intervention_context(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gather context data for intervention simulation"""
        context = {
            "current_time": timezone.now().isoformat(),
            "resources": [],
            "projects": [],
            "tasks": []
        }
        
        # Get relevant resources
        if scenario_data.get('resource_id'):
            try:
                resource = Resource.objects.get(id=scenario_data['resource_id'])
                context["target_resource"] = {
                    "name": resource.name,
                    "role": resource.role,
                    "current_utilization": resource.current_utilization(),
                    "skills": [skill.name for skill in resource.skills.all()]
                }
            except Resource.DoesNotExist:
                pass
        
        # Get relevant projects and tasks
        if scenario_data.get('project_id'):
            try:
                project = Project.objects.get(id=scenario_data['project_id'])
                context["target_project"] = {
                    "name": project.name,
                    "status": project.status,
                    "completion": project.get_completion_percentage(),
                    "deadline": project.end_date.isoformat() if project.end_date else None
                }
            except Project.DoesNotExist:
                pass
        
        # Get available resources for reassignment scenarios
        if scenario_data.get('scenario_type') == 'reassignment':
            available_resources = Resource.objects.all()
            for resource in available_resources:
                context["resources"].append({
                    "name": resource.name,
                    "role": resource.role,
                    "utilization": resource.current_utilization(),
                    "availability": 100 - resource.current_utilization()
                })
        
        return context
    
    def _create_simulation_prompt(self, scenario_data: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Create prompt for intervention simulation"""
        return f"""
You are an expert project management consultant simulating intervention scenarios.

Scenario to Simulate:
{json.dumps(scenario_data, indent=2)}

Current Context:
{json.dumps(context_data, indent=2)}

Simulate this intervention scenario and provide:

1. PREDICTED_OUTCOME: Specific measurable outcomes
2. SUCCESS_PROBABILITY: Decimal from 0.0-1.0
3. ESTIMATED_IMPACT: Detailed impact analysis
4. ESTIMATED_COST: Cost in dollars (if applicable)
5. TIME_IMPACT: Time impact in hours
6. RISKS: Potential risks and mitigation strategies
7. ALTERNATIVES: Alternative approaches to consider

Focus on realistic, data-driven predictions based on the current context.

Respond with valid JSON in this exact format:
{{
    "predicted_outcome": {{
        "primary_metric": "string",
        "expected_value": "string",
        "timeline": "string"
    }},
    "success_probability": decimal,
    "estimated_impact": "string",
    "estimated_cost": decimal,
    "time_impact": integer,
    "risks": [
        {{
            "risk": "string",
            "probability": decimal,
            "mitigation": "string"
        }}
    ],
    "alternatives": [
        {{
            "option": "string",
            "description": "string",
            "pros": ["string"],
            "cons": ["string"]
        }}
    ]
}}
"""
    
    def _store_simulation(self, scenario_data: Dict[str, Any], ai_response: Dict[str, Any], 
                         context_data: Dict[str, Any], user: Optional[User]) -> InterventionScenario:
        """Store simulation results"""
        scenario = InterventionScenario.objects.create(
            scenario_type=scenario_data.get('scenario_type', 'reassignment'),
            title=scenario_data.get('title', 'Intervention Simulation'),
            description=scenario_data.get('description', ''),
            simulation_data=scenario_data,
            predicted_outcome=ai_response.get('predicted_outcome', {}),
            estimated_impact=ai_response.get('estimated_impact', ''),
            success_probability=ai_response.get('success_probability', 0.0),
            estimated_cost=ai_response.get('estimated_cost'),
            estimated_time_impact=ai_response.get('time_impact'),
            created_by=user
        )
        
        # Link to related objects if specified
        if scenario_data.get('project_id'):
            try:
                scenario.related_project = Project.objects.get(id=scenario_data['project_id'])
                scenario.save()
            except Project.DoesNotExist:
                pass
        
        return scenario
    
    def _format_simulation_response(self, scenario: InterventionScenario) -> Dict[str, Any]:
        """Format simulation response for frontend"""
        return {
            "id": scenario.id,
            "title": scenario.title,
            "scenario_type": scenario.scenario_type,
            "predicted_outcome": scenario.predicted_outcome,
            "estimated_impact": scenario.estimated_impact,
            "success_probability": scenario.success_probability,
            "estimated_cost": float(scenario.estimated_cost) if scenario.estimated_cost else None,
            "estimated_time_impact": scenario.estimated_time_impact,
            "created_at": scenario.created_at.isoformat()
        }

class NaturalLanguageInterfaceService:
    """Natural Language Interface service for AI queries"""
    
    def process_query(self, query_text: str, user: Optional[User] = None) -> Dict[str, Any]:
        """
        Process natural language query
        
        Args:
            query_text: The user's natural language query
            user: User making the query
            
        Returns:
            Dictionary containing query response
        """
        start_time = time.time()
        
        try:
            # Analyze query intent
            intent_data = self._analyze_query_intent(query_text)
            
            # Generate response based on intent
            response = self._generate_query_response(query_text, intent_data)
            
            execution_time = time.time() - start_time
            
            # Store query
            query_record = NLIQuery.objects.create(
                query_text=query_text,
                intent=intent_data.get('intent', ''),
                entities=intent_data.get('entities', {}),
                response_data=response,
                response_text=response.get('text', ''),
                execution_time=execution_time,
                success=not response.get('error'),
                error_message=response.get('error', ''),
                user=user
            )
            
            return {
                "id": query_record.id,
                "response": response,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error processing NLI query: {e}")
            return {"error": f"Failed to process query: {str(e)}"}
    
    def _analyze_query_intent(self, query_text: str) -> Dict[str, Any]:
        """Analyze query to determine intent and entities"""
        # Simple keyword-based intent analysis (can be enhanced with ML)
        query_lower = query_text.lower()
        
        intent = "general"
        entities = {}
        
        if any(word in query_lower for word in ["available", "free", "capacity"]):
            intent = "availability_query"
        elif any(word in query_lower for word in ["overallocated", "busy", "workload"]):
            intent = "utilization_query"
        elif any(word in query_lower for word in ["deadline", "due", "urgent"]):
            intent = "deadline_query"
        elif any(word in query_lower for word in ["skill", "expertise", "ability"]):
            intent = "skill_query"
        elif any(word in query_lower for word in ["project", "status", "progress"]):
            intent = "project_query"
        elif any(word in query_lower for word in ["risk", "problem", "issue"]):
            intent = "risk_query"
        
        return {"intent": intent, "entities": entities}
    
    def _generate_query_response(self, query_text: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response based on query intent"""
        intent = intent_data.get('intent', 'general')
        
        if intent == "availability_query":
            return self._handle_availability_query(query_text)
        elif intent == "utilization_query":
            return self._handle_utilization_query(query_text)
        elif intent == "deadline_query":
            return self._handle_deadline_query(query_text)
        elif intent == "skill_query":
            return self._handle_skill_query(query_text)
        elif intent == "project_query":
            return self._handle_project_query(query_text)
        elif intent == "risk_query":
            return self._handle_risk_query(query_text)
        else:
            return self._handle_general_query(query_text)
    
    def _handle_availability_query(self, query_text: str) -> Dict[str, Any]:
        """Handle availability-related queries"""
        resources = Resource.objects.all()
        available_resources = []
        
        for resource in resources:
            utilization = resource.current_utilization()
            if utilization < 80:  # Consider <80% as available
                available_resources.append({
                    "name": resource.name,
                    "role": resource.role,
                    "availability": 100 - utilization
                })
        
        if available_resources:
            text = f"Found {len(available_resources)} available resources:\n"
            for resource in available_resources[:5]:  # Show top 5
                text += f"• {resource['name']} ({resource['role']}) - {resource['availability']:.1f}% available\n"
        else:
            text = "No resources with significant availability found."
        
        return {
            "text": text,
            "data": available_resources,
            "type": "availability_list"
        }
    
    def _handle_utilization_query(self, query_text: str) -> Dict[str, Any]:
        """Handle utilization-related queries"""
        resources = Resource.objects.all()
        overallocated_resources = []
        
        for resource in resources:
            utilization = resource.current_utilization()
            if utilization > 100:
                overallocated_resources.append({
                    "name": resource.name,
                    "role": resource.role,
                    "utilization": utilization
                })
        
        if overallocated_resources:
            text = f"Found {len(overallocated_resources)} overallocated resources:\n"
            for resource in overallocated_resources:
                text += f"• {resource['name']} ({resource['role']}) - {resource['utilization']:.1f}% utilized\n"
        else:
            text = "No overallocated resources found."
        
        return {
            "text": text,
            "data": overallocated_resources,
            "type": "utilization_list"
        }
    
    def _handle_deadline_query(self, query_text: str) -> Dict[str, Any]:
        """Handle deadline-related queries"""
        today = timezone.now().date()
        upcoming_deadlines = Task.objects.filter(
            end_date__gte=today,
            end_date__lte=today + timedelta(days=7),
            status__in=['not_started', 'in_progress', 'blocked']
        ).order_by('end_date')[:10]
        
        deadline_data = []
        for task in upcoming_deadlines:
            days_until = (task.end_date - today).days
            deadline_data.append({
                "task": task.name,
                "project": task.project.name,
                "days_until": days_until,
                "status": task.status
            })
        
        if deadline_data:
            text = f"Found {len(deadline_data)} upcoming deadlines:\n"
            for deadline in deadline_data:
                text += f"• {deadline['task']} ({deadline['project']}) - {deadline['days_until']} days\n"
        else:
            text = "No upcoming deadlines in the next 7 days."
        
        return {
            "text": text,
            "data": deadline_data,
            "type": "deadline_list"
        }
    
    def _handle_skill_query(self, query_text: str) -> Dict[str, Any]:
        """Handle skill-related queries"""
        # This is a simplified implementation
        # In a real system, you'd use NLP to extract specific skills from the query
        return {
            "text": "Skill analysis feature is being enhanced. Please use the Skills Analytics page for detailed skill insights.",
            "data": {},
            "type": "skill_info"
        }
    
    def _handle_project_query(self, query_text: str) -> Dict[str, Any]:
        """Handle project-related queries"""
        active_projects = Project.objects.filter(status='active')
        project_data = []
        
        for project in active_projects:
            completion = project.get_completion_percentage()
            project_data.append({
                "name": project.name,
                "completion": completion,
                "status": project.status,
                "deadline": project.end_date.isoformat() if project.end_date else None
            })
        
        if project_data:
            text = f"Found {len(project_data)} active projects:\n"
            for project in project_data:
                text += f"• {project['name']} - {project['completion']:.1f}% complete\n"
        else:
            text = "No active projects found."
        
        return {
            "text": text,
            "data": project_data,
            "type": "project_list"
        }
    
    def _handle_risk_query(self, query_text: str) -> Dict[str, Any]:
        """Handle risk-related queries"""
        active_insights = AIInsight.objects.filter(
            is_active=True,
            is_resolved=False
        ).order_by('-severity', '-created_at')[:10]
        
        risk_data = []
        for insight in active_insights:
            risk_data.append({
                "title": insight.title,
                "severity": insight.severity,
                "type": insight.insight_type,
                "description": insight.description
            })
        
        if risk_data:
            text = f"Found {len(risk_data)} active risks:\n"
            for risk in risk_data:
                text += f"• {risk['title']} ({risk['severity']})\n"
        else:
            text = "No active risks identified."
        
        return {
            "text": text,
            "data": risk_data,
            "type": "risk_list"
        }
    
    def _handle_general_query(self, query_text: str) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "text": "I can help you with questions about resource availability, utilization, deadlines, skills, projects, and risks. Try asking something like 'Who is available for a new project?' or 'What are the upcoming deadlines?'",
            "data": {},
            "type": "help"
        }

# Create service instances
dashboard_ai_service = DashboardAIService()
intervention_simulator_service = InterventionSimulatorService()
nli_service = NaturalLanguageInterfaceService()
