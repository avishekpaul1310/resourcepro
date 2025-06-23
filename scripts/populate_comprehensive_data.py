#!/usr/bin/env python
"""
Comprehensive Test Data Population Script
Deletes all existing sample data and repopulates with diverse, comprehensive test data
for manual testing of all app features.
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
from random import choice, randint, random, sample
from decimal import Decimal

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from resources.models import Resource, Skill, ResourceSkill, ResourceAvailability, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment

def clear_all_data():
    """Clear all existing sample data from the database"""
    print("🧹 Clearing ALL existing data...")
    print("="*60)
    
    # Clear in reverse dependency order to avoid foreign key constraints
    TimeEntry.objects.all().delete()
    print("✅ Cleared TimeEntry data")
    
    Assignment.objects.all().delete()
    print("✅ Cleared Assignment data")
    
    ResourceAvailability.objects.all().delete()
    print("✅ Cleared ResourceAvailability data")
    
    ResourceSkill.objects.all().delete()
    print("✅ Cleared ResourceSkill data")
    
    Task.objects.all().delete()
    print("✅ Cleared Task data")
    
    Project.objects.all().delete()
    print("✅ Cleared Project data")
    
    Resource.objects.all().delete()
    print("✅ Cleared Resource data")
    
    Skill.objects.all().delete()
    print("✅ Cleared Skill data")
    
    UserProfile.objects.all().delete()
    print("✅ Cleared UserProfile data")
    
    # Clear users except superusers
    User.objects.filter(is_superuser=False).delete()
    print("✅ Cleared non-superuser data")
    
    print("🎉 All existing data cleared successfully!")
    print()

def create_skills():
    """Create diverse skill categories"""
    print("🛠️ Creating Skills...")
    
    skills_data = [
        # Technical Skills
        {"name": "Python", "description": "Python programming language"},
        {"name": "JavaScript", "description": "JavaScript development"},
        {"name": "React", "description": "React.js framework"},
        {"name": "Django", "description": "Django web framework"},
        {"name": "Node.js", "description": "Node.js runtime"},
        {"name": "SQL", "description": "Database query language"},
        {"name": "MongoDB", "description": "NoSQL database"},
        {"name": "Docker", "description": "Containerization platform"},
        {"name": "Kubernetes", "description": "Container orchestration"},
        {"name": "AWS", "description": "Amazon Web Services"},
        {"name": "Azure", "description": "Microsoft Azure cloud"},
        {"name": "DevOps", "description": "Development and Operations"},
        {"name": "Machine Learning", "description": "AI and ML algorithms"},
        {"name": "Data Analysis", "description": "Data analysis and visualization"},
        {"name": "Cybersecurity", "description": "Information security"},
        {"name": "Mobile Development", "description": "iOS/Android development"},
        {"name": "UI/UX Design", "description": "User interface and experience design"},
        {"name": "QA Testing", "description": "Quality assurance testing"},
        
        # Business Skills
        {"name": "Project Management", "description": "Project planning and execution"},
        {"name": "Agile/Scrum", "description": "Agile development methodologies"},
        {"name": "Business Analysis", "description": "Business requirements analysis"},
        {"name": "Technical Writing", "description": "Documentation and technical communication"},
        {"name": "Client Relations", "description": "Customer relationship management"},
        {"name": "Team Leadership", "description": "Team management and leadership"},
        {"name": "Strategic Planning", "description": "Business strategy development"},
        {"name": "Financial Analysis", "description": "Financial modeling and analysis"},
        {"name": "Marketing", "description": "Digital marketing and promotion"},
        {"name": "Sales", "description": "Sales and business development"},
    ]
    
    skills = []
    for skill_data in skills_data:
        skill = Skill.objects.create(**skill_data)
        skills.append(skill)
        
    print(f"✅ Created {len(skills)} skills")
    return skills

def create_users_and_resources(skills):
    """Create diverse users and resources"""
    print("👥 Creating Users and Resources...")
    
    # Define resource data with diverse roles, departments, and locations
    resources_data = [
        # Development Team
        {"name": "Alice Johnson", "role": "Senior Full-Stack Developer", "department": "Engineering", 
         "capacity": 40, "cost_per_hour": 85, "timezone": "America/New_York", "location": "New York, USA",
         "skills": ["Python", "React", "Django", "SQL", "AWS"], "proficiencies": [9, 8, 9, 7, 6]},
        
        {"name": "Bob Chen", "role": "Frontend Developer", "department": "Engineering", 
         "capacity": 40, "cost_per_hour": 70, "timezone": "America/Los_Angeles", "location": "San Francisco, USA",
         "skills": ["JavaScript", "React", "UI/UX Design", "Mobile Development"], "proficiencies": [9, 9, 7, 6]},
        
        {"name": "Carol Smith", "role": "Backend Developer", "department": "Engineering", 
         "capacity": 40, "cost_per_hour": 75, "timezone": "Europe/London", "location": "London, UK",
         "skills": ["Python", "Django", "SQL", "MongoDB", "Docker"], "proficiencies": [8, 8, 9, 7, 6]},
        
        {"name": "David Rodriguez", "role": "DevOps Engineer", "department": "Engineering", 
         "capacity": 40, "cost_per_hour": 90, "timezone": "Europe/Madrid", "location": "Madrid, Spain",
         "skills": ["Docker", "Kubernetes", "AWS", "DevOps", "Cybersecurity"], "proficiencies": [9, 8, 9, 9, 7]},
        
        {"name": "Emma Wilson", "role": "Mobile Developer", "department": "Engineering", 
         "capacity": 32, "cost_per_hour": 80, "timezone": "Australia/Sydney", "location": "Sydney, Australia",
         "skills": ["Mobile Development", "JavaScript", "React", "UI/UX Design"], "proficiencies": [9, 8, 7, 8]},
        
        # Data & AI Team
        {"name": "Frank Kumar", "role": "Data Scientist", "department": "Data & AI", 
         "capacity": 40, "cost_per_hour": 95, "timezone": "Asia/Kolkata", "location": "Bangalore, India",
         "skills": ["Machine Learning", "Python", "Data Analysis", "SQL"], "proficiencies": [9, 9, 9, 8]},
        
        {"name": "Grace Lee", "role": "ML Engineer", "department": "Data & AI", 
         "capacity": 40, "cost_per_hour": 85, "timezone": "Asia/Seoul", "location": "Seoul, South Korea",
         "skills": ["Machine Learning", "Python", "AWS", "Docker"], "proficiencies": [8, 9, 7, 6]},
        
        # Design Team
        {"name": "Henry Taylor", "role": "Senior UX Designer", "department": "Design", 
         "capacity": 40, "cost_per_hour": 75, "timezone": "America/New_York", "location": "New York, USA",
         "skills": ["UI/UX Design", "Technical Writing", "Client Relations"], "proficiencies": [9, 7, 8]},
        
        {"name": "Ivy Chen", "role": "UI Designer", "department": "Design", 
         "capacity": 35, "cost_per_hour": 65, "timezone": "America/Los_Angeles", "location": "Remote",
         "skills": ["UI/UX Design", "JavaScript", "React"], "proficiencies": [8, 6, 5]},
        
        # QA Team
        {"name": "Jack Brown", "role": "QA Lead", "department": "Quality Assurance", 
         "capacity": 40, "cost_per_hour": 70, "timezone": "America/Chicago", "location": "Chicago, USA",
         "skills": ["QA Testing", "Python", "Agile/Scrum", "Project Management"], "proficiencies": [9, 6, 8, 7]},
        
        {"name": "Kate Davis", "role": "QA Engineer", "department": "Quality Assurance", 
         "capacity": 40, "cost_per_hour": 60, "timezone": "Europe/Berlin", "location": "Berlin, Germany",
         "skills": ["QA Testing", "JavaScript", "SQL"], "proficiencies": [8, 7, 6]},
        
        # Management & Business
        {"name": "Liam Johnson", "role": "Project Manager", "department": "Management", 
         "capacity": 40, "cost_per_hour": 80, "timezone": "America/New_York", "location": "New York, USA",
         "skills": ["Project Management", "Agile/Scrum", "Business Analysis", "Team Leadership"], "proficiencies": [9, 9, 8, 8]},
        
        {"name": "Maya Patel", "role": "Business Analyst", "department": "Business", 
         "capacity": 40, "cost_per_hour": 70, "timezone": "Asia/Kolkata", "location": "Mumbai, India",
         "skills": ["Business Analysis", "Financial Analysis", "SQL", "Technical Writing"], "proficiencies": [9, 8, 7, 8]},
        
        {"name": "Noah Williams", "role": "Technical Lead", "department": "Engineering", 
         "capacity": 35, "cost_per_hour": 100, "timezone": "America/Los_Angeles", "location": "Seattle, USA",
         "skills": ["Team Leadership", "Python", "AWS", "Project Management", "Strategic Planning"], "proficiencies": [9, 9, 8, 8, 7]},
        
        # Part-time and Contractor Resources
        {"name": "Olivia Martinez", "role": "Marketing Specialist", "department": "Marketing", 
         "capacity": 20, "cost_per_hour": 50, "timezone": "America/Mexico_City", "location": "Mexico City, Mexico",
         "skills": ["Marketing", "Technical Writing", "Client Relations"], "proficiencies": [8, 7, 9]},
        
        {"name": "Paul Anderson", "role": "Security Consultant", "department": "Security", 
         "capacity": 25, "cost_per_hour": 120, "timezone": "Europe/Zurich", "location": "Zurich, Switzerland",
         "skills": ["Cybersecurity", "DevOps", "AWS", "Technical Writing"], "proficiencies": [9, 7, 8, 8]},
    ]
    
    resources = []
    all_skills = {skill.name: skill for skill in skills}
    
    for i, resource_data in enumerate(resources_data):
        # Create user
        username = resource_data["name"].lower().replace(" ", ".")
        user = User.objects.create_user(
            username=username,
            email=f"{username}@resourcepro.com",
            first_name=resource_data["name"].split()[0],
            last_name=" ".join(resource_data["name"].split()[1:]),
            password="password123"
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=resource_data["role"],
            department=resource_data["department"]
        )
        
        # Create resource
        colors = ["#4F46E5", "#7C3AED", "#DC2626", "#059669", "#D97706", "#0891B2", "#BE185D", "#7C2D12"]
        resource = Resource.objects.create(
            user=user,
            name=resource_data["name"],
            role=resource_data["role"],
            department=resource_data["department"],
            capacity=resource_data["capacity"],
            cost_per_hour=Decimal(str(resource_data["cost_per_hour"])),
            timezone=resource_data["timezone"],
            location=resource_data["location"],
            color=colors[i % len(colors)]
        )
        
        # Add skills with proficiencies
        for skill_name, proficiency in zip(resource_data["skills"], resource_data["proficiencies"]):
            if skill_name in all_skills:
                ResourceSkill.objects.create(
                    resource=resource,
                    skill=all_skills[skill_name],
                    proficiency=proficiency
                )
        
        resources.append(resource)
    
    print(f"✅ Created {len(resources)} users and resources")
    return resources

def create_projects(resources, skills):
    """Create diverse projects with different statuses and complexities"""
    print("📁 Creating Projects...")
    
    projects_data = [
        {
            "name": "E-commerce Platform Redesign",
            "description": "Complete redesign of the company's e-commerce platform with modern UI/UX",
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today() + timedelta(days=60),
            "status": "active",
            "priority": 5,
            "budget": Decimal("150000.00"),
            "color": "#4F46E5"
        },
        {
            "name": "Mobile App Development",
            "description": "Native mobile application for iOS and Android platforms",
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=120),
            "status": "planning",
            "priority": 4,
            "budget": Decimal("200000.00"),
            "color": "#7C3AED"
        },
        {
            "name": "Data Analytics Dashboard",
            "description": "Real-time analytics dashboard for business intelligence",
            "start_date": date.today() - timedelta(days=45),
            "end_date": date.today() + timedelta(days=15),
            "status": "active",
            "priority": 3,
            "budget": Decimal("80000.00"),
            "color": "#059669"
        },
        {
            "name": "Security Audit & Compliance",
            "description": "Comprehensive security audit and compliance implementation",
            "start_date": date.today() + timedelta(days=20),
            "end_date": date.today() + timedelta(days=90),
            "status": "planning",
            "priority": 5,
            "budget": Decimal("120000.00"),
            "color": "#DC2626"
        },
        {
            "name": "Legacy System Migration",
            "description": "Migration of legacy systems to cloud infrastructure",
            "start_date": date.today() - timedelta(days=90),
            "end_date": date.today() - timedelta(days=10),
            "status": "completed",
            "priority": 4,
            "budget": Decimal("300000.00"),
            "color": "#D97706"
        },
        {
            "name": "AI Chatbot Integration",
            "description": "Integrate AI-powered chatbot for customer support",
            "start_date": date.today() + timedelta(days=5),
            "end_date": date.today() + timedelta(days=75),
            "status": "planning",
            "priority": 3,
            "budget": Decimal("100000.00"),
            "color": "#0891B2"
        },
        {
            "name": "Performance Optimization",
            "description": "Application performance optimization and monitoring",
            "start_date": date.today() - timedelta(days=15),
            "end_date": date.today() + timedelta(days=30),
            "status": "active",
            "priority": 2,
            "budget": Decimal("60000.00"),
            "color": "#BE185D"
        },
        {
            "name": "Marketing Website Revamp",
            "description": "Complete redesign of marketing website with SEO optimization",
            "start_date": date.today() + timedelta(days=30),
            "end_date": date.today() + timedelta(days=100),
            "status": "planning",
            "priority": 2,
            "budget": Decimal("45000.00"),
            "color": "#7C2D12"
        }
    ]
    
    projects = []
    managers = [r for r in resources if "Manager" in r.role or "Lead" in r.role]
    
    for project_data in projects_data:
        project = Project.objects.create(
            name=project_data["name"],
            description=project_data["description"],
            start_date=project_data["start_date"],
            end_date=project_data["end_date"],
            status=project_data["status"],
            priority=project_data["priority"],
            budget=project_data["budget"],
            color=project_data["color"],
            manager=choice(managers).user if managers else None
        )
        projects.append(project)
    
    print(f"✅ Created {len(projects)} projects")
    return projects

def create_tasks(projects, skills):
    """Create diverse tasks for each project"""
    print("📋 Creating Tasks...")
    
    tasks_created = 0
    all_skills = list(skills)
    
    # Task templates for different project types
    task_templates = {
        "E-commerce Platform Redesign": [
            {"name": "User Research & Analysis", "estimated_hours": 80, "skills": ["UI/UX Design", "Business Analysis"], "completion": 100},
            {"name": "Database Schema Design", "estimated_hours": 60, "skills": ["SQL", "Python"], "completion": 100},
            {"name": "Frontend Development", "estimated_hours": 200, "skills": ["React", "JavaScript", "UI/UX Design"], "completion": 75},
            {"name": "Backend API Development", "estimated_hours": 180, "skills": ["Python", "Django", "SQL"], "completion": 60},
            {"name": "Payment Integration", "estimated_hours": 120, "skills": ["Python", "JavaScript", "Cybersecurity"], "completion": 30},
            {"name": "QA Testing", "estimated_hours": 100, "skills": ["QA Testing", "JavaScript"], "completion": 20},
            {"name": "Deployment & DevOps", "estimated_hours": 80, "skills": ["DevOps", "AWS", "Docker"], "completion": 0},
        ],
        "Mobile App Development": [
            {"name": "App Architecture Planning", "estimated_hours": 60, "skills": ["Mobile Development", "Project Management"], "completion": 0},
            {"name": "iOS Development", "estimated_hours": 250, "skills": ["Mobile Development", "UI/UX Design"], "completion": 0},
            {"name": "Android Development", "estimated_hours": 250, "skills": ["Mobile Development", "UI/UX Design"], "completion": 0},
            {"name": "Backend Services", "estimated_hours": 150, "skills": ["Python", "Django", "AWS"], "completion": 0},
            {"name": "App Store Deployment", "estimated_hours": 40, "skills": ["Mobile Development", "DevOps"], "completion": 0},
        ],
        "Data Analytics Dashboard": [
            {"name": "Data Pipeline Setup", "estimated_hours": 100, "skills": ["Python", "SQL", "Data Analysis"], "completion": 90},
            {"name": "Dashboard Frontend", "estimated_hours": 120, "skills": ["React", "JavaScript", "UI/UX Design"], "completion": 80},
            {"name": "Real-time Data Integration", "estimated_hours": 80, "skills": ["Python", "MongoDB", "AWS"], "completion": 70},
            {"name": "Performance Optimization", "estimated_hours": 60, "skills": ["SQL", "Python", "DevOps"], "completion": 40},
            {"name": "User Testing", "estimated_hours": 40, "skills": ["QA Testing", "UI/UX Design"], "completion": 20},
        ],
        "Security Audit & Compliance": [
            {"name": "Security Assessment", "estimated_hours": 80, "skills": ["Cybersecurity", "Technical Writing"], "completion": 0},
            {"name": "Vulnerability Testing", "estimated_hours": 100, "skills": ["Cybersecurity", "QA Testing"], "completion": 0},
            {"name": "Compliance Documentation", "estimated_hours": 60, "skills": ["Technical Writing", "Business Analysis"], "completion": 0},
            {"name": "Security Implementation", "estimated_hours": 120, "skills": ["Cybersecurity", "DevOps", "AWS"], "completion": 0},
        ],
        "Legacy System Migration": [
            {"name": "System Analysis", "estimated_hours": 80, "skills": ["Business Analysis", "SQL"], "completion": 100},
            {"name": "Cloud Architecture Design", "estimated_hours": 100, "skills": ["AWS", "DevOps", "Strategic Planning"], "completion": 100},
            {"name": "Data Migration", "estimated_hours": 150, "skills": ["SQL", "Python", "AWS"], "completion": 100},
            {"name": "Application Migration", "estimated_hours": 200, "skills": ["Python", "Docker", "Kubernetes"], "completion": 100},
            {"name": "Testing & Validation", "estimated_hours": 120, "skills": ["QA Testing", "SQL"], "completion": 100},
            {"name": "Go-Live Support", "estimated_hours": 80, "skills": ["DevOps", "Project Management"], "completion": 100},
        ],
        "AI Chatbot Integration": [
            {"name": "AI Model Research", "estimated_hours": 60, "skills": ["Machine Learning", "Python"], "completion": 0},
            {"name": "Chatbot Development", "estimated_hours": 140, "skills": ["Machine Learning", "Python", "JavaScript"], "completion": 0},
            {"name": "Integration Development", "estimated_hours": 80, "skills": ["Python", "React", "AWS"], "completion": 0},
            {"name": "Training Data Preparation", "estimated_hours": 100, "skills": ["Data Analysis", "Machine Learning"], "completion": 0},
        ],
        "Performance Optimization": [
            {"name": "Performance Analysis", "estimated_hours": 60, "skills": ["Python", "SQL", "Data Analysis"], "completion": 80},
            {"name": "Database Optimization", "estimated_hours": 80, "skills": ["SQL", "MongoDB", "Python"], "completion": 60},
            {"name": "Frontend Optimization", "estimated_hours": 70, "skills": ["JavaScript", "React"], "completion": 40},
            {"name": "Infrastructure Tuning", "estimated_hours": 90, "skills": ["DevOps", "AWS", "Docker"], "completion": 30},
        ],
        "Marketing Website Revamp": [
            {"name": "Brand Design", "estimated_hours": 80, "skills": ["UI/UX Design", "Marketing"], "completion": 0},
            {"name": "Content Strategy", "estimated_hours": 60, "skills": ["Marketing", "Technical Writing"], "completion": 0},
            {"name": "Frontend Development", "estimated_hours": 120, "skills": ["React", "JavaScript", "UI/UX Design"], "completion": 0},
            {"name": "SEO Implementation", "estimated_hours": 40, "skills": ["Marketing", "JavaScript"], "completion": 0},
        ]
    }
    
    skill_map = {skill.name: skill for skill in skills}
    
    for project in projects:
        if project.name in task_templates:
            template_tasks = task_templates[project.name]
        else:
            # Generate generic tasks for projects not in templates
            template_tasks = [
                {"name": "Planning & Analysis", "estimated_hours": 60, "skills": sample([s.name for s in all_skills], 2), "completion": randint(0, 100)},
                {"name": "Development Phase 1", "estimated_hours": 120, "skills": sample([s.name for s in all_skills], 3), "completion": randint(0, 100)},
                {"name": "Development Phase 2", "estimated_hours": 100, "skills": sample([s.name for s in all_skills], 2), "completion": randint(0, 100)},
                {"name": "Testing & QA", "estimated_hours": 80, "skills": ["QA Testing"], "completion": randint(0, 80)},
                {"name": "Deployment", "estimated_hours": 40, "skills": ["DevOps"], "completion": randint(0, 60)},
            ]
        
        # Calculate task dates within project timeline
        project_duration = (project.end_date - project.start_date).days
        task_duration = max(1, project_duration // len(template_tasks))
        
        for i, task_data in enumerate(template_tasks):
            start_offset = timedelta(days=i * task_duration)
            end_offset = timedelta(days=(i + 1) * task_duration - 1)
            
            task_start = project.start_date + start_offset
            task_end = min(project.start_date + end_offset, project.end_date)
            
            # Determine task status based on project status and completion
            if project.status == "completed":
                task_status = "completed"
            elif project.status == "planning":
                task_status = "not_started"
            else:  # active
                if task_data["completion"] == 100:
                    task_status = "completed"
                elif task_data["completion"] > 0:
                    task_status = "in_progress"
                else:
                    task_status = "not_started"
            
            task = Task.objects.create(
                project=project,
                name=task_data["name"],
                description=f"Task for {project.name}: {task_data['name']}",
                start_date=task_start,
                end_date=task_end,
                estimated_hours=task_data["estimated_hours"],
                status=task_status,
                completion_percentage=task_data["completion"],
                priority=randint(1, 5)
            )
            
            # Add required skills
            for skill_name in task_data["skills"]:
                if skill_name in skill_map:
                    task.skills_required.add(skill_map[skill_name])
            
            tasks_created += 1
    
    print(f"✅ Created {tasks_created} tasks")
    return Task.objects.all()

def create_assignments(resources, tasks):
    """Create resource assignments to tasks"""
    print("👤 Creating Assignments...")
    
    assignments_created = 0
    
    for task in tasks:
        # Skip completed tasks from legacy projects for assignment
        if task.status == "completed" and task.project.status == "completed":
            continue
            
        # Get required skills for this task
        required_skills = list(task.skills_required.all())
        
        if not required_skills:
            # If no required skills, assign random resources
            suitable_resources = list(resources)[:3]
        else:
            # Find resources with matching skills
            suitable_resources = []
            for resource in resources:
                resource_skills = [rs.skill for rs in resource.resource_skills.all()]
                if any(skill in resource_skills for skill in required_skills):
                    suitable_resources.append(resource)
            
            # If no perfect match, get resources with highest skill overlap
            if not suitable_resources:
                suitable_resources = list(resources)[:5]
        
        # Assign 1-3 resources per task based on complexity
        num_assignments = min(len(suitable_resources), randint(1, min(3, len(suitable_resources))))
        assigned_resources = sample(suitable_resources, num_assignments)
        
        total_hours = task.estimated_hours
        hours_per_resource = total_hours // num_assignments
        
        for i, resource in enumerate(assigned_resources):
            # Last resource gets any remaining hours
            if i == len(assigned_resources) - 1:
                allocated_hours = total_hours - (hours_per_resource * i)
            else:
                allocated_hours = hours_per_resource
            
            Assignment.objects.create(
                resource=resource,
                task=task,
                allocated_hours=allocated_hours,
                notes=f"Assigned to {task.name} based on skill match"
            )
            assignments_created += 1
    
    print(f"✅ Created {assignments_created} assignments")

def create_time_entries(resources, tasks):
    """Create time entries for completed and in-progress tasks"""
    print("⏰ Creating Time Entries...")
    
    time_entries_created = 0
    
    for task in tasks:
        if task.status in ["completed", "in_progress"]:
            # Get assigned resources for this task
            assigned_resources = [assignment.resource for assignment in task.assignments.all()]
            
            if not assigned_resources:
                continue
            
            # Calculate how many days to generate time entries for
            task_start = max(task.start_date, date.today() - timedelta(days=90))  # Don't go too far back
            
            if task.status == "completed":
                task_end = min(task.end_date, date.today())
            else:  # in_progress
                task_end = min(task.end_date, date.today())
            
            # Generate time entries for work days
            current_date = task_start
            total_logged_hours = 0
            target_hours = task.estimated_hours * (task.completion_percentage / 100.0)
            
            while current_date <= task_end and total_logged_hours < target_hours:
                # Skip weekends
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue
                
                # Random chance of work on this day
                if random() < 0.7:  # 70% chance of work on any given day
                    for resource in assigned_resources:
                        if random() < 0.8:  # 80% chance this resource worked
                            # Random hours between 1-8
                            hours = round(random() * 7 + 1, 2)
                            if total_logged_hours + hours > target_hours:
                                hours = target_hours - total_logged_hours
                            
                            if hours > 0:
                                TimeEntry.objects.create(
                                    resource=resource,
                                    task=task,
                                    date=current_date,
                                    hours=Decimal(str(hours)),
                                    description=f"Work on {task.name}",
                                    is_billable=choice([True, True, True, False])  # 75% billable
                                )
                                time_entries_created += 1
                                total_logged_hours += hours
                
                current_date += timedelta(days=1)
                
                if total_logged_hours >= target_hours:
                    break
    
    print(f"✅ Created {time_entries_created} time entries")

def create_availability_data(resources):
    """Create comprehensive availability data for all resources"""
    print("📅 Creating Availability Data...")
    
    availability_created = 0
    
    # Define availability scenarios with realistic patterns
    availability_scenarios = [
        # Past events (for historical data)
        {'days_offset': -30, 'type': 'vacation', 'duration': 5, 'notes': 'Annual leave'},
        {'days_offset': -20, 'type': 'sick_leave', 'duration': 2, 'notes': 'Flu recovery'},
        {'days_offset': -15, 'type': 'training', 'duration': 3, 'notes': 'Professional development'},
        {'days_offset': -10, 'type': 'meeting', 'duration': 1, 'notes': 'Company all-hands'},
        
        # Current/upcoming events
        {'days_offset': 0, 'type': 'available', 'duration': 1, 'notes': 'Available for tasks'},
        {'days_offset': 2, 'type': 'meeting', 'duration': 1, 'notes': 'Client presentation'},
        {'days_offset': 5, 'type': 'training', 'duration': 2, 'notes': 'Security workshop'},
        {'days_offset': 10, 'type': 'vacation', 'duration': 3, 'notes': 'Long weekend'},
        {'days_offset': 20, 'type': 'vacation', 'duration': 10, 'notes': 'Summer vacation'},
        {'days_offset': 35, 'type': 'meeting', 'duration': 1, 'notes': 'Project review'},
        {'days_offset': 45, 'type': 'training', 'duration': 5, 'notes': 'Annual conference'},
        
        # Future planned events
        {'days_offset': 60, 'type': 'vacation', 'duration': 7, 'notes': 'Family vacation'},
        {'days_offset': 80, 'type': 'training', 'duration': 3, 'notes': 'Technical certification'},
        {'days_offset': 100, 'type': 'meeting', 'duration': 2, 'notes': 'Strategic planning'},
    ]
    
    for resource in resources:
        # Add some scenarios to each resource (not all)
        num_scenarios = randint(4, 8)  # Each resource gets 4-8 scenarios
        selected_scenarios = sample(availability_scenarios, num_scenarios)
        
        for scenario in selected_scenarios:
            start_date = date.today() + timedelta(days=scenario['days_offset'])
            end_date = start_date + timedelta(days=scenario['duration'] - 1)
            
            # Vary hours per day based on availability type
            if scenario['type'] == 'vacation':
                hours_per_day = 0
            elif scenario['type'] == 'sick_leave':
                hours_per_day = 0
            elif scenario['type'] == 'training':
                hours_per_day = 6  # Partial day
            elif scenario['type'] == 'meeting':
                hours_per_day = 4  # Half day
            else:  # available
                hours_per_day = 8
            
            ResourceAvailability.objects.create(
                resource=resource,
                start_date=start_date,
                end_date=end_date,
                availability_type=scenario['type'],
                notes=scenario['notes'],
                hours_per_day=Decimal(str(hours_per_day))
            )
            availability_created += 1
        
        # Add some random additional entries for variety
        for _ in range(randint(2, 5)):
            days_offset = randint(-60, 120)
            duration = randint(1, 4)
            start_date = date.today() + timedelta(days=days_offset)
            end_date = start_date + timedelta(days=duration - 1)
            
            availability_type = choice(['available', 'meeting', 'training', 'personal_leave'])
            
            ResourceAvailability.objects.create(
                resource=resource,
                start_date=start_date,
                end_date=end_date,
                availability_type=availability_type,
                notes=f"Random {availability_type} period",
                hours_per_day=Decimal(str(choice([0, 4, 6, 8])))
            )
            availability_created += 1
    
    print(f"✅ Created {availability_created} availability entries")

def main():
    """Main function to orchestrate the data population"""
    print("🚀 COMPREHENSIVE TEST DATA POPULATION")
    print("="*60)
    print("This script will DELETE all existing data and create new test data")
    print("="*60)
    
    # Confirm before proceeding
    confirm = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return
    
    try:
        # Step 1: Clear all existing data
        clear_all_data()
        
        # Step 2: Create base data
        skills = create_skills()
        resources = create_users_and_resources(skills)
        
        # Step 3: Create projects and tasks
        projects = create_projects(resources, skills)
        tasks = create_tasks(projects, skills)
        
        # Step 4: Create assignments and time tracking
        create_assignments(resources, tasks)
        create_time_entries(resources, tasks)
        
        # Step 5: Create availability data
        create_availability_data(resources)
        
        print("\n🎉 DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Summary:")
        print(f"✅ Skills: {Skill.objects.count()}")
        print(f"✅ Resources: {Resource.objects.count()}")
        print(f"✅ Projects: {Project.objects.count()}")
        print(f"✅ Tasks: {Task.objects.count()}")
        print(f"✅ Assignments: {Assignment.objects.count()}")
        print(f"✅ Time Entries: {TimeEntry.objects.count()}")
        print(f"✅ Availability Entries: {ResourceAvailability.objects.count()}")
        print(f"✅ Users: {User.objects.count()}")
        
        print("\n📊 The database now contains comprehensive, diverse test data for:")
        print("   • Multiple departments and roles")
        print("   • Global team with different timezones")
        print("   • Various project types and statuses")
        print("   • Complex skill requirements and matching")
        print("   • Historical and future availability data")
        print("   • Time tracking and billing data")
        print("   • Different capacity and cost scenarios")
        
        print("\n🧪 All features can now be manually tested with realistic data!")
        
    except Exception as e:
        print(f"❌ Error during data population: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
