"""
Demo Data Service
Implements the TechCorp Enterprise scenario from Curated Demo Scenario.md
"""
import time
import uuid
from datetime import datetime, timedelta, date
from random import choice, randint, random, sample
from decimal import Decimal
from typing import Dict, List, Tuple

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from accounts.models import UserProfile
from resources.models import Resource, Skill, ResourceSkill, ResourceAvailability, TimeEntry
from projects.models import Project, Task
from allocation.models import Assignment
from .models import DemoSession, DemoMetrics


class DemoDataService:
    """Service for managing demo data scenarios"""
    
    def __init__(self):
        self.current_session = None
        
    def load_techcorp_enterprise_scenario(self) -> Dict:
        """
        Load the TechCorp Enterprise scenario with 45 resources, 8 projects, 180+ tasks
        Based on the curated demo scenario design
        """
        start_time = time.time()
        
        try:
            with transaction.atomic():
                # Create demo session
                session_id = f"techcorp_{uuid.uuid4().hex[:8]}"
                self.current_session = DemoSession.objects.create(
                    session_id=session_id,
                    scenario_name="TechCorp Enterprise"
                )
                
                # Clear existing data first
                self._clear_all_data()
                
                print("🏢 Loading TechCorp Enterprise Demo Scenario...")
                print("=" * 60)
                
                # 1. Create Skills (20 skills as per spec)
                skills = self._create_techcorp_skills()
                print(f"✅ Created {len(skills)} skills")
                
                # 2. Create Resources (45 people across 6 departments)
                resources = self._create_techcorp_resources(skills)
                print(f"✅ Created {len(resources)} resources")
                
                # 3. Create Projects (8 concurrent projects)
                projects = self._create_techcorp_projects(resources)
                print(f"✅ Created {len(projects)} projects")
                
                # 4. Create Tasks (180+ tasks)
                tasks = self._create_techcorp_tasks(projects, skills)
                print(f"✅ Created {len(tasks)} tasks")
                
                # 5. Create Assignments (realistic utilization patterns)
                assignments = self._create_techcorp_assignments(resources, tasks)
                print(f"✅ Created {len(assignments)} assignments")
                
                # 6. Create Time Entries for historical data
                time_entries = self._create_techcorp_time_entries(assignments)
                print(f"✅ Created {len(time_entries)} time entries")
                
                # Update session
                self.current_session.data_loaded = True
                self.current_session.save()
                
                # Record metrics
                load_duration = time.time() - start_time
                metrics = DemoMetrics.objects.create(
                    scenario_name="TechCorp Enterprise",
                    total_resources=len(resources),
                    total_projects=len(projects),
                    total_tasks=len(tasks),
                    total_assignments=len(assignments),
                    load_duration=load_duration
                )
                
                print("=" * 60)
                print(f"🎉 TechCorp Enterprise scenario loaded successfully!")
                print(f"📊 Stats: {len(resources)} resources, {len(projects)} projects, {len(tasks)} tasks")
                print(f"⏱️  Load time: {load_duration:.2f} seconds")
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'metrics': {
                        'resources': len(resources),
                        'projects': len(projects),
                        'tasks': len(tasks),
                        'assignments': len(assignments),
                        'load_time': load_duration
                    }
                }
                
        except Exception as e:
            print(f"❌ Error loading demo data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_techcorp_skills(self) -> List[Skill]:
        """Create the 20 skills for TechCorp Enterprise"""
        skills_data = [
            # Technical Skills
            {"name": "React/Frontend", "description": "Frontend development with React.js"},
            {"name": "Node.js/Backend", "description": "Backend development with Node.js"},
            {"name": "Python", "description": "Python programming and development"},
            {"name": "AWS/Cloud", "description": "Amazon Web Services and cloud infrastructure"},
            {"name": "Mobile Development", "description": "iOS/Android and React Native development"},
            {"name": "Machine Learning", "description": "ML/AI algorithms and model development"},
            {"name": "DevOps/Infrastructure", "description": "CI/CD, containerization, infrastructure"},
            {"name": "Database Design", "description": "SQL/NoSQL database design and optimization"},
            {"name": "API Development", "description": "RESTful API design and development"},
            {"name": "Testing/QA", "description": "Test automation and quality assurance"},
            
            # Soft Skills
            {"name": "Project Management", "description": "Agile project management and coordination"},
            {"name": "Technical Writing", "description": "Documentation and technical communication"},
            {"name": "User Research", "description": "User experience research and analysis"},
            {"name": "Data Analysis", "description": "Data analytics and business intelligence"},
            {"name": "Team Leadership", "description": "Team management and leadership"},
            {"name": "Client Communication", "description": "Client relations and communication"},
            {"name": "Agile/Scrum", "description": "Agile methodologies and Scrum framework"},
            {"name": "Problem Solving", "description": "Analytical thinking and problem resolution"},
            {"name": "Mentoring", "description": "Team mentoring and knowledge sharing"},
            {"name": "Strategic Planning", "description": "Strategic thinking and business planning"}
        ]
        
        skills = []
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data["name"],
                defaults={"description": skill_data["description"]}
            )
            skills.append(skill)
        
        return skills
    
    def _create_techcorp_resources(self, skills: List[Skill]) -> List[Resource]:
        """Create 45 resources across 6 departments as per TechCorp structure"""
        
        # Create skill lookup for easy access
        skill_map = {skill.name: skill for skill in skills}
        
        # Department color scheme
        dept_colors = {
            "Engineering": "#3B82F6",      # Blue
            "Product": "#8B5CF6",          # Purple  
            "Operations": "#10B981",       # Green
            "Leadership": "#F59E0B",       # Amber
            "Specialists": "#EF4444",      # Red
            "Design": "#EC4899"            # Pink
        }
        
        resources_data = [
            # Engineering (18 people)
            # Senior Engineers (6)
            {"name": "Alice Johnson", "role": "Senior ML Engineer", "dept": "Engineering", 
             "capacity": 40, "cost": 150, "skills": ["Machine Learning", "Python", "Data Analysis", "Mentoring"], 
             "proficiencies": [9, 10, 8, 7]},
            {"name": "Bob Chen", "role": "Senior Frontend Engineer", "dept": "Engineering", 
             "capacity": 40, "cost": 140, "skills": ["React/Frontend", "API Development", "Team Leadership", "Mentoring"], 
             "proficiencies": [10, 9, 8, 7]},
            {"name": "Carol Martinez", "role": "Senior Backend Engineer", "dept": "Engineering", 
             "capacity": 40, "cost": 145, "skills": ["Node.js/Backend", "Database Design", "API Development", "Team Leadership"], 
             "proficiencies": [10, 9, 9, 8]},
            {"name": "David Kim", "role": "Senior DevOps Engineer", "dept": "Engineering", 
             "capacity": 40, "cost": 135, "skills": ["DevOps/Infrastructure", "AWS/Cloud", "Database Design", "Problem Solving"], 
             "proficiencies": [10, 9, 7, 9]},
            {"name": "Eva Rodriguez", "role": "Senior Full-Stack Engineer", "dept": "Engineering", 
             "capacity": 40, "cost": 142, "skills": ["React/Frontend", "Node.js/Backend", "Database Design", "API Development"], 
             "proficiencies": [9, 9, 8, 9]},
            {"name": "Frank Thompson", "role": "Security Engineer", "dept": "Engineering", 
             "capacity": 40, "cost": 155, "skills": ["DevOps/Infrastructure", "AWS/Cloud", "Problem Solving", "Technical Writing"], 
             "proficiencies": [8, 8, 10, 7]},
            
            # Mid-level Engineers (8)
            {"name": "Grace Liu", "role": "Frontend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 95, "skills": ["React/Frontend", "API Development", "Testing/QA", "Agile/Scrum"], 
             "proficiencies": [8, 7, 6, 8]},
            {"name": "Henry Adams", "role": "Backend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 98, "skills": ["Node.js/Backend", "Database Design", "API Development", "Testing/QA"], 
             "proficiencies": [8, 7, 8, 7]},
            {"name": "Iris Wang", "role": "Mobile Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 100, "skills": ["Mobile Development", "React/Frontend", "API Development", "Testing/QA"], 
             "proficiencies": [8, 6, 7, 7]},
            {"name": "Jack Foster", "role": "Backend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 92, "skills": ["Node.js/Backend", "Python", "Database Design", "API Development"], 
             "proficiencies": [7, 8, 7, 7]},
            {"name": "Kate Miller", "role": "Frontend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 90, "skills": ["React/Frontend", "Testing/QA", "User Research", "Agile/Scrum"], 
             "proficiencies": [7, 8, 6, 8]},
            {"name": "Leo Zhang", "role": "Mobile Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 105, "skills": ["Mobile Development", "React/Frontend", "API Development", "Problem Solving"], 
             "proficiencies": [8, 7, 7, 8]},
            {"name": "Maya Patel", "role": "Full-Stack Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 96, "skills": ["React/Frontend", "Node.js/Backend", "Database Design", "Agile/Scrum"], 
             "proficiencies": [7, 7, 6, 8]},
            {"name": "Nick Brown", "role": "Backend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 94, "skills": ["Python", "Database Design", "API Development", "Testing/QA"], 
             "proficiencies": [8, 7, 7, 7]},
            
            # Junior Engineers (4)
            {"name": "Olivia Green", "role": "Junior Frontend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 65, "skills": ["React/Frontend", "Testing/QA", "Agile/Scrum", "Problem Solving"], 
             "proficiencies": [5, 6, 7, 6]},
            {"name": "Paul Wilson", "role": "Junior Backend Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 68, "skills": ["Node.js/Backend", "Database Design", "Testing/QA", "Agile/Scrum"], 
             "proficiencies": [5, 5, 6, 7]},
            {"name": "Quinn Davis", "role": "Junior Full-Stack Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 62, "skills": ["React/Frontend", "Node.js/Backend", "Testing/QA", "Problem Solving"], 
             "proficiencies": [5, 5, 6, 6]},
            {"name": "Rachel Turner", "role": "Junior Mobile Developer", "dept": "Engineering", 
             "capacity": 40, "cost": 70, "skills": ["Mobile Development", "React/Frontend", "Testing/QA", "Agile/Scrum"], 
             "proficiencies": [5, 5, 6, 7]},
            
            # Product (8 people)
            {"name": "Sarah Williams", "role": "Senior UX Designer", "dept": "Product", 
             "capacity": 40, "cost": 120, "skills": ["User Research", "Problem Solving", "Client Communication", "Strategic Planning"], 
             "proficiencies": [9, 8, 8, 7]},
            {"name": "Tom Anderson", "role": "Product Manager", "dept": "Product", 
             "capacity": 40, "cost": 130, "skills": ["Project Management", "Strategic Planning", "Client Communication", "Data Analysis"], 
             "proficiencies": [9, 8, 9, 7]},
            {"name": "Uma Sharma", "role": "UX Designer", "dept": "Product", 
             "capacity": 40, "cost": 95, "skills": ["User Research", "Problem Solving", "Technical Writing", "Agile/Scrum"], 
             "proficiencies": [8, 7, 6, 8]},
            {"name": "Victor Lee", "role": "Product Manager", "dept": "Product", 
             "capacity": 40, "cost": 125, "skills": ["Project Management", "Data Analysis", "Strategic Planning", "Client Communication"], 
             "proficiencies": [8, 8, 7, 8]},
            {"name": "Wendy Clark", "role": "UI Designer", "dept": "Product", 
             "capacity": 40, "cost": 90, "skills": ["React/Frontend", "User Research", "Problem Solving", "Agile/Scrum"], 
             "proficiencies": [6, 8, 7, 8]},
            {"name": "Xavier Torres", "role": "Product Analyst", "dept": "Product", 
             "capacity": 40, "cost": 85, "skills": ["Data Analysis", "User Research", "Technical Writing", "Problem Solving"], 
             "proficiencies": [8, 7, 7, 8]},
            {"name": "Yuki Tanaka", "role": "Product Analyst", "dept": "Product", 
             "capacity": 40, "cost": 88, "skills": ["Data Analysis", "Python", "Technical Writing", "Problem Solving"], 
             "proficiencies": [8, 6, 7, 8]},
            {"name": "Zoe Mitchell", "role": "Senior Product Manager", "dept": "Product", 
             "capacity": 40, "cost": 140, "skills": ["Project Management", "Strategic Planning", "Team Leadership", "Client Communication"], 
             "proficiencies": [9, 9, 8, 9]},
            
            # Operations (12 people)
            {"name": "Mike Rodriguez", "role": "DevOps Lead", "dept": "Operations", 
             "capacity": 40, "cost": 125, "skills": ["DevOps/Infrastructure", "AWS/Cloud", "Team Leadership", "Problem Solving"], 
             "proficiencies": [10, 9, 8, 9]},
            {"name": "Nancy Cooper", "role": "QA Lead", "dept": "Operations", 
             "capacity": 40, "cost": 110, "skills": ["Testing/QA", "Team Leadership", "Problem Solving", "Agile/Scrum"], 
             "proficiencies": [9, 8, 8, 9]},
            {"name": "Oscar Phillips", "role": "DevOps Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 105, "skills": ["DevOps/Infrastructure", "AWS/Cloud", "Database Design", "Problem Solving"], 
             "proficiencies": [8, 8, 7, 8]},
            {"name": "Petra Jackson", "role": "QA Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 80, "skills": ["Testing/QA", "API Development", "Problem Solving", "Agile/Scrum"], 
             "proficiencies": [8, 6, 7, 8]},
            {"name": "Quincy Moore", "role": "DevOps Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 100, "skills": ["DevOps/Infrastructure", "AWS/Cloud", "Python", "Problem Solving"], 
             "proficiencies": [8, 7, 7, 8]},
            {"name": "Rita Taylor", "role": "QA Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 85, "skills": ["Testing/QA", "API Development", "Technical Writing", "Agile/Scrum"], 
             "proficiencies": [8, 7, 7, 8]},
            {"name": "Steve White", "role": "Technical Writer", "dept": "Operations", 
             "capacity": 40, "cost": 75, "skills": ["Technical Writing", "User Research", "Problem Solving", "Project Management"], 
             "proficiencies": [9, 6, 7, 6]},
            {"name": "Tina Harris", "role": "QA Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 82, "skills": ["Testing/QA", "Mobile Development", "Problem Solving", "Agile/Scrum"], 
             "proficiencies": [8, 6, 7, 8]},
            {"name": "Ulrich Martin", "role": "DevOps Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 98, "skills": ["DevOps/Infrastructure", "Database Design", "Python", "Problem Solving"], 
             "proficiencies": [7, 7, 7, 8]},
            {"name": "Vera Thompson", "role": "Technical Writer", "dept": "Operations", 
             "capacity": 40, "cost": 78, "skills": ["Technical Writing", "API Development", "User Research", "Project Management"], 
             "proficiencies": [9, 5, 7, 6]},
            {"name": "Will Garcia", "role": "QA Engineer", "dept": "Operations", 
             "capacity": 40, "cost": 87, "skills": ["Testing/QA", "API Development", "Problem Solving", "Agile/Scrum"], 
             "proficiencies": [8, 7, 8, 8]},
            {"name": "Xara Robinson", "role": "Technical Writer", "dept": "Operations", 
             "capacity": 40, "cost": 76, "skills": ["Technical Writing", "User Research", "Client Communication", "Project Management"], 
             "proficiencies": [9, 6, 7, 6]},
            
            # Leadership (4 people)
            {"name": "Amy Lewis", "role": "Engineering Manager", "dept": "Leadership", 
             "capacity": 40, "cost": 160, "skills": ["Team Leadership", "Strategic Planning", "Project Management", "Mentoring"], 
             "proficiencies": [10, 9, 9, 9]},
            {"name": "Ben Walker", "role": "Technical Lead", "dept": "Leadership", 
             "capacity": 40, "cost": 155, "skills": ["Team Leadership", "Problem Solving", "Mentoring", "Strategic Planning"], 
             "proficiencies": [9, 10, 9, 8]},
            {"name": "Cara Hall", "role": "Engineering Manager", "dept": "Leadership", 
             "capacity": 40, "cost": 165, "skills": ["Team Leadership", "Project Management", "Strategic Planning", "Client Communication"], 
             "proficiencies": [10, 9, 9, 8]},
            {"name": "Dan Allen", "role": "Technical Lead", "dept": "Leadership", 
             "capacity": 40, "cost": 150, "skills": ["Team Leadership", "Problem Solving", "Technical Writing", "Mentoring"], 
             "proficiencies": [9, 10, 8, 9]},
            
            # Specialists (3 people) - These will be the bottlenecks
            {"name": "Emma Young", "role": "ML Specialist", "dept": "Specialists", 
             "capacity": 40, "cost": 180, "skills": ["Machine Learning", "Python", "Data Analysis", "Problem Solving"], 
             "proficiencies": [10, 10, 9, 9]},
            {"name": "Felix King", "role": "Security Specialist", "dept": "Specialists", 
             "capacity": 40, "cost": 170, "skills": ["DevOps/Infrastructure", "AWS/Cloud", "Problem Solving", "Technical Writing"], 
             "proficiencies": [9, 9, 10, 8]},
            {"name": "Gina Wright", "role": "Performance Engineer", "dept": "Specialists", 
             "capacity": 40, "cost": 175, "skills": ["Database Design", "API Development", "Problem Solving", "Technical Writing"], 
             "proficiencies": [10, 9, 10, 8]},
        ]
        
        resources = []
        for res_data in resources_data:
            # Create resource
            resource = Resource.objects.create(
                name=res_data["name"],
                role=res_data["role"],
                department=res_data["dept"],
                capacity=res_data["capacity"],
                cost_per_hour=Decimal(str(res_data["cost"])),
                color=dept_colors.get(res_data["dept"], "#6B7280"),
                timezone=choice(["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]),
                location=choice(["New York, NY", "San Francisco, CA", "London, UK", "Tokyo, Japan", "Remote"])
            )
            
            # Add skills with proficiencies
            for skill_name, proficiency in zip(res_data["skills"], res_data["proficiencies"]):
                if skill_name in skill_map:
                    ResourceSkill.objects.create(
                        resource=resource,
                        skill=skill_map[skill_name],
                        proficiency=proficiency
                    )
            
            resources.append(resource)
        
        return resources
    
    def _create_techcorp_projects(self, resources: List[Resource]) -> List[Project]:
        """Create 8 concurrent projects as per TechCorp spec"""
        
        # Get managers for project assignment
        managers = [r for r in resources if "Manager" in r.role or "Lead" in r.role or "Senior" in r.role]
        
        projects_data = [
            {
                "name": "NextGen Platform",
                "description": "Complex AI-powered dashboard with machine learning capabilities",
                "start_date": date.today() - timedelta(days=30),
                "end_date": date.today() + timedelta(days=90),
                "status": "active",
                "priority": 1,
                "budget": Decimal("890000.00"),
                "color": "#EF4444"  # Red for high priority
            },
            {
                "name": "Mobile App Redesign", 
                "description": "Cross-platform mobile application with modern UI/UX",
                "start_date": date.today() - timedelta(days=15),
                "end_date": date.today() + timedelta(days=75),
                "status": "active",
                "priority": 2,
                "budget": Decimal("640000.00"),
                "color": "#F59E0B"  # Amber
            },
            {
                "name": "Security Compliance",
                "description": "SOC2 compliance implementation and security hardening",
                "start_date": date.today() - timedelta(days=10),
                "end_date": date.today() + timedelta(days=50),
                "status": "active", 
                "priority": 1,
                "budget": Decimal("420000.00"),
                "color": "#DC2626"  # Dark red for critical
            },
            {
                "name": "API Gateway Migration",
                "description": "Legacy system modernization and API gateway implementation",
                "start_date": date.today() + timedelta(days=15),
                "end_date": date.today() + timedelta(days=135),
                "status": "planning",
                "priority": 3,
                "budget": Decimal("500000.00"),
                "color": "#3B82F6"  # Blue
            },
            {
                "name": "Customer Analytics Dashboard",
                "description": "Real-time analytics and reporting platform",
                "start_date": date.today() - timedelta(days=5),
                "end_date": date.today() + timedelta(days=65),
                "status": "active",
                "priority": 2,
                "budget": Decimal("320000.00"),
                "color": "#8B5CF6"  # Purple
            },
            {
                "name": "Infrastructure Modernization",
                "description": "Cloud migration and infrastructure optimization",
                "start_date": date.today() + timedelta(days=30),
                "end_date": date.today() + timedelta(days=120),
                "status": "planning",
                "priority": 3,
                "budget": Decimal("450000.00"),
                "color": "#10B981"  # Green
            },
            {
                "name": "E-commerce Integration",
                "description": "Third-party e-commerce platform integration",
                "start_date": date.today() + timedelta(days=45),
                "end_date": date.today() + timedelta(days=105),
                "status": "planning",
                "priority": 4,
                "budget": Decimal("280000.00"),
                "color": "#6B7280"  # Gray
            },
            {
                "name": "Performance Optimization",
                "description": "System-wide performance improvements and optimization",
                "start_date": date.today() + timedelta(days=60),
                "end_date": date.today() + timedelta(days=120),
                "status": "planning",
                "priority": 4,
                "budget": Decimal("200000.00"),
                "color": "#84CC16"  # Lime
            }
        ]
        
        projects = []
        for i, proj_data in enumerate(projects_data):
            project = Project.objects.create(
                name=proj_data["name"],
                description=proj_data["description"],
                start_date=proj_data["start_date"],
                end_date=proj_data["end_date"],
                status=proj_data["status"],
                priority=proj_data["priority"],
                budget=proj_data["budget"],
                color=proj_data["color"],
                manager=managers[i % len(managers)]  # Rotate managers
            )
            projects.append(project)
        
        return projects
    
    def _create_techcorp_tasks(self, projects: List[Project], skills: List[Skill]) -> List[Task]:
        """Create 180+ tasks across the 8 projects"""
        
        skill_map = {skill.name: skill for skill in skills}
        tasks = []
        
        # Define task templates for each project
        project_tasks = {
            "NextGen Platform": [
                # AI/ML tasks requiring ML Engineer (45 tasks, 890 hours)
                {"name": "ML Model Architecture Design", "hours": 80, "skills": ["Machine Learning", "Python"], "priority": 1},
                {"name": "Data Pipeline Development", "hours": 60, "skills": ["Python", "Database Design"], "priority": 1},
                {"name": "ML Model Training", "hours": 120, "skills": ["Machine Learning", "Python"], "priority": 1},
                {"name": "Model Performance Optimization", "hours": 100, "skills": ["Machine Learning", "Python"], "priority": 1},
                {"name": "AI Dashboard Frontend", "hours": 80, "skills": ["React/Frontend", "API Development"], "priority": 2},
                {"name": "Backend API for ML Models", "hours": 70, "skills": ["Node.js/Backend", "API Development"], "priority": 2},
                {"name": "Real-time Data Processing", "hours": 90, "skills": ["Python", "Database Design"], "priority": 1},
                {"name": "ML Model Deployment", "hours": 60, "skills": ["DevOps/Infrastructure", "AWS/Cloud"], "priority": 1},
                {"name": "Dashboard UI Components", "hours": 50, "skills": ["React/Frontend"], "priority": 3},
                {"name": "API Integration Testing", "hours": 40, "skills": ["Testing/QA", "API Development"], "priority": 3},
            ],
            
            "Mobile App Redesign": [
                # Mobile and design heavy (32 tasks, 640 hours) 
                {"name": "Mobile App UI Design", "hours": 60, "skills": ["User Research", "Mobile Development"], "priority": 1},
                {"name": "Cross-Platform Framework Setup", "hours": 40, "skills": ["Mobile Development", "DevOps/Infrastructure"], "priority": 1},
                {"name": "iOS App Development", "hours": 80, "skills": ["Mobile Development", "API Development"], "priority": 2},
                {"name": "Android App Development", "hours": 80, "skills": ["Mobile Development", "API Development"], "priority": 2},
                {"name": "Mobile API Backend", "hours": 70, "skills": ["Node.js/Backend", "API Development"], "priority": 2},
                {"name": "User Authentication System", "hours": 50, "skills": ["Mobile Development", "API Development"], "priority": 1},
                {"name": "Push Notification System", "hours": 45, "skills": ["Mobile Development", "DevOps/Infrastructure"], "priority": 3},
                {"name": "Mobile App Testing", "hours": 60, "skills": ["Testing/QA", "Mobile Development"], "priority": 2},
                {"name": "App Store Optimization", "hours": 30, "skills": ["Technical Writing", "Project Management"], "priority": 4},
                {"name": "Performance Monitoring", "hours": 35, "skills": ["Mobile Development", "Data Analysis"], "priority": 3},
            ],
            
            "Security Compliance": [
                # Security focused (28 tasks, 420 hours)
                {"name": "Security Assessment", "hours": 40, "skills": ["DevOps/Infrastructure", "Problem Solving"], "priority": 1},
                {"name": "SOC2 Documentation", "hours": 60, "skills": ["Technical Writing", "Project Management"], "priority": 1},
                {"name": "Access Control Implementation", "hours": 50, "skills": ["DevOps/Infrastructure", "Database Design"], "priority": 1},
                {"name": "Encryption Implementation", "hours": 45, "skills": ["DevOps/Infrastructure", "API Development"], "priority": 1},
                {"name": "Security Testing", "hours": 55, "skills": ["Testing/QA", "DevOps/Infrastructure"], "priority": 1},
                {"name": "Compliance Monitoring", "hours": 35, "skills": ["DevOps/Infrastructure", "Data Analysis"], "priority": 2},
                {"name": "Security Training Materials", "hours": 40, "skills": ["Technical Writing", "Team Leadership"], "priority": 3},
                {"name": "Incident Response Plan", "hours": 45, "skills": ["Technical Writing", "Strategic Planning"], "priority": 2},
                {"name": "Audit Trail Implementation", "hours": 30, "skills": ["Database Design", "API Development"], "priority": 2},
                {"name": "Security Dashboard", "hours": 20, "skills": ["React/Frontend", "Data Analysis"], "priority": 4},
            ]
        }
        
        # Add more generic tasks for other projects
        generic_task_templates = [
            {"name": "Project Planning", "hours": 20, "skills": ["Project Management"], "priority": 1},
            {"name": "Requirements Analysis", "hours": 30, "skills": ["Technical Writing", "Problem Solving"], "priority": 1},
            {"name": "System Architecture", "hours": 40, "skills": ["Problem Solving", "Strategic Planning"], "priority": 1},
            {"name": "Database Design", "hours": 35, "skills": ["Database Design"], "priority": 2},
            {"name": "API Development", "hours": 45, "skills": ["API Development", "Node.js/Backend"], "priority": 2},
            {"name": "Frontend Development", "hours": 50, "skills": ["React/Frontend"], "priority": 2},
            {"name": "Testing Implementation", "hours": 30, "skills": ["Testing/QA"], "priority": 3},
            {"name": "Documentation", "hours": 25, "skills": ["Technical Writing"], "priority": 4},
            {"name": "Deployment Setup", "hours": 35, "skills": ["DevOps/Infrastructure"], "priority": 3},
            {"name": "Performance Testing", "hours": 40, "skills": ["Testing/QA", "Problem Solving"], "priority": 3},
        ]
        
        for project in projects:
            # Get specific tasks for major projects
            if project.name in project_tasks:
                task_templates = project_tasks[project.name]
                # Add some generic tasks to reach target numbers
                task_templates.extend(generic_task_templates[:5])
            else:
                # Use generic tasks for other projects
                task_templates = generic_task_templates * 2  # Duplicate to get enough tasks
            
            # Create tasks for this project
            for i, task_template in enumerate(task_templates):
                if len(tasks) >= 200:  # Cap at 200 tasks to keep demo manageable
                    break
                    
                # Calculate dates
                project_duration = (project.end_date - project.start_date).days
                task_start = project.start_date + timedelta(days=randint(0, max(1, project_duration // 3)))
                task_duration = randint(7, 45)  # 1-6 weeks
                task_end = min(task_start + timedelta(days=task_duration), project.end_date)
                
                task = Task.objects.create(
                    project=project,
                    name=f"{task_template['name']} - {project.name}",
                    description=f"Task for {project.name}: {task_template['name']}",
                    start_date=task_start,
                    end_date=task_end,
                    estimated_hours=task_template["hours"],
                    priority=task_template["priority"],
                    status=choice(["not_started", "in_progress", "not_started", "not_started"]),  # Mostly unstarted
                    completion_percentage=randint(0, 30) if randint(1, 100) < 20 else 0  # Some partial progress
                )
                
                # Add required skills
                for skill_name in task_template["skills"]:
                    if skill_name in skill_map:
                        task.skills_required.add(skill_map[skill_name])
                
                tasks.append(task)
        
        return tasks
    
    def _create_techcorp_assignments(self, resources: List[Resource], tasks: List[Task]) -> List[Assignment]:
        """Create realistic assignments with the overallocation patterns described in spec"""
        
        assignments = []
        
        # Get specific resources that should be overallocated per spec
        overallocated_resources = {
            "Alice Johnson": 190,  # ML Engineer
            "Bob Chen": 145,       # Senior Frontend  
            "Sarah Williams": 160, # UX Designer
            "Mike Rodriguez": 180  # DevOps Lead
        }
        
        # Create resource lookup
        resource_map = {r.name: r for r in resources}
        
        # Track assignments per resource to manage utilization
        resource_assignments = {r.id: [] for r in resources}
        
        # First, assign critical tasks to overallocated resources
        ml_tasks = [t for t in tasks if any(skill.name == "Machine Learning" for skill in t.skills_required.all())]
        frontend_critical_tasks = [t for t in tasks if t.priority <= 2 and any(skill.name == "React/Frontend" for skill in t.skills_required.all())]
        ux_tasks = [t for t in tasks if any(skill.name == "User Research" for skill in t.skills_required.all())]
        devops_critical_tasks = [t for t in tasks if t.priority <= 2 and any(skill.name == "DevOps/Infrastructure" for skill in t.skills_required.all())]
        
        # Assign ML tasks to Alice Johnson (overallocate)
        if "Alice Johnson" in resource_map:
            alice = resource_map["Alice Johnson"]
            for task in ml_tasks[:8]:  # Assign to 8 ML tasks (overallocation)
                assignment = Assignment.objects.create(
                    resource=alice,
                    task=task,
                    allocated_hours=task.estimated_hours,
                    notes="Critical ML expertise required"
                )
                assignments.append(assignment)
                resource_assignments[alice.id].append(assignment)
        
        # Assign frontend tasks to Bob Chen (overallocate)
        if "Bob Chen" in resource_map:
            bob = resource_map["Bob Chen"]
            for task in frontend_critical_tasks[:6]:  # Assign to 6 critical frontend tasks
                assignment = Assignment.objects.create(
                    resource=bob,
                    task=task,
                    allocated_hours=task.estimated_hours,
                    notes="Senior frontend expertise required"
                )
                assignments.append(assignment)
                resource_assignments[bob.id].append(assignment)
        
        # Assign UX tasks to Sarah Williams (overallocate)
        if "Sarah Williams" in resource_map:
            sarah = resource_map["Sarah Williams"]
            for task in ux_tasks[:7]:  # Assign to 7 UX tasks
                assignment = Assignment.objects.create(
                    resource=sarah,
                    task=task,
                    allocated_hours=task.estimated_hours,
                    notes="UX design expertise required"
                )
                assignments.append(assignment)
                resource_assignments[sarah.id].append(assignment)
        
        # Assign DevOps tasks to Mike Rodriguez (overallocate)
        if "Mike Rodriguez" in resource_map:
            mike = resource_map["Mike Rodriguez"]
            for task in devops_critical_tasks[:7]:  # Assign to 7 DevOps tasks
                assignment = Assignment.objects.create(
                    resource=mike,
                    task=task,
                    allocated_hours=task.estimated_hours,
                    notes="DevOps leadership required"
                )
                assignments.append(assignment)
                resource_assignments[mike.id].append(assignment)
        
        # Assign remaining tasks to other resources (balanced)
        assigned_task_ids = {a.task.id for a in assignments}
        remaining_tasks = [t for t in tasks if t.id not in assigned_task_ids]
        
        # Get junior resources (underutilized per spec)
        junior_resources = [r for r in resources if "Junior" in r.role]
        technical_writers = [r for r in resources if "Technical Writer" in r.role]
        qa_engineers = [r for r in resources if "QA Engineer" in r.role]
        
        # Assign some tasks to underutilized resources
        for task in remaining_tasks[:20]:  # Assign 20 tasks to underutilized resources
            suitable_resources = []
            
            # Find resources with matching skills
            for resource in junior_resources + technical_writers + qa_engineers:
                resource_skills = {rs.skill.name for rs in resource.resource_skills.all()}
                task_skills = {skill.name for skill in task.skills_required.all()}
                
                if task_skills.intersection(resource_skills):
                    suitable_resources.append(resource)
            
            if suitable_resources:
                chosen_resource = choice(suitable_resources)
                assignment = Assignment.objects.create(
                    resource=chosen_resource,
                    task=task,
                    allocated_hours=task.estimated_hours,
                    notes="Skill development opportunity"
                )
                assignments.append(assignment)
                assigned_task_ids.add(task.id)
        
        # Assign remaining tasks to mid-level resources (balanced utilization)
        remaining_tasks = [t for t in tasks if t.id not in assigned_task_ids]
        mid_level_resources = [r for r in resources if "Senior" not in r.role and "Junior" not in r.role and "Lead" not in r.role and "Manager" not in r.role]
        
        for task in remaining_tasks[:40]:  # Assign 40 more tasks
            suitable_resources = []
            
            for resource in mid_level_resources:
                if len(resource_assignments[resource.id]) < 3:  # Limit to 3 tasks per resource
                    resource_skills = {rs.skill.name for rs in resource.resource_skills.all()}
                    task_skills = {skill.name for skill in task.skills_required.all()}
                    
                    if task_skills.intersection(resource_skills):
                        suitable_resources.append(resource)
            
            if suitable_resources:
                chosen_resource = choice(suitable_resources)
                assignment = Assignment.objects.create(
                    resource=chosen_resource,
                    task=task,
                    allocated_hours=task.estimated_hours,
                    notes="Balanced workload assignment"
                )
                assignments.append(assignment)
                resource_assignments[chosen_resource.id].append(assignment)
                assigned_task_ids.add(task.id)
        
        print(f"📊 Assignment Summary:")
        print(f"   - Alice Johnson: {len(resource_assignments[resource_map['Alice Johnson'].id])} tasks (ML overallocation)")
        print(f"   - Bob Chen: {len(resource_assignments[resource_map['Bob Chen'].id])} tasks (Frontend overallocation)")
        print(f"   - Sarah Williams: {len(resource_assignments[resource_map['Sarah Williams'].id])} tasks (UX overallocation)")
        print(f"   - Mike Rodriguez: {len(resource_assignments[resource_map['Mike Rodriguez'].id])} tasks (DevOps overallocation)")
        print(f"   - Total assignments: {len(assignments)}")
        print(f"   - Unassigned tasks: {len(tasks) - len(assigned_task_ids)} (for AI recommendations)")
        
        return assignments
    
    def _create_techcorp_time_entries(self, assignments: List[Assignment]) -> List[TimeEntry]:
        """Create historical time entries for 12 months as specified"""
        
        time_entries = []
        current_date = date.today()
        
        # Create time entries for past 12 months
        for assignment in assignments:
            if assignment.task.status in ["completed", "in_progress"]:
                # Create time entries for completed or in-progress tasks
                days_to_create = min(30, (current_date - assignment.task.start_date).days)
                
                for i in range(0, days_to_create, 2):  # Every other day
                    entry_date = assignment.task.start_date + timedelta(days=i)
                    if entry_date <= current_date and entry_date.weekday() < 5:  # Weekdays only
                        
                        # Vary hours based on resource seniority and task priority
                        base_hours = 6 if "Senior" in assignment.resource.role else 4
                        hours_variation = randint(-2, 4)
                        actual_hours = max(1, base_hours + hours_variation)
                        
                        time_entry = TimeEntry.objects.create(
                            resource=assignment.resource,
                            task=assignment.task,
                            date=entry_date,
                            hours=actual_hours,
                            description=f"Work on {assignment.task.name}"
                        )
                        time_entries.append(time_entry)
        
        return time_entries
    
    def _clear_all_data(self):
        """Clear all existing data in correct order"""
        print("🧹 Clearing existing data...")
        
        # Clear in dependency order
        TimeEntry.objects.all().delete()
        Assignment.objects.all().delete() 
        ResourceAvailability.objects.all().delete()
        ResourceSkill.objects.all().delete()
        Task.objects.all().delete()
        Project.objects.all().delete()
        Resource.objects.all().delete()
        Skill.objects.all().delete()
        
        # Clear non-superuser users
        User.objects.filter(is_superuser=False).delete()
        UserProfile.objects.all().delete()
    
    def clear_demo_data(self) -> Dict:
        """Completely clear all demo data"""
        start_time = time.time()
        
        try:
            with transaction.atomic():
                self._clear_all_data()
                
                # Clear demo sessions
                DemoSession.objects.all().delete()
                
                duration = time.time() - start_time
                
                print("🧹 Demo data cleared successfully!")
                print(f"⏱️  Clear time: {duration:.2f} seconds")
                
                return {
                    'success': True,
                    'clear_time': duration,
                    'message': 'All demo data has been cleared from the database'
                }
                
        except Exception as e:
            print(f"❌ Error clearing demo data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_demo_status(self) -> Dict:
        """Get current demo data status"""
        from django.db import connection
        
        # Get table counts
        with connection.cursor() as cursor:
            tables = [
                ('resources_resource', 'Resources'),
                ('projects_project', 'Projects'), 
                ('projects_task', 'Tasks'),
                ('allocation_assignment', 'Assignments'),
                ('resources_skill', 'Skills'),
                ('resources_timeentry', 'Time Entries')
            ]
            
            counts = {}
            for table, label in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[label] = cursor.fetchone()[0]
        
        # Get latest demo session
        latest_session = DemoSession.objects.filter(is_active=True).first()
        
        return {
            'has_data': any(count > 0 for count in counts.values()),
            'counts': counts,
            'latest_session': {
                'scenario': latest_session.scenario_name if latest_session else None,
                'created_at': latest_session.created_at.isoformat() if latest_session else None,
                'session_id': latest_session.session_id if latest_session else None
            } if latest_session else None
        }
