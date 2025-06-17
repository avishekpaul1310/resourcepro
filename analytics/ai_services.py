"""
AI-enhanced services for ResourcePro using Gemini 1.5 Flash
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q

from resources.models import Resource, Skill
from projects.models import Task, Project
from allocation.models import Assignment
from analytics.models import (
    SkillDemandAnalysis, AISkillRecommendation, 
    AIResourceAllocationSuggestion, ResourceDemandForecast,
    AIForecastAdjustment
)
from utils.gemini_ai import gemini_service

logger = logging.getLogger(__name__)

class AISkillRecommendationService:
    """AI-powered skill recommendation engine"""
    
    def generate_skill_recommendations(self, force_refresh: bool = False) -> Dict[str, List[Dict]]:
        """
        Generate AI-powered skill recommendations based on current team skills and project demands
        
        Args:
            force_refresh: If True, regenerate even if recent recommendations exist
            
        Returns:
            Dictionary containing categorized recommendations
        """
        # Check if we have recent recommendations (within last 24 hours)
        if not force_refresh:
            recent_recommendations = AISkillRecommendation.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            )
            if recent_recommendations.exists():
                return self._format_existing_recommendations(recent_recommendations)
        
        if not gemini_service.is_available():
            logger.warning("Gemini AI not available for skill recommendations")
            return {"error": "AI service not available"}
        
        # Gather team skills data
        team_skills_data = self._get_team_skills_data()
        project_requirements_data = self._get_project_requirements_data()
        skill_demand_data = self._get_skill_demand_data()
          # Create prompt for Gemini
        prompt = self._create_skill_recommendation_prompt(
            team_skills_data, project_requirements_data, skill_demand_data
        )
        
        try:
            # Get AI recommendations
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
            
            if not ai_response:
                logger.warning("AI service returned no response")
                return {"error": "Failed to generate AI recommendations"}
            
            # Process and store recommendations
            recommendations = self._process_and_store_recommendations(ai_response)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating skill recommendations: {e}")
            return {"error": f"Failed to generate recommendations: {str(e)}"}
    
    def _get_team_skills_data(self) -> Dict[str, Any]:
        """Gather current team skills data"""
        skills_data = []
        
        for skill in Skill.objects.all():
            resources_with_skill = Resource.objects.filter(skills=skill)
            skill_info = {
                "name": skill.name,
                "description": skill.description or "",
                "total_resources": resources_with_skill.count(),
                "roles": list(set([r.role for r in resources_with_skill])),
                "departments": list(set([r.department for r in resources_with_skill]))
            }
            skills_data.append(skill_info)
        
        return {
            "total_skills": len(skills_data),
            "skills": skills_data,
            "total_resources": Resource.objects.count(),
            "roles": list(set(Resource.objects.values_list('role', flat=True))),
            "departments": list(set(Resource.objects.values_list('department', flat=True)))
        }
    
    def _get_project_requirements_data(self) -> Dict[str, Any]:
        """Gather project requirements and skill demands"""
        active_projects = Project.objects.filter(
            status__in=['planning', 'active']
        )
        
        project_skills = []
        for project in active_projects:
            project_tasks = Task.objects.filter(project=project)
            required_skills = []
            
            for task in project_tasks:
                for skill in task.skills_required.all():
                    required_skills.append({
                        "name": skill.name,
                        "task": task.name,
                        "priority": task.priority,
                        "status": task.status
                    })
            
            if required_skills:
                project_skills.append({
                    "project": project.name,
                    "status": project.status,
                    "start_date": project.start_date.isoformat(),
                    "end_date": project.end_date.isoformat(),
                    "skills_required": required_skills
                })
        
        return {
            "active_projects": len(active_projects),
            "project_requirements": project_skills
        }
    
    def _get_skill_demand_data(self) -> Dict[str, Any]:
        """Get recent skill demand analysis data"""
        recent_analyses = SkillDemandAnalysis.objects.filter(
            analysis_date__gte=timezone.now().date() - timedelta(days=30)
        ).order_by('-analysis_date')
        
        demand_data = []
        for analysis in recent_analyses:
            demand_data.append({
                "skill": analysis.skill_name,
                "current_demand": analysis.current_demand,
                "available_resources": analysis.available_resources,
                "demand_score": float(analysis.demand_score),
                "predicted_future_demand": analysis.predicted_future_demand,
                "analysis_date": analysis.analysis_date.isoformat()
            })
        
        return {"skill_demand_analyses": demand_data}
    
    def _create_skill_recommendation_prompt(self, team_skills: Dict, project_requirements: Dict, skill_demand: Dict) -> str:
        """Create the prompt for Gemini AI"""
        return f"""
