#!/usr/bin/env python
"""
Script to add realistic skill requirements to tasks for better AI testing
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from projects.models import Task
from resources.models import Skill

def add_skills_to_tasks():
    """Add realistic skill requirements to tasks"""
    
    # Get skills
    skills = {skill.name: skill for skill in Skill.objects.all()}
    print(f"Available skills: {list(skills.keys())}")
    
    # Define skill mappings for different task types
    skill_mappings = {
        'frontend': ['JavaScript', 'HTML/CSS', 'React'],
        'backend': ['Python', 'Django', 'SQL'],
        'design': ['HTML/CSS', 'UI/UX'],
        'deployment': ['DevOps', 'System Administration'],
        'testing': ['Python', 'Testing'],
        'bug': ['Python', 'Django', 'SQL'],
        'api': ['Python', 'Django', 'REST APIs'],
        'database': ['SQL', 'Database Design'],
        'ml': ['Machine Learning', 'Python'],
        'pm': ['Project Management']
    }
    
    tasks_updated = 0
    
    for task in Task.objects.all():
        task_name_lower = task.name.lower()
        task_description_lower = (task.description or '').lower()
        
        # Determine what skills this task might need
        required_skills = []
        
        if any(word in task_name_lower for word in ['frontend', 'ui', 'ux', 'interface']):
            required_skills.extend(['JavaScript', 'HTML/CSS'])
        
        if any(word in task_name_lower for word in ['backend', 'api', 'server']):
            required_skills.extend(['Python', 'Django'])
        
        if any(word in task_name_lower for word in ['database', 'sql', 'data']):
            required_skills.extend(['SQL'])
        
        if any(word in task_name_lower for word in ['deploy', 'infrastructure']):
            required_skills.extend(['DevOps'])
        
        if any(word in task_name_lower for word in ['test', 'bug', 'fix']):
            required_skills.extend(['Python', 'Testing'])
        
        if any(word in task_name_lower for word in ['design', 'ui', 'ux']):
            required_skills.extend(['HTML/CSS'])
        
        if any(word in task_name_lower for word in ['machine learning', 'ml', 'ai']):
            required_skills.extend(['Machine Learning', 'Python'])
        
        # If no specific skills found, add some general ones
        if not required_skills:
            required_skills = ['Python']  # Default skill
        
        # Add the skills to the task
        skills_added = []
        for skill_name in required_skills:
            if skill_name in skills:
                skill_obj = skills[skill_name]
                if not task.skills_required.filter(id=skill_obj.id).exists():
                    task.skills_required.add(skill_obj)
                    skills_added.append(skill_name)
        
        if skills_added:
            print(f"✅ {task.name}: Added skills {skills_added}")
            tasks_updated += 1
        else:
            existing_skills = [s.name for s in task.skills_required.all()]
            print(f"ℹ️  {task.name}: Already has skills {existing_skills}")
    
    print(f"\nUpdated {tasks_updated} tasks with skill requirements")

if __name__ == "__main__":
    add_skills_to_tasks()
