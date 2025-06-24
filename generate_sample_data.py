#!/usr/bin/env python
"""
Script to generate sample data for forecasting functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.utils import timezone
from resources.models import Resource, Skill
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import ResourceDemandForecast, HistoricalUtilization

def create_sample_assignments():
    """Create sample assignments for the last 60 days"""
    print("Creating sample assignments...")
    
    # Get existing resources and projects
    resources = list(Resource.objects.all())
    projects = list(Project.objects.all())
    
    if not resources:
        print("No resources found. Please create some resources first.")
        return
    
    if not projects:
        print("No projects found. Please create some projects first.")
        return
    
    # Create some tasks if they don't exist
    tasks = list(Task.objects.all())
    if len(tasks) < 5:
        print("Creating sample tasks...")
        for project in projects[:3]:  # Use first 3 projects
            for i in range(3):  # 3 tasks per project
                task, created = Task.objects.get_or_create(
                    name=f"Task {i+1} for {project.name}",
                    project=project,
                    defaults={
                        'description': f"Sample task {i+1} for forecasting demo",
                        'start_date': timezone.now().date() - timedelta(days=30),
                        'end_date': timezone.now().date() + timedelta(days=30),
                        'estimated_hours': Decimal(str(random.randint(20, 100))),
                        'status': random.choice(['not_started', 'in_progress', 'completed'])
                    }
                )
                if created:
                    print(f"  Created task: {task.name}")
        tasks = list(Task.objects.all())
      # Create strategic assignments to avoid unique constraint issues
    assignments_created = 0
    
    # Instead of random assignments per day, create strategic assignments
    # Each resource gets assigned to 2-4 tasks over the period
    for resource in resources:
        # Assign each resource to 2-4 different tasks
        num_tasks = min(random.randint(2, 4), len(tasks))
        assigned_tasks = random.sample(tasks, num_tasks)
        
        for task in assigned_tasks:
            # Check if assignment already exists (unique constraint on resource+task)
            existing = Assignment.objects.filter(
                resource=resource,
                task=task
            ).first()
            
            if not existing:
                # Create assignment with realistic hours based on role
                role_multiplier = {
                    'Senior Developer': 1.2,
                    'Developer': 1.0,
                    'Junior Developer': 0.8,
                    'Project Manager': 0.6,
                    'Designer': 0.9,
                    'QA Engineer': 0.8,
                }.get(resource.role, 1.0)
                allocated_hours = Decimal(str(random.randint(20, 60) * role_multiplier))
                  # Random assignment date within the last 180 days (forecast needs 180 days of data)
                days_ago = random.randint(0, 179)
                assignment_date = timezone.now().date() - timedelta(days=days_ago)
                assignment = Assignment.objects.create(
                    resource=resource,
                    task=task,
                    allocated_hours=int(allocated_hours),
                    notes=f"Sample assignment created for forecasting data"
                )
                
                # Manually update the created_at field to spread data across 180 days
                assignment.created_at = timezone.make_aware(
                    datetime.combine(assignment_date, datetime.min.time())
                )
                assignment.save(update_fields=['created_at'])
                assignments_created += 1
    
    print(f"Created {assignments_created} sample assignments")

def create_sample_utilization_data():
    """Create sample historical utilization data"""
    print("Creating sample utilization data...")
    
    resources = list(Resource.objects.all())
    if not resources:
        print("No resources found. Please create some resources first.")
        return
    
    start_date = timezone.now().date() - timedelta(days=180)
    utilization_records = 0
    
    for days_back in range(180):
        date = start_date + timedelta(days=days_back)
        
        for resource in resources:
            # Check if utilization record already exists
            existing = HistoricalUtilization.objects.filter(
                resource=resource,
                date=date
            ).first()
            
            if not existing:
                # Generate realistic utilization data
                base_utilization = random.uniform(30, 90)
                
                # Add some variation based on role
                if resource.role in ['Senior Developer', 'Project Manager']:
                    base_utilization += random.uniform(0, 15)
                elif resource.role in ['Junior Developer']:
                    base_utilization -= random.uniform(0, 10)
                
                utilization_percentage = min(100, max(0, base_utilization))
                
                # Calculate hours based on 8-hour work day
                available_hours = Decimal('8.0')
                allocated_hours = available_hours * Decimal(str(utilization_percentage / 100))
                
                HistoricalUtilization.objects.create(
                    resource=resource,
                    date=date,
                    utilization_percentage=Decimal(str(round(utilization_percentage, 1))),
                    allocated_hours=allocated_hours,
                    available_hours=available_hours
                )
                utilization_records += 1
    
    print(f"Created {utilization_records} utilization records")

def create_sample_skills_and_assignments():
    """Create sample skills and assign them to resources and tasks"""
    print("Creating sample skills...")
    
    # Create some common skills
    skills_data = [
        'Python', 'JavaScript', 'React', 'Django', 'Node.js',
        'Project Management', 'UI/UX Design', 'Quality Assurance',
        'Database Design', 'DevOps', 'Machine Learning', 'API Development'
    ]
    
    skills = []
    for skill_name in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'description': f'Skill in {skill_name}'}
        )
        skills.append(skill)
        if created:
            print(f"  Created skill: {skill_name}")
      # Assign skills to resources
    from resources.models import ResourceSkill
    resources = list(Resource.objects.all())
    for resource in resources:
        # Each resource gets 2-4 random skills
        num_skills = random.randint(2, 4)
        resource_skills = random.sample(skills, min(num_skills, len(skills)))
        
        for skill in resource_skills:
            # Create ResourceSkill with proficiency level
            proficiency = random.randint(5, 9)  # 5-9 proficiency level
            ResourceSkill.objects.get_or_create(
                resource=resource,
                skill=skill,
                defaults={'proficiency': proficiency}
            )
        
        print(f"  Assigned {len(resource_skills)} skills to {resource.name}")
      # Assign skills to tasks as well
    tasks = list(Task.objects.all())
    for task in tasks:
        # Each task requires 1-3 skills
        num_skills = random.randint(1, 3)
        task_skills = random.sample(skills, min(num_skills, len(skills)))
        
        for skill in task_skills:
            task.skills_required.add(skill)
        
        print(f"  Assigned {len(task_skills)} skills to {task.name}")

def clean_old_forecasts():
    """Clean up old forecast data"""
    print("Cleaning old forecast data...")
    old_forecasts = ResourceDemandForecast.objects.filter(
        forecast_date__lt=timezone.now().date() - timedelta(days=7)
    )
    count = old_forecasts.count()
    old_forecasts.delete()
    print(f"Deleted {count} old forecast records")

def main():
    """Main function to generate all sample data"""
    print("=== Generating Sample Data for Forecasting ===")
    
    try:
        # Clean old data first
        clean_old_forecasts()
        
        # Create sample skills and assign to resources
        create_sample_skills_and_assignments()
        
        # Create sample assignments (required for forecasting)
        create_sample_assignments()
        
        # Create sample utilization data
        create_sample_utilization_data()
        
        print("\n=== Sample Data Generation Complete ===")
        print("You can now try generating forecasts again!")
        
        # Test standard forecast generation
        test_tiered_forecasting()
        
        # Test limited data scenario
        create_limited_data_scenario()
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        import traceback
        traceback.print_exc()

def test_tiered_forecasting():
    """Test different forecasting methods with various data amounts"""
    from analytics.services import PredictiveAnalyticsService
    
    print("\n=== Testing Tiered Forecasting ===")
    
    service = PredictiveAnalyticsService()
    
    # Test with current data
    forecasts = service.generate_resource_demand_forecast(days_ahead=30)
    
    if forecasts:
        if isinstance(forecasts, dict):
            method = forecasts.get('generation_method', 'unknown')
            confidence = forecasts.get('confidence_level', 0)
            data_quality = forecasts.get('data_quality', 'unknown')
            forecast_count = len(forecasts.get('statistical_forecasts', []))
            
            print(f"✅ Generated {forecast_count} forecasts using {method}")
            print(f"   Data Quality: {data_quality}")
            print(f"   Confidence Level: {confidence}/4")
        else:
            print(f"✅ Generated {len(forecasts)} forecasts (legacy format)")
    else:
        print("❌ No forecasts could be generated")

def create_limited_data_scenario():
    """Create a scenario with only 30 days of data to test bootstrap mode"""
    from allocation.models import Assignment
    
    print("\n=== Creating Limited Data Scenario ===")
    
    # Delete most assignments to simulate a new project
    Assignment.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=30)
    ).delete()
    
    remaining = Assignment.objects.count()
    print(f"Reduced to {remaining} recent assignments (last 30 days)")
    
    test_tiered_forecasting()

if __name__ == "__main__":
    main()