You are an expert resource management consultant analyzing a software development team's skills and project requirements.

Current Team Skills Data:
{json.dumps(team_skills, indent=2)}

Project Requirements Data:
{json.dumps(project_requirements, indent=2)}

Skill Demand Analysis:
{json.dumps(skill_demand, indent=2)}

Based on this data, provide strategic skill recommendations in the following categories:

1. SKILLS TO DEVELOP: Top 5 skills the team should prioritize developing (new skills or improving existing ones)
2. TRAINING AREAS: Top 5 specific training areas to address skill gaps in current projects
3. OBSOLETE SKILLS: Top 3 skills that might become less relevant or obsolete in the near future

For each recommendation, provide:
- skill_name: The specific skill name
- priority_score: Integer from 1-10 (10 = highest priority)
- reasoning: Detailed explanation (2-3 sentences)
- confidence_score: Decimal from 0.0-1.0 based on data certainty
- estimated_impact: Brief description of expected business impact

IMPORTANT: If no items exist for a category, return an empty array []. Never use null or None values.

Respond with valid JSON in this exact format:
{{
    "skills_to_develop": [
        {{
            "skill_name": "string",
            "priority_score": integer,
            "reasoning": "string",
            "confidence_score": decimal,
            "estimated_impact": "string"
        }}
    ],
    "training_areas": [
        {{
            "skill_name": "string",
            "priority_score": integer,
            "reasoning": "string",
            "confidence_score": decimal,
            "estimated_impact": "string"
        }}
    ],
    "obsolete_skills": [
        {{
            "skill_name": "string",
            "priority_score": integer,
            "reasoning": "string",
            "confidence_score": decimal,            "estimated_impact": "string"
        }}
    ]
}}
"""
    
    def _process_and_store_recommendations(self, ai_response: Dict) -> Dict[str, List[Dict]]:
        """Process AI response and store recommendations in database"""
        # Clear old recommendations (keep last 30 days)
        old_date = timezone.now().date() - timedelta(days=30)
        AISkillRecommendation.objects.filter(analysis_date__lt=old_date).delete()
        
        recommendations = {
            "skills_to_develop": [],
            "training_areas": [],
            "obsolete_skills": []
        }
          # Process each category
        for category, db_type in [
            ("skills_to_develop", "develop"),
            ("training_areas", "training"),
            ("obsolete_skills", "obsolete")
        ]:
            if category in ai_response:
                for item in ai_response[category]:
                    skill_name = item.get("skill_name") or ""
                    skill_name = skill_name.strip() if skill_name else ""
                    if not skill_name:  # Skip empty skill names
                        continue
                        
                    # Store in database
                    recommendation = AISkillRecommendation.objects.create(
                        recommendation_type=db_type,
                        skill_name=skill_name,
                        priority_score=item.get("priority_score", 5),
                        reasoning=item.get("reasoning", "No reasoning provided"),
                        confidence_score=Decimal(str(item.get("confidence_score", 0.5)))
                    )
                    
                    # Add to response
                    recommendations[category].append({
                        "id": recommendation.id,
                        "skill_name": recommendation.skill_name,
                        "priority_score": recommendation.priority_score,
                        "reasoning": recommendation.reasoning,
                        "confidence_score": float(recommendation.confidence_score),
                        "estimated_impact": item.get("estimated_impact", ""),
                        "created_at": recommendation.created_at.isoformat()
                    })
        
        return recommendations
    
    def _format_existing_recommendations(self, recommendations) -> Dict[str, List[Dict]]:
        """Format existing recommendations from database"""
        result = {
            "skills_to_develop": [],
            "training_areas": [],
            "obsolete_skills": []
        }
        
        type_mapping = {
            "develop": "skills_to_develop",
            "training": "training_areas",
            "obsolete": "obsolete_skills"
        }
        
        for rec in recommendations:
            category = type_mapping.get(rec.recommendation_type)
            if category:
                result[category].append({
                    "id": rec.id,
                    "skill_name": rec.skill_name,
                    "priority_score": rec.priority_score,
                    "reasoning": rec.reasoning,
                    "confidence_score": float(rec.confidence_score),
                    "created_at": rec.created_at.isoformat()
                })
        
        return result

class AIResourceAllocationService:
    """AI-powered resource allocation advisor"""
    
    def suggest_optimal_resource_allocation(self, task_id: int, force_refresh: bool = False) -> Optional[Dict]:
        """
        Generate AI-powered resource allocation suggestions for a specific task
        
        Args:
            task_id: ID of the task to get suggestions for
            force_refresh: If True, regenerate even if recent suggestions exist
            
        Returns:
            Dictionary containing allocation suggestions or None if failed
        """
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return {"error": "Task not found"}
        
        # Check if we have recent suggestions (within last 4 hours)
        if not force_refresh:
            recent_suggestion = AIResourceAllocationSuggestion.objects.filter(
                task=task,
                created_at__gte=timezone.now() - timedelta(hours=4)
            ).first()
            
            if recent_suggestion:
                return self._format_existing_suggestion(recent_suggestion)
        
        if not gemini_service.is_available():
            logger.warning("Gemini AI not available for resource allocation")
            return {"error": "AI service not available"}
        
        # Get available resources (not over-allocated)
        available_resources = self._get_available_resources(task)
        
        if not available_resources:
            return {"error": "No available resources found"}
        
        # Create task data for AI analysis
        task_data = self._prepare_task_data(task)
        resources_data = self._prepare_resources_data(available_resources, task)
        
        # Create prompt for Gemini
        prompt = self._create_allocation_prompt(task_data, resources_data)
        
        try:
            # Get AI recommendations
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.2)
            
            if not ai_response:
                return {"error": "Failed to generate AI recommendations"}
            
            # Process and store the best suggestions
            suggestions = self._process_and_store_allocation_suggestions(task, ai_response, available_resources)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating allocation suggestions: {e}")
            return {"error": "Failed to generate suggestions"}
    
    def _get_available_resources(self, task: Task) -> List[Resource]:
        """Get resources that are available for allocation"""
        # Get resources that are not over-allocated (utilization < 100%)
        available_resources = []
        
        for resource in Resource.objects.all():
            current_utilization = resource.current_utilization(
                task.start_date, task.end_date
            )
            
            # Consider resource available if utilization is less than 90%
            if current_utilization < 90:
                available_resources.append(resource)
        
        return available_resources
    
    def _prepare_task_data(self, task: Task) -> Dict[str, Any]:
        """Prepare task data for AI analysis"""
        return {
            "id": task.id,
            "name": task.name,
            "description": task.description or "",
            "priority": task.priority,
            "status": task.status,
            "estimated_hours": task.estimated_hours,
            "start_date": task.start_date.isoformat(),
            "end_date": task.end_date.isoformat(),
            "project": task.project.name,
            "project_priority": task.project.priority if hasattr(task.project, 'priority') else "medium",
            "required_skills": [
                {"name": skill.name, "description": skill.description or ""}
                for skill in task.skills_required.all()
            ]
        }
    
    def _prepare_resources_data(self, resources: List[Resource], task: Task) -> List[Dict[str, Any]]:
        """Prepare resources data for AI analysis"""
        resources_data = []
        
        for resource in resources:
            # Get resource skills with proficiency if available
            resource_skills = []
            for skill in resource.skills.all():
                skill_info = {"name": skill.name}
                # Try to get proficiency from ResourceSkill through relationship
                try:
                    from resources.models import ResourceSkill
                    resource_skill = ResourceSkill.objects.get(resource=resource, skill=skill)
                    skill_info["proficiency"] = resource_skill.proficiency
                except:
                    skill_info["proficiency"] = 5  # default intermediate level
                
                resource_skills.append(skill_info)
            
            # Calculate current utilization for the task period
            current_utilization = resource.current_utilization(
                task.start_date, task.end_date
            )
            
            resources_data.append({
                "id": resource.id,
                "name": resource.name,
                "role": resource.role,
                "department": resource.department,
                "skills": resource_skills,
                "current_utilization": current_utilization,
                "capacity": resource.capacity,
                "cost_per_hour": float(resource.cost_per_hour),
                "availability_score": max(0, 100 - current_utilization) / 100
            })
        
        return resources_data
    
    def _create_allocation_prompt(self, task_data: Dict, resources_data: List[Dict]) -> str:
        """Create the prompt for Gemini AI"""
        return f"""
