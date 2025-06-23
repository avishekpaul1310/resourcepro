#!/usr/bin/env python
"""
Enhanced AI Resource Allocation Service
Implements dynamic time-based analysis, priority-driven assignments, 
and future-aware scheduling as recommended.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.utils import timezone
from django.db.models import Q
from allocation.models import Assignment
from projects.models import Task
from resources.models import Resource, Skill
from analytics.models import AIResourceAllocationSuggestion

logger = logging.getLogger(__name__)

class EnhancedAIResourceAllocationService:
    """Enhanced AI service with dynamic scheduling and priority-driven assignments"""
    
    def __init__(self):
        self.priority_weights = {
            'critical': 4,
            'high': 3, 
            'medium': 2,
            'low': 1
        }
    
    def get_enhanced_task_suggestions(self, task_ids: List[int] = None) -> Dict[str, Any]:
        """
        Main entry point for enhanced AI suggestions
        Implements the new 6-pass decision-making process
        """
        # Get unassigned tasks, sorted by priority
        if task_ids:
            unassigned_tasks = Task.objects.filter(id__in=task_ids)
        else:
            assigned_task_ids = Assignment.objects.values_list('task_id', flat=True)
            unassigned_tasks = Task.objects.exclude(id__in=assigned_task_ids)
        
        # Sort tasks by priority (critical first)
        prioritized_tasks = self._sort_tasks_by_priority(unassigned_tasks)
        
        suggestions = {}
        for task in prioritized_tasks:
            task_suggestions = self._analyze_task_with_enhanced_logic(task)
            if task_suggestions:
                suggestions[str(task.id)] = task_suggestions
        
        return {
            'suggestions': suggestions,
            'total_tasks_analyzed': len(prioritized_tasks),
            'tasks_with_suggestions': len(suggestions)
        }
    
    def _sort_tasks_by_priority(self, tasks) -> List[Task]:
        """Sort tasks by priority level"""
        def get_priority_weight(task):
            priority = getattr(task, 'priority', 3)  # Default to 3 (medium)
            # Convert integer priority to our weight system (higher int = higher priority)
            return priority
        
        return sorted(tasks, key=get_priority_weight, reverse=True)
    
    def _analyze_task_with_enhanced_logic(self, task: Task) -> Optional[Dict]:
        """
        Implement the 6-pass decision-making process:
        1. Ideal Assignment Pass
        2. Future-Aware Pass  
        3. Flexible & Collaborative Pass
        4. Good Fit Pass
        5. Informed Over-allocation Pass
        """
        
        # Pass 1: Ideal Assignment (under 90% utilization)
        ideal_suggestions = self._ideal_assignment_pass(task)
        if ideal_suggestions:
            return {
                'type': 'ideal',
                'suggestions': ideal_suggestions,
                'reasoning': 'Found ideal assignee with perfect skill match and low utilization'
            }
        
        # Pass 2: Future-Aware Scheduling
        future_suggestions = self._future_aware_pass(task)
        if future_suggestions:
            return {
                'type': 'future_scheduled',
                'suggestions': future_suggestions,
                'reasoning': 'Best-fit assignee available with delayed start date'
            }
        
        # Pass 3: Flexible & Collaborative Assignment
        flexible_suggestions = self._flexible_collaborative_pass(task)
        if flexible_suggestions:
            return {
                'type': 'collaborative',
                'suggestions': flexible_suggestions,
                'reasoning': 'Task can be completed through collaboration or task splitting'
            }
        
        # Pass 4: Good Fit (adjacent skills)
        adjacent_suggestions = self._good_fit_pass(task)
        if adjacent_suggestions:
            return {
                'type': 'good_fit',
                'suggestions': adjacent_suggestions,
                'reasoning': 'Alternative assignee with related skills available'
            }
        
        # Pass 5: Informed Over-allocation
        overallocation_suggestions = self._informed_overallocation_pass(task)
        if overallocation_suggestions:
            return {
                'type': 'overallocation',
                'suggestions': overallocation_suggestions,
                'reasoning': 'Assignment possible with calculated over-allocation risk'
            }
        
        return None
    
    def _ideal_assignment_pass(self, task: Task) -> List[Dict]:
        """Pass 1: Find assignees with perfect skill match and under 90% utilization"""
        suggestions = []
        
        for resource in Resource.objects.all():
            # Check skill match
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match < 0.7:  # Require at least 70% skill match
                continue
            
            # Check current utilization (should be under 90%)
            current_util = resource.current_utilization()
            projected_util = self._calculate_projected_utilization(resource, task)
            
            if current_util < 90 and projected_util < 100:
                suggestions.append({
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'skill_match': skill_match,
                    'current_utilization': current_util,
                    'projected_utilization': projected_util,
                    'start_date': task.start_date.isoformat(),
                    'confidence': 'high'
                })
        
        return sorted(suggestions, key=lambda x: x['skill_match'], reverse=True)[:3]
    
    def _future_aware_pass(self, task: Task) -> List[Dict]:
        """Pass 2: Find future dates when best-fit assignees have capacity"""
        suggestions = []
        
        # Get resources with good skill matches (even if currently overloaded)
        skilled_resources = []
        for resource in Resource.objects.all():
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match >= 0.7:
                skilled_resources.append((resource, skill_match))
        
        # Sort by skill match
        skilled_resources.sort(key=lambda x: x[1], reverse=True)
        
        for resource, skill_match in skilled_resources[:5]:  # Check top 5 matches
            future_slots = self._find_future_capacity_slots(resource, task)
            if future_slots:
                earliest_slot = future_slots[0]
                suggestions.append({
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'skill_match': skill_match,
                    'suggested_start_date': earliest_slot['start_date'].isoformat(),
                    'original_start_date': task.start_date.isoformat(),
                    'delay_days': (earliest_slot['start_date'] - task.start_date).days,
                    'projected_utilization': earliest_slot['projected_utilization'],
                    'confidence': 'medium'
                })
        
        return sorted(suggestions, key=lambda x: (x['skill_match'], -x['delay_days']), reverse=True)[:3]
    
    def _flexible_collaborative_pass(self, task: Task) -> List[Dict]:
        """Pass 3: Analyze task splitting and collaborative assignments"""
        suggestions = []
        
        # Option 1: Split task over time
        if task.estimated_hours > 40:  # Only split large tasks
            split_suggestion = self._analyze_task_splitting(task)
            if split_suggestion:
                suggestions.append(split_suggestion)
        
        # Option 2: Collaborative assignment
        collaborative_suggestion = self._analyze_collaborative_assignment(task)
        if collaborative_suggestion:
            suggestions.append(collaborative_suggestion)
        
        return suggestions
    
    def _good_fit_pass(self, task: Task) -> List[Dict]:
        """Pass 4: Find assignees with adjacent/related skills"""
        suggestions = []
        
        task_skills = set(task.skills_required.all())
        
        for resource in Resource.objects.all():
            resource_skills = set(resource.skills.all())
            
            # Calculate adjacent skill match (related but not perfect)
            adjacent_match = self._calculate_adjacent_skill_match(resource_skills, task_skills)
            
            if 0.4 <= adjacent_match < 0.7:  # Good enough but not perfect
                current_util = resource.current_utilization()
                projected_util = self._calculate_projected_utilization(resource, task)
                
                if projected_util < 95:  # Slightly more lenient for adjacent skills
                    suggestions.append({
                        'resource_id': resource.id,
                        'resource_name': resource.name,
                        'skill_match': adjacent_match,
                        'skill_gap': list(task_skills - resource_skills),
                        'current_utilization': current_util,
                        'projected_utilization': projected_util,
                        'mentoring_needed': True,
                        'confidence': 'medium'
                    })
        
        return sorted(suggestions, key=lambda x: x['skill_match'], reverse=True)[:3]
    
    def _informed_overallocation_pass(self, task: Task) -> List[Dict]:
        """Pass 5: Calculate over-allocation scenarios with risk analysis"""
        suggestions = []
        
        # Only consider this for high/critical priority tasks
        task_priority = getattr(task, 'priority', 'medium').lower()
        if task_priority not in ['high', 'critical']:
            return suggestions
        
        for resource in Resource.objects.all():
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match < 0.6:  # Must have reasonable skill match
                continue
            
            current_util = resource.current_utilization()
            projected_util = self._calculate_projected_utilization(resource, task)
            
            if projected_util <= 120:  # Cap at 120% for safety
                risk_analysis = self._calculate_overallocation_risk(resource, task, projected_util)
                
                suggestions.append({
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'skill_match': skill_match,
                    'current_utilization': current_util,
                    'projected_utilization': projected_util,
                    'overallocation_percentage': projected_util - 100,
                    'risk_analysis': risk_analysis,
                    'mitigation_options': self._suggest_mitigation_options(resource, task),
                    'confidence': 'low',
                    'warning': 'This assignment exceeds normal capacity limits'
                })
        
        return sorted(suggestions, key=lambda x: (x['skill_match'], -x['projected_utilization']), reverse=True)[:2]
    
    def _find_future_capacity_slots(self, resource: Resource, task: Task) -> List[Dict]:
        """Find future time slots where resource has capacity for the task"""
        slots = []
        
        # Look ahead up to 8 weeks
        current_date = max(timezone.now().date(), task.start_date)
        
        for weeks_ahead in range(1, 9):
            potential_start = current_date + timedelta(weeks=weeks_ahead)
            potential_end = potential_start + (task.end_date - task.start_date)
            
            # Calculate utilization for this future period
            future_util = resource.current_utilization(potential_start, potential_end)
            projected_util = self._calculate_projected_utilization_for_period(
                resource, task, potential_start, potential_end
            )
            
            if projected_util < 95:
                slots.append({
                    'start_date': potential_start,
                    'end_date': potential_end,
                    'projected_utilization': projected_util
                })
        
        return slots
    
    def _analyze_task_splitting(self, task: Task) -> Optional[Dict]:
        """Analyze if task can be split into phases"""
        # Simple heuristic: split large tasks into 2-3 phases
        if task.estimated_hours < 40:
            return None
        
        phases = []
        hours_per_phase = task.estimated_hours // 3
        
        for i in range(3):
            phase_start = task.start_date + timedelta(weeks=i*2)
            phase_end = phase_start + timedelta(days=10)
            phases.append({
                'phase': i + 1,
                'hours': hours_per_phase,
                'start_date': phase_start.isoformat(),
                'end_date': phase_end.isoformat()
            })
        
        return {
            'type': 'task_splitting',
            'phases': phases,
            'total_duration_weeks': 6,
            'reasoning': f'Split {task.estimated_hours}h task into manageable phases'
        }
    
    def _analyze_collaborative_assignment(self, task: Task) -> Optional[Dict]:
        """Find multiple resources who can collaborate on the task"""
        available_resources = []
        
        for resource in Resource.objects.all():
            skill_match = self._calculate_skill_match(resource, task)
            if skill_match >= 0.5:
                current_util = resource.current_utilization()
                if current_util < 85:  # More lenient for collaboration
                    available_hours = max(0, (85 - current_util) / 100 * 40)  # Assume 40h/week capacity
                    available_resources.append({
                        'resource': resource,
                        'skill_match': skill_match,
                        'available_hours': available_hours
                    })
        
        if len(available_resources) >= 2:
            # Sort by skill match and take top collaborators
            available_resources.sort(key=lambda x: x['skill_match'], reverse=True)
            top_collaborators = available_resources[:2]
            
            total_available_hours = sum(r['available_hours'] for r in top_collaborators)
            
            if total_available_hours >= task.estimated_hours * 0.8:  # 80% coverage
                return {
                    'type': 'collaborative',
                    'collaborators': [
                        {
                            'resource_id': r['resource'].id,
                            'resource_name': r['resource'].name,
                            'skill_match': r['skill_match'],
                            'available_hours': r['available_hours']
                        } for r in top_collaborators
                    ],
                    'total_available_hours': total_available_hours,
                    'coverage_percentage': (total_available_hours / task.estimated_hours) * 100
                }
        
        return None
    
    def _calculate_skill_match(self, resource: Resource, task: Task) -> float:
        """Calculate how well resource's skills match task requirements"""
        task_skills = set(task.skills_required.all())
        resource_skills = set(resource.skills.all())
        
        if not task_skills:
            return 0.5  # Default match if no skills specified
        
        intersection = task_skills.intersection(resource_skills)
        return len(intersection) / len(task_skills)
    
    def _calculate_adjacent_skill_match(self, resource_skills: set, task_skills: set) -> float:
        """Calculate match including related/adjacent skills"""
        # Define skill adjacencies (could be moved to database)
        skill_adjacencies = {
            'JavaScript': ['TypeScript', 'React', 'Node.js'],
            'Python': ['Django', 'Flask', 'Data Analysis'],
            'AWS': ['Docker', 'DevOps', 'Kubernetes'],
            'UI/UX Design': ['Graphic Design', 'Frontend Development'],
            # Add more as needed
        }
        
        direct_matches = 0
        adjacent_matches = 0
        
        for task_skill in task_skills:
            task_skill_name = task_skill.name
            
            # Check direct match
            if any(rs.name == task_skill_name for rs in resource_skills):
                direct_matches += 1
            else:
                # Check adjacent skills
                adjacent_skills = skill_adjacencies.get(task_skill_name, [])
                if any(rs.name in adjacent_skills for rs in resource_skills):
                    adjacent_matches += 0.5
        
        total_matches = direct_matches + adjacent_matches
        return total_matches / len(task_skills) if task_skills else 0
    
    def _calculate_projected_utilization(self, resource: Resource, task: Task) -> float:
        """Calculate projected utilization if task is assigned"""
        current_util = resource.current_utilization(task.start_date, task.end_date)
        
        # Calculate task duration in work days
        task_duration_days = (task.end_date - task.start_date).days + 1
        work_days = sum(1 for i in range(task_duration_days) 
                       if (task.start_date + timedelta(days=i)).weekday() < 5)
        
        if work_days > 0:
            # Assume 8 hours per work day capacity
            available_hours_in_period = 8 * work_days
            if available_hours_in_period > 0:
                additional_util = (task.estimated_hours / available_hours_in_period) * 100
                projected_util = current_util + additional_util
            else:
                projected_util = current_util
        else:
            projected_util = current_util
            
        return round(projected_util, 1)
    
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
            
        return round(projected_util, 1)
    
    def _calculate_overallocation_risk(self, resource: Resource, task: Task, projected_util: float) -> Dict:
        """Calculate risks associated with over-allocating a resource"""
        overallocation = projected_util - 100
        
        # Get other tasks this resource is assigned to
        current_assignments = Assignment.objects.filter(resource=resource)
        affected_tasks = []
        
        for assignment in current_assignments:
            if assignment.task.end_date > task.start_date:  # Overlapping tasks
                affected_tasks.append({
                    'task_name': assignment.task.name,
                    'project': assignment.task.project.name if assignment.task.project else 'No Project',
                    'deadline': assignment.task.end_date.isoformat()
                })
        
        # Estimate delay risk
        if overallocation <= 10:
            delay_risk = 'Low (1-2 days potential delay)'
        elif overallocation <= 20:
            delay_risk = 'Medium (3-5 days potential delay)'
        else:
            delay_risk = 'High (1+ week potential delay)'
        
        return {
            'overallocation_percentage': overallocation,
            'delay_risk': delay_risk,
            'affected_tasks': affected_tasks,
            'overtime_hours_needed': max(0, overallocation / 100 * 40)  # Assuming 40h/week
        }
    
    def _suggest_mitigation_options(self, resource: Resource, task: Task) -> List[Dict]:
        """Suggest ways to mitigate over-allocation"""
        options = []
        
        # Option 1: Overtime
        overtime_hours = self._calculate_overallocation_risk(resource, task, 
                                                           self._calculate_projected_utilization(resource, task))['overtime_hours_needed']
        options.append({
            'type': 'overtime',
            'description': f'Approve {overtime_hours:.1f} hours of overtime',
            'cost_impact': 'Medium'
        })
        
        # Option 2: Reassign other tasks
        current_assignments = Assignment.objects.filter(resource=resource)
        if current_assignments.exists():
            options.append({
                'type': 'reassignment',
                'description': f'Reassign some of {resource.name}\'s current tasks to other team members',
                'cost_impact': 'Low',
                'affected_tasks': [a.task.name for a in current_assignments[:2]]
            })
        
        # Option 3: Accept delay
        options.append({
            'type': 'accept_delay',
            'description': 'Accept potential delays to other projects',
            'cost_impact': 'High'
        })
        
        return options
