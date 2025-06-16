from analytics.models import SkillDemandAnalysis

# Check what data we have
recent_analyses = SkillDemandAnalysis.objects.order_by('-analysis_date')[:20]
print(f'Found {recent_analyses.count()} skill analyses')

# Process the data as the view does
skill_demand = []
for analysis in recent_analyses:
    skill_data = {
        'skill_name': analysis.skill_name,
        'demand_score': float(analysis.demand_score),
        'active_projects': analysis.current_demand,
        'resource_count': analysis.available_resources,
        'trend': 0
    }
    skill_demand.append(skill_data)
    
print(f'Processed {len(skill_demand)} skills')
for skill in skill_demand[:3]:
    print(f'- {skill["skill_name"]}: score={skill["demand_score"]}, projects={skill["active_projects"]}')

# Test calculations
skill_demand_sorted = sorted(skill_demand, key=lambda x: x['demand_score'], reverse=True)
print('Top 3 skills by demand score:')
for skill in skill_demand_sorted[:3]:
    print(f'  {skill["skill_name"]}: {skill["demand_score"]}')
