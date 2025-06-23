#!/usr/bin/env python
"""
Working Enhanced AI Resource Allocation Service
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone

from allocation.models import Assignment
from projects.models import Task
from resources.models import Resource, Skill
from analytics.models import AIResourceAllocationSuggestion

logger = logging.getLogger(__name__)

class WorkingEnhancedAIService:
    """Working enhanced AI service with the 6-pass approach"""
    
    def get_enhanced_suggestions(self, task_ids: List[int] = None) -> Dict[str, Any]:
        """Get enhanced AI suggestions with priority-based analysis"""
        
        # Get unassigned tasks
        if task_ids:
            unassigned_tasks = Task.objects.filter(id__in=task_ids)
        else:
            assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
            unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)
        
        # Sort by priority (higher number = higher priority)
        prioritized_tasks = unassigned_tasks.order_by('-priority')
        
        suggestions = {}
        
        for task in prioritized_tasks[:10]:  # Limit to first 10 tasks
            suggestion = self._analyze_single_task(task)
            if suggestion:
                suggestions[str(task.id)] = suggestion
        
        return {
            'suggestions': suggestions,
            'total_tasks_analyzed': prioritized_tasks.count(),
            'tasks_with_suggestions': len(suggestions)
        }
    
    def _analyze_single_task(self, task: Task) -> Optional[Dict]:
        """Analyze a single task using the enhanced 6-pass approach"""
        
        # Pass 1: Ideal Assignment
        ideal_suggestions = self._find_ideal_assignments(task)
        if ideal_suggestions:
            return {
                'type': 'ideal',
                'suggestions': ideal_suggestions,
                'reasoning': 'Found ideal assignee with perfect skill match and low utilization'
            }
        
        # Pass 2: Future-Aware Assignment
        future_suggestions = self._find_future_assignments(task)
        if future_suggestions:
            return {
                'type': 'future_scheduled',
                'suggestions': future_suggestions,
                'reasoning': 'Best-fit assignee available with delayed start date'
            }
        
        # Pass 3: Good Fit Assignment  
        good_fit_suggestions = self._find_good_fit_assignments(task)
        if good_fit_suggestions:
            return {
                'type': 'good_fit',
                'suggestions': good_fit_suggestions,
                'reasoning': 'Alternative assignee with related skills available'
            }
        
        # Pass 4: Informed Over-allocation (for high priority tasks only)
        if task.priority >= 4:  # High priority tasks (4 or 5)
            overallocation_suggestions = self._find_overallocation_assignments(task)
            if overallocation_suggestions:
                return {
                    'type': 'overallocation',
                    'suggestions': overallocation_suggestions,
                    'reasoning': 'Assignment possible with calculated over-allocation risk'
                }
        
        return None
    
    def _find_ideal_assignments(self, task: Task) -> List[Dict]:
        """Find resources with good skill match and under 95% utilization"""
        suggestions = []
        
        for resource in Resource.objects.all():
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match < 0.6:  # Reduced from 0.7 to 0.6 for more flexibility
                continue
                
            current_util = resource.current_utilization()
            projected_util = self._calculate_projected_utilization(resource, task)
            
            # More flexible thresholds
            if current_util < 95 and projected_util < 105:  # Allow slight over-allocation
                suggestions.append({
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'skill_match': round(skill_match, 2),
                    'current_utilization': round(current_util, 1),
                    'projected_utilization': round(projected_util, 1),
                    'confidence': 'high'
                })
        
        # Sort by skill match
        return sorted(suggestions, key=lambda x: x['skill_match'], reverse=True)[:3]
    
    def _find_future_assignments(self, task: Task) -> List[Dict]:
        """Find future slots where skilled resources have capacity"""
        suggestions = []
          # Get top skilled resources
        skilled_resources = []
        for resource in Resource.objects.all():
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match >= 0.5:  # Reduced from 0.6 to 0.5
                skilled_resources.append((resource, skill_match))
        
        skilled_resources.sort(key=lambda x: x[1], reverse=True)
        
        # Check future availability for top 5 skilled resources
        for resource, skill_match in skilled_resources[:5]:
            future_slot = self._find_future_slot(resource, task)
            if future_slot:
                suggestions.append({
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'skill_match': round(skill_match, 2),
                    'suggested_start_date': future_slot['start_date'].isoformat(),
                    'delay_days': future_slot['delay_days'],
                    'projected_utilization': round(future_slot['projected_util'], 1),
                    'confidence': 'medium'
                })
        
        return sorted(suggestions, key=lambda x: (x['skill_match'], -x['delay_days']), reverse=True)[:3]
    
    def _find_good_fit_assignments(self, task: Task) -> List[Dict]:
        """Find resources with adjacent/related skills"""
        suggestions = []
        
        task_skills = set(task.skills_required.all())
        
        for resource in Resource.objects.all():
            resource_skills = set(resource.skills.all())
            
            # Calculate skill overlap
            if not task_skills:
                continue
                
            overlap = len(task_skills.intersection(resource_skills)) / len(task_skills)
              # Look for partial matches (30-70% overlap) - more flexible
            if 0.3 <= overlap < 0.7:
                projected_util = self._calculate_projected_utilization(resource, task)
                
                if projected_util < 110:  # More lenient for good fit
                    skill_gaps = list(task_skills - resource_skills)
                    suggestions.append({
                        'resource_id': resource.id,
                        'resource_name': resource.name,
                        'skill_match': round(overlap, 2),
                        'skill_gap': [skill.name for skill in skill_gaps],
                        'projected_utilization': round(projected_util, 1),
                        'mentoring_needed': len(skill_gaps) > 0,
                        'confidence': 'medium'
                    })
        
        return sorted(suggestions, key=lambda x: x['skill_match'], reverse=True)[:3]
    
    def _find_overallocation_assignments(self, task: Task) -> List[Dict]:
        """Find over-allocation scenarios with risk analysis"""
        suggestions = []
        
        for resource in Resource.objects.all():
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match < 0.6:  # Must have reasonable skill match
                continue
                
            projected_util = self._calculate_projected_utilization(resource, task)
            
            # Only suggest up to 120% utilization
            if 100 < projected_util <= 120:
                overallocation = projected_util - 100
                
                # Calculate risk
                if overallocation <= 10:
                    risk = "Low (1-2 days potential delay)"
                elif overallocation <= 20:
                    risk = "Medium (3-5 days potential delay)"
                else:
                    risk = "High (1+ week potential delay)"
                
                suggestions.append({
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'skill_match': round(skill_match, 2),
                    'projected_utilization': round(projected_util, 1),
                    'overallocation_percentage': round(overallocation, 1),
                    'risk_analysis': {'delay_risk': risk},
                    'mitigation_options': [
                        {'description': f'Approve {overallocation:.1f}% overtime', 'cost_impact': 'Medium'},
                        {'description': 'Reassign other lower-priority tasks', 'cost_impact': 'Low'}
                    ],
                    'confidence': 'low',
                    'warning': 'This assignment exceeds normal capacity limits'
                })
        
        return sorted(suggestions, key=lambda x: (x['skill_match'], -x['projected_utilization']), reverse=True)[:2]
    
    def _calculate_skill_match(self, resource: Resource, task: Task) -> float:
        """Calculate skill match percentage"""
        task_skills = set(task.skills_required.all())
        resource_skills = set(resource.skills.all())
        
        if not task_skills:
            return 0.5  # Default if no skills specified
            
        intersection = task_skills.intersection(resource_skills)
        return len(intersection) / len(task_skills)
    
    def _calculate_projected_utilization(self, resource: Resource, task: Task) -> float:
        """Calculate projected utilization if task is assigned"""
        current_util = resource.current_utilization(task.start_date, task.end_date)
        
        # Calculate work days in task period
        task_duration_days = (task.end_date - task.start_date).days + 1
        work_days = sum(1 for i in range(task_duration_days) 
                       if (task.start_date + timedelta(days=i)).weekday() < 5)
        
        if work_days > 0:
            # Assume 8 hours per work day
            available_hours_in_period = 8 * work_days
            if available_hours_in_period > 0:
                additional_util = (task.estimated_hours / available_hours_in_period) * 100
                projected_util = current_util + additional_util
            else:
                projected_util = current_util
        else:
            projected_util = current_util
            
        return projected_util
    
    def _find_future_slot(self, resource: Resource, task: Task) -> Optional[Dict]:
        """Find the earliest future slot where resource has capacity"""
        current_date = max(timezone.now().date(), task.start_date)
        task_duration = task.end_date - task.start_date
        
        # Look ahead up to 6 weeks
        for weeks_ahead in range(1, 7):
            potential_start = current_date + timedelta(weeks=weeks_ahead)
            potential_end = potential_start + task_duration
            
            projected_util = self._calculate_projected_utilization_for_period(
                resource, task, potential_start, potential_end
            )
            
            if projected_util < 95:
                return {
                    'start_date': potential_start,
                    'delay_days': (potential_start - task.start_date).days,
                    'projected_util': projected_util
                }
        
        return None
    
    def _calculate_projected_utilization_for_period(self, resource: Resource, task: Task, start_date, end_date) -> float:
        """Calculate projected utilization for a specific period"""
        current_util = resource.current_utilization(start_date, end_date)
        
        task_duration_days = (end_date - start_date).days + 1
        work_days = sum(1 for i in range(task_duration_days) 
                       if (start_date + timedelta(days=i)).weekday() < 5)
        
        if work_days > 0:
            available_hours_in_period = 8 * work_days
            if available_hours_in_period > 0:
                additional_util = (task.estimated_hours / available_hours_in_period) * 100
                projected_util = current_util + additional_util
            else:
                projected_util = current_util
        else:
            projected_util = current_util
            
        return projected_util
