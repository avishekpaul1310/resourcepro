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
from dashboard.models import DashboardAIAnalysis, InterventionScenario, NLIQuery, AIInsight, RiskCategory, DynamicRisk
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
                is_active=True            ).first()
            
            if recent_analysis:
                return self._format_analysis_response(recent_analysis)
        
        if not gemini_service.is_available():
            logger.warning("Gemini AI not available for dashboard analysis")
            return {"error": "AI service not available"}
        
        try:
            # Gather dashboard data
            dashboard_data = self._gather_dashboard_data()
            
            # Perform comprehensive risk analysis
            risk_service = EnhancedRiskAnalysisService()
            comprehensive_risks = risk_service.analyze_comprehensive_risks(dashboard_data)
            
            # Create prompt for AI analysis (enhanced with comprehensive risks)
            prompt = self._create_enhanced_dashboard_analysis_prompt(dashboard_data, comprehensive_risks)
            
            # Get AI analysis
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
            
            if not ai_response:
                logger.warning("AI service returned no response")
                return {"error": "Failed to generate AI analysis"}
            
            # Enhance response with comprehensive risk data
            ai_response['comprehensive_risks'] = comprehensive_risks
            ai_response['risk_categories'] = self._categorize_risks(comprehensive_risks)
            
            # Store and return analysis
            analysis = self._store_enhanced_analysis(ai_response, dashboard_data, comprehensive_risks)
            return self._format_enhanced_analysis_response(analysis)
            
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
    def _create_enhanced_dashboard_analysis_prompt(self, data: Dict[str, Any], comprehensive_risks: List[Dict[str, Any]]) -> str:
        """Create enhanced prompt including comprehensive risk analysis"""
        return f"""
You are an expert resource management analyst providing daily briefings for a project management dashboard.

Current Dashboard Data:
{json.dumps(data, indent=2)}

Comprehensive Risk Analysis:
{json.dumps(comprehensive_risks, indent=2)}

Based on both the dashboard data and the comprehensive risk analysis, provide insights in the following format:

{{
    "summary": "A concise overview of the current situation (2-3 sentences)",
    "risks": [
        {{
            "title": "Brief descriptive title",
            "description": "Detailed explanation",
            "priority": "high|medium|low",
            "affected_items": ["list of affected resources/projects/tasks"],
            "confidence": 0.85,
            "risk_category": "resource|technical|external|team|business|operational|financial|timeline|scope|quality"
        }}
    ],
    "recommendations": [
        {{
            "title": "Actionable recommendation title", 
            "description": "Detailed implementation guidance",
            "priority": "high|medium|low",
            "affected_items": ["list of affected items"],
            "confidence": 0.90,
            "intervention_type": "training|external_resource|process_improvement|technology_upgrade|communication_plan|quality_assurance|stakeholder_engagement|risk_mitigation|reassignment|overtime|resource_addition|deadline_extension|scope_reduction"
        }}
    ],
    "confidence_score": 0.85
}}

Focus on actionable insights that help project managers make informed decisions. Include risks from ALL categories, not just resource-related ones."""

    def _categorize_risks(self, comprehensive_risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize risks by type for better organization"""
        categories = {}
        
        for risk in comprehensive_risks:
            category = risk.get('category_type', 'operational')
            if category not in categories:
                categories[category] = []
            categories[category].append(risk)
        
        return categories

    def _store_enhanced_analysis(self, ai_response: Dict[str, Any], dashboard_data: Dict[str, Any], comprehensive_risks: List[Dict[str, Any]]) -> DashboardAIAnalysis:
        """Store enhanced analysis with comprehensive risk data"""
        analysis = DashboardAIAnalysis.objects.create(
            analysis_type='daily_briefing',
            summary=ai_response.get('summary', 'No summary available'),
            risks=ai_response.get('risks', []),
            recommendations=ai_response.get('recommendations', []),
            confidence_score=ai_response.get('confidence_score', 0.0),
            analysis_data={
                'dashboard_data': dashboard_data,
                'comprehensive_risks': comprehensive_risks,
                'ai_response': ai_response
            }
        )
        
        # Create AI insights for high-priority risks
        for risk in ai_response.get('risks', []):
            if risk.get('priority') == 'high':
                self._create_ai_insight_from_risk(risk, analysis)
        return analysis

    def _format_enhanced_analysis_response(self, analysis: DashboardAIAnalysis) -> Dict[str, Any]:
        """Format enhanced analysis for frontend response"""
        return {
            "id": analysis.id,
            "summary": analysis.summary,
            "risks": analysis.risks,
            "recommendations": analysis.recommendations,
            "confidence_score": analysis.confidence_score,
            "comprehensive_risks": analysis.analysis_data.get('comprehensive_risks', []),
            "risk_categories": self._categorize_risks(analysis.analysis_data.get('comprehensive_risks', [])),
            "created_at": analysis.created_at,
            "is_fresh": (timezone.now() - analysis.created_at).total_seconds() < 3600
        }
    
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
        
        # Note: No longer automatically creating AI insights from risks
        # to reduce redundancy - all insights are contained in the Daily Briefing
        
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
            "created_at": analysis.created_at,  # Keep as datetime object for template formatting
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
            "tasks": [],
            "project_tasks": [],
            "project_resources": []
        }
        
        # Get relevant resources
        if scenario_data.get('resource_id'):
            try:
                resource = Resource.objects.get(id=scenario_data['resource_id'])
                context["target_resource"] = {
                    "name": resource.name,
                    "role": resource.role,
                    "current_utilization": resource.current_utilization(),
                    "skills": [skill.name for skill in resource.skills.all()],
                    "hourly_rate": float(resource.hourly_rate) if hasattr(resource, 'hourly_rate') and resource.hourly_rate else 50.0
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
                    "deadline": project.end_date.isoformat() if project.end_date else None,
                    "total_budget": float(project.budget) if hasattr(project, 'budget') and project.budget else None
                }
                
                # Get project tasks for scope reduction scenarios
                project_tasks = Task.objects.filter(project=project)
                for task in project_tasks:
                    context["project_tasks"].append({                        "name": task.name,
                        "status": task.status,
                        "priority": getattr(task, 'priority', 'medium'),
                        "estimated_hours": float(task.estimated_hours) if task.estimated_hours else 0,
                        "completion": task.completion_percentage,
                        "assigned_resources": [a.resource.name for a in task.assignments.all()]
                    })
                
                # Get project resources for overtime scenarios
                assigned_resource_ids = Assignment.objects.filter(
                    task__project=project
                ).values_list('resource_id', flat=True).distinct()
                
                for resource_id in assigned_resource_ids:
                    try:
                        resource = Resource.objects.get(id=resource_id)
                        context["project_resources"].append({
                            "id": resource.id,
                            "name": resource.name,
                            "role": resource.role,
                            "utilization": resource.current_utilization(),
                            "availability": 100 - resource.current_utilization(),
                            "hourly_rate": float(resource.hourly_rate) if hasattr(resource, 'hourly_rate') and resource.hourly_rate else 50.0
                        })
                    except Resource.DoesNotExist:
                        pass
                        
            except Project.DoesNotExist:
                pass
        
        # Get all available resources for reassignment and additional resource scenarios
        if scenario_data.get('scenario_type') in ['reassignment', 'overtime', 'resource_addition']:
            available_resources = Resource.objects.all()
            for resource in available_resources:
                resource_data = {
                    "id": resource.id,
                    "name": resource.name,
                    "role": resource.role,
                    "utilization": resource.current_utilization(),
                    "availability": 100 - resource.current_utilization(),
                    "skills": [skill.name for skill in resource.skills.all()],
                    "hourly_rate": float(resource.hourly_rate) if hasattr(resource, 'hourly_rate') and resource.hourly_rate else 50.0
                }
                
                # Only add to general resources if not already in project_resources
                if not any(pr['id'] == resource.id for pr in context["project_resources"]):
                    context["resources"].append(resource_data)
        
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
            
            # Check if this is a simple query or needs AI processing
            if self._is_complex_query(query_text, intent_data):
                response = self._process_ai_query(query_text, user)
            else:
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
        elif any(word in query_lower for word in ["project", "status", "progress"]) and not any(word in query_lower for word in ["active", "most active"]):
            intent = "project_query"
        elif any(word in query_lower for word in ["risk", "problem", "issue"]):
            intent = "risk_query"
        elif any(word in query_lower for word in ["active", "most active", "activity", "productive", "engaged"]):
            intent = "activity_query"
        
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
        elif intent == "activity_query":
            return self._handle_activity_query(query_text)
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
            "text": "Skill analysis feature is being enhanced. Please use the Skills Analytics page for detailed skill insights.",            "data": {},
            "type": "skill_info"
        }
    
    def _handle_activity_query(self, query_text: str) -> Dict[str, Any]:
        """Handle activity-related queries like 'most active resource'"""
        from allocation.models import Assignment
        
        # Get all resources and calculate their activity level
        resources = Resource.objects.all()
        resource_activity = []
        
        for resource in resources:
            # Calculate activity based on current assignments and utilization
            active_assignments = Assignment.objects.filter(
                resource=resource
            ).count()
            
            utilization = resource.current_utilization()
            
            # Activity score combines number of assignments and utilization
            activity_score = (active_assignments * 20) + utilization
            
            resource_activity.append({
                "name": resource.name,
                "role": resource.role,
                "department": resource.department,
                "active_assignments": active_assignments,
                "utilization": utilization,
                "activity_score": activity_score
            })
        
        # Sort by activity score (highest first)
        resource_activity.sort(key=lambda x: x['activity_score'], reverse=True)
        
        if resource_activity:
            most_active = resource_activity[0]
            text = f"The most active resource is {most_active['name']} ({most_active['role']}):\n"
            text += f"• Current utilization: {most_active['utilization']:.1f}%\n"
            text += f"• Active assignments: {most_active['active_assignments']}\n"
            text += f"• Department: {most_active['department']}\n\n"
            
            if len(resource_activity) > 1:
                text += "Top 5 most active resources:\n"
                for i, resource in enumerate(resource_activity[:5], 1):
                    text += f"{i}. {resource['name']} - {resource['utilization']:.1f}% utilization, {resource['active_assignments']} assignments\n"
        else:
            text = "No resource activity data found."
        
        return {
            "text": text,
            "data": resource_activity[:10],  # Return top 10
            "type": "activity_list"
        }
    
    def _handle_general_query(self, query_text: str) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "text": "I can help you with questions about resource availability, utilization, deadlines, skills, projects, and risks. Try asking something like 'Who is available for a new project?' or 'What are the upcoming deadlines?'",
            "data": {},
            "type": "help"
        }
    
    def _is_complex_query(self, query_text: str, intent_data: Dict[str, Any]) -> bool:
        """Determine if query needs AI processing or can use simple matching"""
        query_lower = query_text.lower()
        
        # Complex query indicators
        complex_indicators = [
            # Comparisons
            "compare", "better", "worse", "vs", "versus", "between",
            # Calculations  
            "calculate", "total", "sum", "average", "cost", "budget", "forecast",
            # Analysis
            "analyze", "trend", "pattern", "correlation", "insight",
            # Superlatives that need data analysis
            "most experienced", "best", "worst", "highest", "lowest",
            # Time-based analysis
            "last month", "this quarter", "trend", "over time", "historically",
            # Multi-factor questions
            "and", "with", "having", "where",
            # Complex relationships
            "which project has", "what percentage", "how much", "how many",
        ]
        
        # If it's a general intent but has complex indicators, use AI
        if intent_data.get('intent') == 'general' and any(indicator in query_lower for indicator in complex_indicators):
            return True
            
        # If query is long and descriptive, likely complex
        if len(query_text.split()) > 8:
            return True
            
        # If it contains question words with multiple conditions
        question_words = ["which", "what", "how", "when", "where", "why"]
        if any(qw in query_lower for qw in question_words) and any(ci in query_lower for ci in complex_indicators):
            return True
            
        return False
    
    def _process_ai_query(self, query_text: str, user: Optional[User] = None) -> Dict[str, Any]:
        """Process complex queries using AI"""
        if not gemini_service.is_available():
            return {
                "text": "AI service is not available. I can only answer simple questions about availability, utilization, deadlines, and basic project information.",
                "data": {},
                "type": "error"
            }
        
        try:
            # Gather comprehensive data context
            context_data = self._gather_comprehensive_context()
            
            # Create AI prompt
            prompt = self._create_ai_query_prompt(query_text, context_data)
            
            # Get AI response
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
            
            if not ai_response:
                return {
                    "text": "I couldn't process that question. Please try asking something simpler or more specific.",
                    "data": {},
                    "type": "error"
                }
            
            return {
                "text": ai_response.get('answer', 'No answer provided'),
                "data": ai_response.get('data', {}),
                "calculations": ai_response.get('calculations', {}),
                "confidence": ai_response.get('confidence', 0),
                "type": "ai_response"
            }
            
        except Exception as e:
            logger.error(f"Error in AI query processing: {e}")
            return {
                "text": f"I encountered an error processing your question: {str(e)}. Please try asking something simpler.",
                "data": {},
                "type": "error"
            }
    
    def _gather_comprehensive_context(self) -> Dict[str, Any]:
        """Gather comprehensive data context for AI processing"""
        from allocation.models import Assignment
        
        context = {
            "current_date": timezone.now().date().isoformat(),
            "resources": [],
            "projects": [],
            "tasks": [],
            "assignments": []
        }
          # Get all resources with details
        resources = Resource.objects.all()
        for resource in resources:
            assignments_count = Assignment.objects.filter(resource=resource).count()
            context["resources"].append({
                "id": resource.id,
                "name": resource.name,
                "role": resource.role,
                "department": resource.department,
                "hourly_rate": float(resource.hourly_rate) if hasattr(resource, 'hourly_rate') and resource.hourly_rate else 0.0,
                "utilization": resource.current_utilization(),
                "skills": [skill.name for skill in resource.skills.all()],
                "assignments_count": assignments_count,
                "email": getattr(resource, 'email', '')
            })
          # Get all projects with details
        projects = Project.objects.all()
        for project in projects:
            task_count = project.tasks.count()
            completion = project.get_completion_percentage()
            context["projects"].append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "start_date": project.start_date.isoformat(),
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "budget": float(getattr(project, 'budget', 0)) if getattr(project, 'budget', None) else 0.0,
                "completion_percentage": completion,
                "task_count": task_count,
                "priority": getattr(project, 'priority', 'medium')
            })
        
        # Get all tasks with details
        tasks = Task.objects.all()
        for task in tasks:
            assigned_resources = [a.resource.name for a in task.assignments.all()]
            context["tasks"].append({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "project": task.project.name,
                "status": task.status,
                "priority": task.priority,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "estimated_hours": task.estimated_hours,
                "assigned_resources": assigned_resources,
                "required_skills": [skill.name for skill in task.skills_required.all()]
            })
        
        # Get assignment details
        assignments = Assignment.objects.all()
        for assignment in assignments:
            context["assignments"].append({
                "id": assignment.id,
                "resource": assignment.resource.name,
                "task": assignment.task.name,
                "project": assignment.task.project.name,
                "allocated_hours": assignment.allocated_hours,
                "created_at": assignment.created_at.isoformat()
            })
        
        return context
    
    def _create_ai_query_prompt(self, query_text: str, context_data: Dict[str, Any]) -> str:
        """Create AI prompt for complex query processing"""
        return f"""
You are an expert resource management analyst with access to comprehensive project data. 
Answer the user's question based on the provided data with accuracy and detail.

DATA CONTEXT:
Resources: {len(context_data['resources'])} total
Projects: {len(context_data['projects'])} total  
Tasks: {len(context_data['tasks'])} total
Assignments: {len(context_data['assignments'])} total

DETAILED DATA:
{json.dumps(context_data, indent=2)}

USER QUESTION: "{query_text}"

INSTRUCTIONS:
1. Analyze the data thoroughly to answer the question
2. Perform any necessary calculations
3. Provide specific, actionable insights
4. If the question cannot be answered with available data, say so clearly
5. Be conversational but professional

Respond in this JSON format:
{{
    "answer": "Clear, detailed response to the user's question",
    "data": {{
        "key_findings": ["list of key insights"],
        "relevant_items": ["specific resources/projects/tasks mentioned"],
        "numbers": {{"metric": "value"}}
    }},
    "calculations": {{
        "methodology": "How calculations were performed",
        "results": {{"calculation_name": "result"}}
    }},
    "confidence": 85,
    "recommendations": ["actionable suggestions based on analysis"]
}}
"""

# Enhanced AI services for comprehensive risk management

class EnhancedRiskAnalysisService:
    """Advanced AI-powered risk analysis for diverse project scenarios"""
    
    def analyze_comprehensive_risks(self, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify all types of risks, not just resource-related ones"""
        
        if not gemini_service.is_available():
            return []
        
        try:
            # Create comprehensive risk analysis prompt
            prompt = self._create_comprehensive_risk_prompt(project_context)
            
            # Get AI analysis
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.4)
            
            if not ai_response or 'risks' not in ai_response:
                return []
            
            # Process and categorize risks
            enhanced_risks = []
            for risk in ai_response['risks']:
                enhanced_risk = self._enhance_risk_analysis(risk, project_context)
                enhanced_risks.append(enhanced_risk)
            
            return enhanced_risks
            
        except Exception as e:
            logger.error(f"Error in comprehensive risk analysis: {e}")
            return []
    
    def _create_comprehensive_risk_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for comprehensive risk analysis"""
        return f"""