You are an expert project manager tasked with optimizing resource allocation for a software development task.

Task Details:
{json.dumps(task_data, indent=2)}

Available Resources:
{json.dumps(resources_data, indent=2)}

Analyze each resource and provide the top 3 recommendations for this task. Consider:

1. SKILL MATCH: How well the resource's skills align with task requirements
2. AVAILABILITY: Resource utilization and capacity
3. COST EFFICIENCY: Balance between skill level and cost
4. EXPERIENCE FIT: Role and department alignment with task needs

For each recommended resource, provide:
- resource_id: The resource ID
- match_score: Decimal 0.0-1.0 (overall suitability)
- reasoning: Detailed explanation (2-3 sentences)
- estimated_completion_time: Hours needed (consider skill match and experience)
- cost_efficiency_score: Decimal 0.0-1.0 (value for money)
- risk_factors: Array of potential risks
- benefits: Array of key benefits

Respond with valid JSON in this exact format:
{{
    "recommendations": [
        {{
            "resource_id": integer,
            "match_score": decimal,
            "reasoning": "string",
            "estimated_completion_time": decimal,
            "cost_efficiency_score": decimal,
            "risk_factors": ["string"],
            "benefits": ["string"]
        }}
    ],
    "analysis_summary": "string"
}}

Sort recommendations by match_score (highest first). Only include resources with match_score >= 0.3.
"""
    
    def _process_and_store_allocation_suggestions(self, task: Task, ai_response: Dict, available_resources: List[Resource]) -> Dict:
        """Process AI response and store allocation suggestions"""
        # Clear old suggestions for this task (keep last 24 hours)
        old_datetime = timezone.now() - timedelta(hours=24)
        AIResourceAllocationSuggestion.objects.filter(
            task=task, 
            created_at__lt=old_datetime
        ).delete()
        
        suggestions = []
        resource_dict = {r.id: r for r in available_resources}
        
        if "recommendations" in ai_response:
            for rec in ai_response["recommendations"]:
                resource_id = rec.get("resource_id")
                if resource_id in resource_dict:
                    resource = resource_dict[resource_id]
                      # Store suggestion in database (handle duplicates)
                    suggestion, created = AIResourceAllocationSuggestion.objects.get_or_create(
                        task=task,
                        suggested_resource=resource,
                        defaults={
                            'match_score': Decimal(str(rec.get("match_score", 0.5))),
                            'reasoning': rec.get("reasoning", ""),
                            'estimated_completion_time': Decimal(str(rec.get("estimated_completion_time", task.estimated_hours))),
                            'cost_efficiency_score': Decimal(str(rec.get("cost_efficiency_score", 0.5)))
                        }
                    )
                    
                    suggestions.append({
                        "id": suggestion.id,
                        "resource": {
                            "id": resource.id,
                            "name": resource.name,
                            "role": resource.role,
                            "department": resource.department,
                            "cost_per_hour": float(resource.cost_per_hour)
                        },
                        "match_score": float(suggestion.match_score),
                        "reasoning": suggestion.reasoning,
                        "estimated_completion_time": float(suggestion.estimated_completion_time),
                        "cost_efficiency_score": float(suggestion.cost_efficiency_score),
                        "risk_factors": rec.get("risk_factors", []),
                        "benefits": rec.get("benefits", []),
                        "created_at": suggestion.created_at.isoformat()
                    })
        
        return {
            "task": {
                "id": task.id,
                "name": task.name,
                "estimated_hours": task.estimated_hours
            },
            "suggestions": suggestions,
            "analysis_summary": ai_response.get("analysis_summary", "AI analysis completed"),
            "generated_at": timezone.now().isoformat()
        }
    
    def _format_existing_suggestion(self, suggestion: AIResourceAllocationSuggestion) -> Dict:
        """Format existing suggestion from database"""
        return {
            "task": {
                "id": suggestion.task.id,
                "name": suggestion.task.name,
                "estimated_hours": suggestion.task.estimated_hours
            },
            "suggestions": [{
                "id": suggestion.id,
                "resource": {
                    "id": suggestion.suggested_resource.id,
                    "name": suggestion.suggested_resource.name,
                    "role": suggestion.suggested_resource.role,
                    "department": suggestion.suggested_resource.department,
                    "cost_per_hour": float(suggestion.suggested_resource.cost_per_hour)
                },
                "match_score": float(suggestion.match_score),
                "reasoning": suggestion.reasoning,
                "estimated_completion_time": float(suggestion.estimated_completion_time),
                "cost_efficiency_score": float(suggestion.cost_efficiency_score),
                "created_at": suggestion.created_at.isoformat()
            }],
            "generated_at": suggestion.created_at.isoformat()
        }

class AIForecastEnhancementService:
    """AI-enhanced resource demand forecasting"""
    
    def enhance_resource_demand_forecast(self, statistical_forecasts: List[ResourceDemandForecast], 
                                       business_context: str = "") -> Dict[str, Any]:
        """
        Enhance statistical forecasts with AI reasoning based on business context
        
        Args:
            statistical_forecasts: List of ResourceDemandForecast objects
            business_context: Business context string (projects, market trends, etc.)
            
        Returns:
            Dictionary containing enhanced forecasts with AI adjustments
        """
        if not statistical_forecasts:
            return {"error": "No statistical forecasts provided"}
        
        if not gemini_service.is_available():
            logger.warning("Gemini AI not available for forecast enhancement")
            return {"error": "AI service not available"}
        
        # Prepare forecast data for AI analysis
        forecast_data = self._prepare_forecast_data(statistical_forecasts)
        
        # Get business context if not provided
        if not business_context:
            business_context = self._gather_business_context()
        
        # Create prompt for Gemini
        prompt = self._create_forecast_enhancement_prompt(forecast_data, business_context)
        
        try:
            # Get AI enhancements
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.3)
            
            if not ai_response:
                return {"error": "Failed to generate AI enhancements"}
            
            # Process and store enhanced forecasts
            enhanced_forecasts = self._process_and_store_forecast_adjustments(
                statistical_forecasts, ai_response
            )
            
            return enhanced_forecasts
            
        except Exception as e:
            logger.error(f"Error enhancing forecasts: {e}")
            return {"error": "Failed to enhance forecasts"}
    
    def generate_strategic_recommendations(self, enhanced_forecasts: Dict) -> Dict[str, Any]:
        """
        Generate strategic hiring and training recommendations based on enhanced forecasts
        """
        if not gemini_service.is_available():
            return {"error": "AI service not available"}
        
        # Prepare data for strategic analysis
        forecast_summary = enhanced_forecasts.get("enhanced_forecasts", [])
        
        if not forecast_summary:
            return {"error": "No forecast data available"}
        
        prompt = self._create_strategic_recommendations_prompt(forecast_summary)
        
        try:
            ai_response = gemini_service.generate_json_response(prompt, temperature=0.4)
            
            if not ai_response:
                return {"error": "Failed to generate strategic recommendations"}
            
            return {
                "strategic_recommendations": ai_response,
                "generated_at": timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating strategic recommendations: {e}")
            return {"error": "Failed to generate recommendations"}
    
    def _prepare_forecast_data(self, forecasts: List[ResourceDemandForecast]) -> List[Dict]:
        """Prepare forecast data for AI analysis"""
        forecast_data = []
        
        for forecast in forecasts:
            forecast_data.append({
                "id": forecast.id,
                "resource_role": forecast.resource_role,
                "predicted_demand_hours": float(forecast.predicted_demand_hours),
                "confidence_score": float(forecast.confidence_score),
                "period_start": forecast.period_start.isoformat(),
                "period_end": forecast.period_end.isoformat(),
                "forecast_date": forecast.forecast_date.isoformat()
            })
        
        return forecast_data
    
    def _gather_business_context(self) -> str:
        """Gather current business context automatically"""
        context_parts = []
        
        # Active projects context
        active_projects = Project.objects.filter(status__in=['planning', 'active'])
        if active_projects.exists():
            context_parts.append(f"Currently {active_projects.count()} active projects")
            
            # High priority projects
            high_priority = active_projects.filter(priority__in=['high', 'critical']).count()
            if high_priority > 0:
                context_parts.append(f"{high_priority} high-priority projects requiring immediate attention")
        
        # Resource utilization context
        overutilized_resources = []
        underutilized_resources = []
        
        for resource in Resource.objects.all():
            utilization = resource.current_utilization()
            if utilization > 95:
                overutilized_resources.append(resource.role)
            elif utilization < 60:
                underutilized_resources.append(resource.role)
        
        if overutilized_resources:
            context_parts.append(f"Overutilized roles: {', '.join(set(overutilized_resources))}")
        
        if underutilized_resources:
            context_parts.append(f"Underutilized roles: {', '.join(set(underutilized_resources))}")
        
        # Skills gap context
        recent_skill_analysis = SkillDemandAnalysis.objects.filter(
            analysis_date__gte=timezone.now().date() - timedelta(days=7)
        ).order_by('-demand_score')[:5]
        
        if recent_skill_analysis.exists():
            high_demand_skills = [s.skill_name for s in recent_skill_analysis if s.demand_score > 2.0]
            if high_demand_skills:
                context_parts.append(f"High-demand skills: {', '.join(high_demand_skills)}")
        
        return ". ".join(context_parts) if context_parts else "Standard business operations"
    
    def _create_forecast_enhancement_prompt(self, forecast_data: List[Dict], business_context: str) -> str:
        """Create prompt for forecast enhancement"""
        return f"""
