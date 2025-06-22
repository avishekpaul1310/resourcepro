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
from dashboard.models import DashboardAIAnalysis, NLIQuery, AIInsight, RiskCategory, DynamicRisk, AIRecommendation
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
        """        # Check if we have recent analysis (within last 2 hours)
        if not force_refresh:
            recent_analysis = DashboardAIAnalysis.objects.filter(
                analysis_type='daily_briefing',
                created_at__gte=timezone.now() - timedelta(hours=2),
                is_active=True            ).first()
            
            if recent_analysis:
                return self._format_enhanced_analysis_response(recent_analysis)
        
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
        # Enrich risks with database IDs where available
        enriched_risks = self._enrich_risks_with_database_ids(analysis.risks)
        
        return {
            "id": analysis.id,
            "summary": analysis.summary,
            "risks": enriched_risks,
            "recommendations": analysis.recommendations,
            "confidence_score": analysis.confidence_score,
            "comprehensive_risks": analysis.analysis_data.get('comprehensive_risks', []),
            "risk_categories": self._categorize_risks(analysis.analysis_data.get('comprehensive_risks', [])),
            "created_at": analysis.created_at,
            "is_fresh": (timezone.now() - analysis.created_at).total_seconds() < 3600        }
    
    def _enrich_risks_with_database_ids(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich AI-generated risks with database IDs where matches exist"""
        enriched_risks = []
        
        # Get all existing dynamic risks
        existing_risks = DynamicRisk.objects.all()
        
        for risk in risks:
            enriched_risk = risk.copy()
            
            # Try to match with existing database risks by keywords and similarity
            risk_title = risk.get('title', '').lower()
            best_match = None
            best_score = 0
            
            for db_risk in existing_risks:
                db_title = db_risk.title.lower()
                
                # Check for exact keyword matches first
                if 'deadline' in risk_title and 'deadline' in db_title:
                    best_match = db_risk
                    break
                elif 'overallocation' in risk_title and 'overallocation' in db_title:
                    best_match = db_risk
                    break
                elif 'communication' in risk_title and 'communication' in db_title:
                    best_match = db_risk
                    break
                elif 'skill' in risk_title and 'skill' in db_title:
                    best_match = db_risk
                    break
                else:
                    # Calculate title similarity
                    similarity = self._calculate_title_similarity(risk_title, db_title)
                    if similarity > best_score:
                        best_score = similarity
                        if similarity > 0.3:  # Lower threshold for similarity
                            best_match = db_risk
            
            if best_match:
                enriched_risk['id'] = best_match.id
                enriched_risk['database_risk_id'] = best_match.id
                print(f"Matched '{risk.get('title')}' with '{best_match.title}' (ID: {best_match.id})")
            
            enriched_risks.append(enriched_risk)
        
        return enriched_risks
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        title1_words = set(title1.lower().split())
        title2_words = set(title2.lower().split())
        
        if not title1_words or not title2_words:
            return 0.0
        
        intersection = title1_words.intersection(title2_words)
        union = title1_words.union(title2_words)
        
        return len(intersection) / len(union) if union else 0.0
    
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
            "confidence_score": analysis.confidence_score,            "created_at": analysis.created_at,  # Keep as datetime object for template formatting
            "is_fresh": (timezone.now() - analysis.created_at).total_seconds() < 3600  # Less than 1 hour old
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
        
        # Enhanced context-aware filtering
        project_context = context.get('project_context', {})
        budget_level = self._categorize_budget(project_context.get('budget', 0))
        timeline_pressure = self._assess_timeline_pressure(project_context)
        team_size = self._categorize_team_size(context.get('team_size', 0))
        project_type = project_context.get('project_type', 'standard')
        
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
        
        # Context-based filtering and prioritization
        filtered_types = self._filter_by_context(suggested_types, budget_level, timeline_pressure, team_size, project_type)
        
        # If high severity, add emergency interventions (but filter by budget)
        if severity in ['high', 'critical']:
            emergency_options = ['external_resource', 'stakeholder_engagement']
            if budget_level in ['high', 'medium']:  # Only add expensive options if budget allows
                filtered_types.extend(emergency_options)
            elif timeline_pressure == 'high':
                filtered_types.extend(['overtime', 'scope_reduction'])  # Cheaper emergency options
        
        # Generate specific intervention details for filtered types
        interventions = []
        for intervention_type in filtered_types[:6]:  # Limit to top 6 most relevant
            intervention = self._create_intervention_details(intervention_type, risk, context)
            if intervention:
                # Add context-specific success probability adjustments
                intervention = self._adjust_for_context(intervention, budget_level, timeline_pressure, team_size)
                interventions.append(intervention)
        
        return interventions
    
    def _categorize_budget(self, budget: float) -> str:
        """Categorize project budget level"""
        if budget >= 100000:
            return 'high'
        elif budget >= 25000:
            return 'medium'
        else:
            return 'low'
    
    def _assess_timeline_pressure(self, project_context: Dict) -> str:
        """Assess timeline pressure level"""
        days_remaining = project_context.get('days_remaining', 30)
        completion_percentage = project_context.get('completion_percentage', 0)
        
        if days_remaining <= 7 and completion_percentage < 80:
            return 'critical'
        elif days_remaining <= 14 and completion_percentage < 60:
            return 'high'
        elif days_remaining <= 30 and completion_percentage < 40:
            return 'medium'
        else:
            return 'low'
    
    def _categorize_team_size(self, team_size: int) -> str:
        """Categorize team size"""
        if team_size >= 10:
            return 'large'
        elif team_size >= 5:
            return 'medium'
        elif team_size >= 2:
            return 'small'
        else:
            return 'minimal'
    
    def _filter_by_context(self, interventions: List[str], budget_level: str, timeline_pressure: str, team_size: str, project_type: str) -> List[str]:
        """Filter and prioritize interventions based on project context"""
        filtered = []
        
        # Budget-based filtering
        expensive_interventions = ['external_resource', 'technology_upgrade', 'resource_addition']
        cheap_interventions = ['reassignment', 'process_improvement', 'communication_plan']
        
        for intervention in interventions:
            # Budget filtering
            if budget_level == 'low' and intervention in expensive_interventions:
                continue  # Skip expensive options for low budget
            
            # Timeline pressure filtering
            if timeline_pressure in ['critical', 'high']:
                # Prioritize quick wins
                if intervention in ['overtime', 'scope_reduction', 'reassignment']:
                    filtered.insert(0, intervention)  # Add to front
                elif intervention in ['training', 'technology_upgrade']:
                    continue  # Skip long-term solutions under time pressure
                else:
                    filtered.append(intervention)
            else:
                # Normal priority
                filtered.append(intervention)
            
            # Team size considerations
            if team_size == 'minimal' and intervention == 'reassignment':
                continue  # Can't reassign in minimal teams
            
            # Project type considerations
            if project_type == 'maintenance' and intervention == 'resource_addition':
                continue  # Maintenance projects rarely need additional resources
        
        return list(dict.fromkeys(filtered))  # Remove duplicates while preserving order
    
    def _adjust_for_context(self, intervention: Dict, budget_level: str, timeline_pressure: str, team_size: str) -> Dict:
        """Adjust intervention success rates and costs based on context"""
        
        # Adjust success probability based on context
        base_success = intervention.get('success_rate', 0.75)
        
        # Budget impact on success
        if budget_level == 'high' and intervention['name'] in ['External Consultant/Contractor', 'Technology Upgrade']:
            base_success += 0.1  # Better resources = higher success
        elif budget_level == 'low' and intervention['name'] in ['External Consultant/Contractor']:
            base_success -= 0.15  # Budget constraints reduce quality
        
        # Timeline pressure impact
        if timeline_pressure in ['critical', 'high']:
            if intervention['name'] in ['Overtime Authorization', 'Scope Reduction']:
                base_success += 0.05  # These work well under pressure
            else:
                base_success -= 0.1  # Most interventions suffer under time pressure
        
        # Team size impact
        if team_size == 'large' and intervention['name'] == 'Communication Enhancement':
            base_success += 0.1  # More important in large teams
        elif team_size == 'minimal' and intervention['name'] == 'Task Reassignment':
            base_success -= 0.2  # Hard to reassign in small teams
        
        intervention['success_rate'] = max(0.1, min(0.95, base_success))  # Keep between 10-95%
        
        return intervention

    def _create_intervention_details(self, intervention_type: str, risk: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed intervention information based on type and context"""
        
        # Base intervention templates
        intervention_templates = {
            'reassignment': {
                'name': 'Task Reassignment',
                'description': 'Redistribute tasks among team members based on skills and availability',
                'estimated_cost': 500,
                'time_range': '1-3 days',
                'success_rate': 0.75
            },
            'overtime': {
                'name': 'Overtime Authorization',
                'description': 'Authorize additional working hours to meet deadlines',
                'estimated_cost': 2000,
                'time_range': '1-2 weeks',
                'success_rate': 0.65
            },
            'resource_addition': {
                'name': 'Additional Resource',
                'description': 'Add temporary or permanent team members to increase capacity',
                'estimated_cost': 8000,
                'time_range': '2-4 weeks',
                'success_rate': 0.80
            },
            'deadline_extension': {
                'name': 'Deadline Extension',
                'description': 'Negotiate timeline extension with stakeholders',
                'estimated_cost': 0,
                'time_range': '1 week',
                'success_rate': 0.60
            },
            'scope_reduction': {
                'name': 'Scope Reduction',
                'description': 'Reduce project scope to meet timeline and budget constraints',
                'estimated_cost': 0,
                'time_range': '1-2 weeks',
                'success_rate': 0.70
            },
            'training': {
                'name': 'Training & Development',
                'description': 'Provide targeted training to address skill gaps',
                'estimated_cost': 3000,
                'time_range': '2-6 weeks',
                'success_rate': 0.85
            },
            'external_resource': {
                'name': 'External Consultant/Contractor',
                'description': 'Engage external experts or contractors for specialized skills',
                'estimated_cost': 12000,
                'time_range': '1-8 weeks',
                'success_rate': 0.80
            },
            'process_improvement': {
                'name': 'Process Optimization',
                'description': 'Streamline workflows and eliminate inefficiencies',
                'estimated_cost': 1500,
                'time_range': '2-4 weeks',
                'success_rate': 0.75
            },
            'technology_upgrade': {
                'name': 'Technology Upgrade',
                'description': 'Upgrade tools, infrastructure, or technology stack',
                'estimated_cost': 15000,
                'time_range': '4-8 weeks',
                'success_rate': 0.70
            },
            'risk_mitigation': {
                'name': 'Risk Mitigation',
                'description': 'Implement specific measures to reduce identified risks',
                'estimated_cost': 2500,
                'time_range': '1-3 weeks',
                'success_rate': 0.65
            },
            'communication_plan': {
                'name': 'Communication Enhancement',
                'description': 'Improve communication channels and meeting structures',
                'estimated_cost': 500,
                'time_range': '1-2 weeks',
                'success_rate': 0.70
            },
            'quality_assurance': {
                'name': 'Quality Enhancement',
                'description': 'Strengthen quality assurance processes and controls',
                'estimated_cost': 3500,
                'time_range': '2-6 weeks',
                'success_rate': 0.80
            },
            'stakeholder_engagement': {
                'name': 'Stakeholder Alignment',
                'description': 'Improve stakeholder communication and expectation management',
                'estimated_cost': 1000,
                'time_range': '1-4 weeks',
                'success_rate': 0.65
            }
        }
        
        # Get base template
        intervention = intervention_templates.get(intervention_type, {
            'name': 'Custom Intervention',
            'description': 'Custom intervention strategy',
            'estimated_cost': 2000,
            'time_range': '2-4 weeks',
            'success_rate': 0.70
        })
        
        # Customize description based on risk context
        risk_title = risk.get('title', 'project issue')
        risk_category = risk.get('category_type', 'general')
        
        # Add context-specific details to description
        if intervention_type == 'reassignment' and risk_category == 'resource':
            intervention['description'] = f"Redistribute tasks to better match team member skills and availability for {risk_title}"
        elif intervention_type == 'training' and risk_category == 'technical':
            intervention['description'] = f"Provide technical training to address skill gaps related to {risk_title}"
        elif intervention_type == 'external_resource' and risk_category == 'technical':
            intervention['description'] = f"Engage external technical experts to resolve {risk_title}"
        
        return intervention
    def generate_risk_recommendations(self, risk_id, risk_data=None):
        """
        Generate simple AI recommendations for a specific risk
        
        Args:
            risk_id: ID of the risk (can be string or int)
            risk_data: Optional risk data dict if risk_id is not a database ID
            
        Returns:
            List of AIRecommendation objects
        """
        if not gemini_service.is_available():
            logger.warning("Gemini AI not available for recommendations")
            return {"error": "AI service not available"}
        
        risk_obj = None
        
        try:
            # Handle different risk_id types
            if isinstance(risk_id, str) and risk_data:
                # Use provided risk data for generated risks
                context = {
                    "risk": {
                        "title": risk_data.get('title', 'Unknown Risk'),
                        "description": risk_data.get('description', ''),
                        "severity": risk_data.get('priority', 'medium'),
                        "category": risk_data.get('category_type', 'general'),
                        "probability": risk_data.get('probability', 0.5),
                        "impact_score": risk_data.get('impact_score', 5.0)
                    },
                    "project": None,
                    "resources": []
                }
                risk_title = risk_data.get('title', 'Unknown Risk')
            else:
                # Try to get from database
                from dashboard.models import DynamicRisk
                try:
                    risk_obj = DynamicRisk.objects.get(id=int(risk_id))
                    # Create context for the risk
                    context = {
                        "risk": {
                            "title": risk_obj.title,
                            "description": risk_obj.description,
                            "severity": risk_obj.severity,
                            "category": risk_obj.category.risk_type if risk_obj.category else "general",
                            "probability": risk_obj.probability,
                            "impact_score": risk_obj.impact_score
                        },
                        "project": None,
                        "resources": []
                    }
                    
                    # Add project context if available
                    if risk_obj.related_project:
                        context["project"] = {
                            "name": risk_obj.related_project.name,
                            "status": risk_obj.related_project.status,
                            "completion": risk_obj.related_project.get_completion_percentage(),
                            "deadline": risk_obj.related_project.end_date.isoformat() if risk_obj.related_project.end_date else None
                        }
                    
                    # Add resource context if available
                    if risk_obj.related_resource:
                        context["resources"].append({
                            "name": risk_obj.related_resource.name,
                            "role": risk_obj.related_resource.role,
                            "utilization": risk_obj.related_resource.current_utilization()
                        })
                    
                    risk_title = risk_obj.title
                    
                except (DynamicRisk.DoesNotExist, ValueError):
                    # Fallback for string IDs
                    context = {
                        "risk": {
                            "title": f"Risk {risk_id}",
                            "description": "General project risk",
                            "severity": "medium",
                            "category": "general",
                            "probability": 0.5,
                            "impact_score": 5.0
                        },
                        "project": None,
                        "resources": []
                    }
                    risk_title = f"Risk {risk_id}"
              # Create AI prompt for recommendations
            prompt = f"""
You are an expert project management consultant. Generate 2-3 practical, actionable recommendations for the following risk:

Risk Context:
{json.dumps(context, indent=2)}

Provide recommendations that are:
1. Specific and actionable
2. Realistic based on the context
3. Include a success probability percentage (0-100)

Respond with valid JSON in this exact format:
{{
    "recommendations": [
        {{
            "title": "Brief recommendation title",
            "description": "Detailed actionable description",
            "success_probability": 85,
            "implementation_effort": "Low|Medium|High",
            "timeframe": "Immediate|Short-term|Medium-term"
        }}
    ]
}}
"""
            
            # Get AI recommendations
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
            
            if not ai_response or 'recommendations' not in ai_response:
                return {"error": "Failed to generate recommendations"}
            
            # Store recommendations in database if we have a risk object
            if risk_obj:
                self._store_risk_recommendations(risk_obj, ai_response['recommendations'])
            
            return {
                "success": True,
                "risk_title": risk_title,
                "recommendations": ai_response['recommendations']
            }
            
        except Exception as e:
            logger.error(f"Error generating risk recommendations: {e}")
            return {"error": f"Failed to generate recommendations: {str(e)}"}
    
    def _store_risk_recommendations(self, risk: 'DynamicRisk', recommendations: List[Dict[str, Any]]) -> None:
        """Store recommendations in the database"""
        try:
            from dashboard.models import AIRecommendation
            
            # Clear any existing recommendations for this risk
            AIRecommendation.objects.filter(related_risk=risk).delete()
            
            # Store new recommendations
            for rec in recommendations:
                AIRecommendation.objects.create(
                    title=rec.get('title', 'Untitled Recommendation'),
                    description=rec.get('description', ''),
                    success_probability=rec.get('success_probability', 75) / 100.0,  # Convert to decimal
                    related_risk=risk,
                    related_project=risk.related_project,
                    recommendation_data=rec,
                    confidence_score=rec.get('success_probability', 75) / 100.0
                )
                
        except Exception as e:
            logger.error(f"Error storing recommendations: {e}")

    def analyze_portfolio_risks(self) -> Dict[str, Any]:
        """Analyze risks across the entire portfolio"""
        try:
            # Get portfolio context
            project_context = self._get_portfolio_context()
            
            # Get comprehensive risks
            risks = self.analyze_comprehensive_risks(project_context)
            
            # Add unique IDs to risks for frontend use
            for i, risk in enumerate(risks):
                risk['id'] = f"risk-{i+1}"
            
            return {
                'risks': risks,
                'summary': self._generate_portfolio_summary(risks),
                'confidence_score': 0.85,
                'created_at': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing portfolio risks: {e}")
            return {
                'risks': [],
                'summary': 'Unable to analyze portfolio risks at this time.',
                'confidence_score': 0.0,
                'created_at': timezone.now().isoformat()
            }
    
    def _get_portfolio_context(self) -> Dict[str, Any]:
        """Get context data for portfolio analysis"""
        try:
            # Get basic project statistics
            projects = Project.objects.all()
            resources = Resource.objects.all()
            tasks = Task.objects.all()
            
            context = {
                'projects': {
                    'total': projects.count(),
                    'active': projects.filter(status='active').count() if hasattr(Project, 'status') else projects.count(),
                },
                'resources': {
                    'total': resources.count(),
                    'available': resources.filter(is_active=True).count() if hasattr(Resource, 'is_active') else resources.count(),
                },
                'tasks': {
                    'total': tasks.count(),
                    'pending': tasks.filter(status='pending').count() if hasattr(Task, 'status') else 0,
                }
            }
            
            return context
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            return {'projects': {'total': 0}, 'resources': {'total': 0}, 'tasks': {'total': 0}}
    
    def _generate_portfolio_summary(self, risks: List[Dict]) -> str:
        """Generate a summary of portfolio risks"""
        if not risks:
            return "No significant risks identified in the current portfolio."
        
        high_priority = len([r for r in risks if r.get('priority') == 'high'])
        total_risks = len(risks)
        
        if high_priority > 0:
            return f"Portfolio analysis identified {total_risks} risks, with {high_priority} requiring immediate attention."
        else:
            return f"Portfolio analysis identified {total_risks} risks with manageable impact levels."
    
# Create instances for import
dashboard_ai_service = DashboardAIService()
nli_service = NaturalLanguageInterfaceService()
enhanced_risk_service = EnhancedRiskAnalysisService()