You are an expert project management risk analyst. Analyze the following project context and identify ALL types of risks that could impact project success.

Project Context:
{json.dumps(context, indent=2)}

Analyze for these risk categories:
1. RESOURCE & ALLOCATION: Team capacity, skill gaps, utilization issues
2. TECHNICAL & QUALITY: Technical debt, integration issues, quality problems
3. EXTERNAL DEPENDENCIES: Vendor delays, API issues, client dependencies
4. TEAM DYNAMICS: Communication, conflicts, knowledge silos
5. BUSINESS & STRATEGIC: Changing requirements, market shifts, priorities
6. OPERATIONAL: Infrastructure, tools, processes, compliance
7. FINANCIAL & BUDGET: Cost overruns, budget cuts, resource costs
8. TIMELINE & SCHEDULE: Deadline pressure, sequence issues, dependencies
9. SCOPE & REQUIREMENTS: Scope creep, unclear requirements, changes
10. QUALITY & STANDARDS: Quality standards, testing gaps, compliance

For each identified risk, provide:

{{
    "risks": [
        {{
            "category": "string (one of the categories above)",
            "title": "string",
            "description": "string (detailed explanation)",
            "severity": "low|medium|high|critical",
            "probability": decimal (0.0-1.0),
            "impact_score": decimal (0.0-10.0),
            "affected_items": ["string"],
            "root_causes": ["string"],
            "potential_triggers": ["string"],
            "impact_areas": ["timeline", "budget", "quality", "team_morale", "client_satisfaction"],
            "suggested_interventions": [
                {{
                    "intervention_type": "string",
                    "description": "string",
                    "effort_required": "low|medium|high",
                    "success_probability": decimal,
                    "estimated_cost": decimal,
                    "time_to_implement": "string"
                }}
            ],
            "monitoring_indicators": ["string"],
            "escalation_conditions": ["string"]
        }}
    ],
    "overall_risk_assessment": {{
        "project_risk_level": "low|medium|high|critical",
        "primary_concerns": ["string"],
        "immediate_actions_needed": ["string"],
        "long_term_strategies": ["string"]
    }}
}}
"""

    def _enhance_risk_analysis(self, risk: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance risk analysis with additional context and interventions"""
        
        # Map risk category to our model categories
        category_mapping = {
            'RESOURCE & ALLOCATION': 'resource',
            'TECHNICAL & QUALITY': 'technical',
            'EXTERNAL DEPENDENCIES': 'external',
            'TEAM DYNAMICS': 'team',
            'BUSINESS & STRATEGIC': 'business',
            'OPERATIONAL': 'operational',
            'FINANCIAL & BUDGET': 'financial',
            'TIMELINE & SCHEDULE': 'timeline',
            'SCOPE & REQUIREMENTS': 'scope',
            'QUALITY & STANDARDS': 'quality'
        }
        
        risk['category_type'] = category_mapping.get(risk.get('category', ''), 'operational')
        
        # Generate dynamic intervention scenarios
        risk['dynamic_interventions'] = self._generate_dynamic_interventions(risk, context)
        
        # Add risk metadata
        risk['analysis_timestamp'] = timezone.now().isoformat()
        risk['confidence'] = min(risk.get('probability', 0.5) * risk.get('impact_score', 5.0) / 5.0, 1.0)
        
        return risk
    
    def _generate_dynamic_interventions(self, risk: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate context-specific intervention strategies for any type of risk"""
        
        risk_category = risk.get('category_type', 'operational')
        severity = risk.get('severity', 'medium')
        
        # Base interventions by category
        category_interventions = {
            'resource': ['reassignment', 'overtime', 'resource_addition', 'training'],
            'technical': ['training', 'external_resource', 'technology_upgrade', 'process_improvement'],
            'external': ['stakeholder_engagement', 'risk_mitigation', 'scope_reduction'],
            'team': ['communication_plan', 'training', 'process_improvement'],
            'business': ['stakeholder_engagement', 'scope_reduction', 'deadline_extension'],
            'operational': ['process_improvement', 'technology_upgrade', 'risk_mitigation'],
            'financial': ['scope_reduction', 'resource_addition', 'deadline_extension'],
            'timeline': ['overtime', 'resource_addition', 'scope_reduction', 'deadline_extension'],
            'scope': ['scope_reduction', 'stakeholder_engagement', 'deadline_extension'],
            'quality': ['quality_assurance', 'training', 'process_improvement']
        }
        
        suggested_types = category_interventions.get(risk_category, ['custom'])
        
        # If high severity, add emergency interventions
        if severity in ['high', 'critical']:
            suggested_types.extend(['external_resource', 'stakeholder_engagement'])
        
        # Generate specific intervention details
        interventions = []
        for intervention_type in suggested_types[:5]:  # Limit to top 5
            intervention = self._create_intervention_details(intervention_type, risk, context)
            if intervention:
                interventions.append(intervention)
        
        return interventions
    
    def _create_intervention_details(self, intervention_type: str, risk: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed intervention plan for specific risk"""
        
        intervention_templates = {
            'training': {
                'name': 'Skill Development & Training',
                'description': 'Provide targeted training to address skill gaps',
                'effort': 'medium',
                'success_rate': 0.75,
                'time_range': '1-4 weeks'
            },
            'external_resource': {
                'name': 'External Consultant/Contractor',
                'description': 'Bring in specialized external expertise',
                'effort': 'high', 
                'success_rate': 0.85,
                'time_range': '1-2 weeks'
            },
            'process_improvement': {
                'name': 'Process Optimization',
                'description': 'Improve workflows and eliminate inefficiencies',
                'effort': 'medium',
                'success_rate': 0.70,
                'time_range': '2-6 weeks'
            },
            'technology_upgrade': {
                'name': 'Technology/Tool Enhancement',
                'description': 'Upgrade tools or implement new technology',
                'effort': 'high',
                'success_rate': 0.80,
                'time_range': '2-8 weeks'
            },
            'communication_plan': {
                'name': 'Communication Enhancement',
                'description': 'Improve team communication and collaboration',
                'effort': 'low',
                'success_rate': 0.65,
                'time_range': '1-2 weeks'
            },
            'quality_assurance': {
                'name': 'Quality Assurance Boost',
                'description': 'Implement additional QA measures and testing',
                'effort': 'medium',
                'success_rate': 0.80,
                'time_range': '1-3 weeks'
            },
            'stakeholder_engagement': {
                'name': 'Stakeholder Re-engagement',
                'description': 'Realign stakeholder expectations and requirements',
                'effort': 'medium',
                'success_rate': 0.70,
                'time_range': '1-2 weeks'
            },
            'risk_mitigation': {
                'name': 'Risk Mitigation Plan',
                'description': 'Develop comprehensive risk mitigation strategy',
                'effort': 'medium',
                'success_rate': 0.75,
                'time_range': '1-3 weeks'
            }
        }
        
        template = intervention_templates.get(intervention_type)
        if not template:
            return None
        
        return {
            'type': intervention_type,
            'name': template['name'],
            'description': f"{template['description']} - {risk.get('title', '')}",
            'effort_required': template['effort'],
            'success_probability': template['success_rate'],
            'time_to_implement': template['time_range'],
            'estimated_cost': self._estimate_intervention_cost(intervention_type, context),
            'risk_category': risk.get('category_type', 'operational')
        }
    
    def _estimate_intervention_cost(self, intervention_type: str, context: Dict[str, Any]) -> float:
        """Estimate cost for different intervention types"""
        
        # Base cost estimates (in USD)
        cost_estimates = {
            'training': 2000,
            'external_resource': 8000,
            'process_improvement': 3000,
            'technology_upgrade': 5000,
            'communication_plan': 500,
            'quality_assurance': 3000,
            'stakeholder_engagement': 1000,
            'risk_mitigation': 2000,
            'reassignment': 0,
            'overtime': 1500,
            'resource_addition': 6000,
            'deadline_extension': 500,
            'scope_reduction': 0
        }
        
        base_cost = cost_estimates.get(intervention_type, 1000)
        
        # Adjust based on project size/complexity
        project_count = len(context.get('projects', {}).get('details', []))
        team_size = context.get('resources', {}).get('total', 1)
        
        complexity_multiplier = 1 + (project_count * 0.2) + (team_size * 0.1)
        
        return base_cost * complexity_multiplier

# Create service instances
dashboard_ai_service = DashboardAIService()
intervention_simulator_service = InterventionSimulatorService()
nli_service = NaturalLanguageInterfaceService()
enhanced_risk_analysis_service = EnhancedRiskAnalysisService()