You are an expert workforce planning consultant analyzing resource demand forecasts for a software development organization.

Statistical Forecasts (Generated by ML):
{json.dumps(forecast_data, indent=2)}

Current Business Context:
{business_context}

Your task is to review these statistical forecasts and provide AI-enhanced adjustments considering:

1. BUSINESS CONTEXT: How current business situation might affect demand
2. MARKET TRENDS: General technology and software development trends
3. SEASONAL PATTERNS: Typical seasonal variations in software projects
4. STRATEGIC INITIATIVES: Potential impact of business growth/changes
5. SKILL EVOLUTION: How skill demands might shift over time

For each forecast, provide:
- original_forecast_id: The original forecast ID
- adjusted_demand_hours: Your adjusted prediction
- adjustment_percentage: Percentage change from original (+/- decimal)
- reasoning: Detailed explanation for the adjustment (2-3 sentences)
- confidence_score: Your confidence in the adjustment (0.0-1.0)
- context_factors: Array of business factors that influenced your decision

Also provide overall insights:
- market_trends_impact: How market trends affect these forecasts
- strategic_recommendations: High-level strategic advice
- risk_factors: Potential risks to consider
- opportunities: Potential opportunities identified

Respond with valid JSON in this exact format:
{{
    "adjusted_forecasts": [
        {{
            "original_forecast_id": integer,
            "adjusted_demand_hours": decimal,
            "adjustment_percentage": decimal,
            "reasoning": "string",
            "confidence_score": decimal,
            "context_factors": ["string"]
        }}
    ],
    "overall_insights": {{
        "market_trends_impact": "string",
        "strategic_recommendations": "string",
        "risk_factors": ["string"],
        "opportunities": ["string"]
    }}
}}
"""
    
    def _create_strategic_recommendations_prompt(self, forecast_summary: List[Dict]) -> str:
        """Create prompt for strategic recommendations"""
        return f"""
You are a strategic workforce planning consultant. Based on these enhanced demand forecasts, provide actionable recommendations for hiring, training, and resource optimization.

Enhanced Forecast Data:
{json.dumps(forecast_summary, indent=2)}

Provide strategic recommendations in these categories:

1. IMMEDIATE HIRING NEEDS (next 1-3 months)
2. TRAINING & DEVELOPMENT priorities
3. RESOURCE OPTIMIZATION opportunities
4. LONG-TERM STRATEGIC PLANNING (6+ months)

For each recommendation category, provide:
- priority_level: "high", "medium", or "low"
- timeline: Expected timeframe for implementation
- specific_actions: Array of specific actionable steps
- expected_roi: Brief description of expected return on investment
- implementation_complexity: "low", "medium", or "high"

Respond with valid JSON in this exact format:
{{
    "immediate_hiring": {{
        "priority_level": "string",
        "timeline": "string",
        "specific_actions": ["string"],
        "expected_roi": "string",
        "implementation_complexity": "string"
    }},
    "training_development": {{
        "priority_level": "string",
        "timeline": "string",
        "specific_actions": ["string"],
        "expected_roi": "string",
        "implementation_complexity": "string"
    }},
    "resource_optimization": {{
        "priority_level": "string",
        "timeline": "string",
        "specific_actions": ["string"],
        "expected_roi": "string",
        "implementation_complexity": "string"
    }},
    "long_term_planning": {{
        "priority_level": "string",
        "timeline": "string",
        "specific_actions": ["string"],
        "expected_roi": "string",
        "implementation_complexity": "string"
    }}
}}
"""
    
    def _process_and_store_forecast_adjustments(self, original_forecasts: List[ResourceDemandForecast], 
                                              ai_response: Dict) -> Dict[str, Any]:
        """Process AI response and store forecast adjustments"""
        enhanced_forecasts = []
        insights = ai_response.get("overall_insights", {})
        
        # Create mapping of original forecasts
        forecast_dict = {f.id: f for f in original_forecasts}
        
        if "adjusted_forecasts" in ai_response:
            for adjustment in ai_response["adjusted_forecasts"]:
                original_id = adjustment.get("original_forecast_id")
                if original_id in forecast_dict:
                    original_forecast = forecast_dict[original_id]
                    
                    # Store adjustment in database
                    ai_adjustment = AIForecastAdjustment.objects.create(
                        original_forecast=original_forecast,
                        adjusted_demand_hours=Decimal(str(adjustment.get("adjusted_demand_hours", 0))),
                        adjustment_percentage=Decimal(str(adjustment.get("adjustment_percentage", 0))),
                        reasoning=adjustment.get("reasoning", ""),
                        business_context_factors=adjustment.get("context_factors", []),
                        confidence_score=Decimal(str(adjustment.get("confidence_score", 0.5)))
                    )
                    
                    enhanced_forecasts.append({
                        "original_forecast": {
                            "id": original_forecast.id,
                            "resource_role": original_forecast.resource_role,
                            "predicted_demand_hours": float(original_forecast.predicted_demand_hours),
                            "confidence_score": float(original_forecast.confidence_score)
                        },
                        "ai_adjustment": {
                            "id": ai_adjustment.id,
                            "adjusted_demand_hours": float(ai_adjustment.adjusted_demand_hours),
                            "adjustment_percentage": float(ai_adjustment.adjustment_percentage),
                            "reasoning": ai_adjustment.reasoning,
                            "context_factors": ai_adjustment.business_context_factors,
                            "confidence_score": float(ai_adjustment.confidence_score)
                        }
                    })
        
        return {
            "enhanced_forecasts": enhanced_forecasts,
            "insights": insights,
            "generated_at": timezone.now().isoformat(),
            "total_forecasts_processed": len(enhanced_forecasts)
        }
