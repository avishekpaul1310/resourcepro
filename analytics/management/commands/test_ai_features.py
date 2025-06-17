"""
Management command to test AI features
"""
from django.core.management.base import BaseCommand
from analytics.ai_services import AISkillRecommendationService, AIResourceAllocationService, AIForecastEnhancementService
from analytics.services import PredictiveAnalyticsService
from projects.models import Task
from utils.gemini_ai import gemini_service


class Command(BaseCommand):
    help = 'Test AI features and services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feature',
            type=str,
            choices=['skills', 'allocation', 'forecasting', 'all'],
            default='all',
            help='Which AI feature to test'
        )
        parser.add_argument(
            '--task-id',
            type=int,
            help='Task ID for allocation testing'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing AI Features'))
        
        # Check if AI service is available
        if not gemini_service.is_available():
            self.stdout.write(
                self.style.WARNING(
                    'Gemini AI service is not available. Please set GEMINI_API_KEY environment variable.'
                )
            )
            return
        
        feature = options['feature']
        
        if feature in ['skills', 'all']:
            self.test_skill_recommendations()
        
        if feature in ['allocation', 'all']:
            task_id = options.get('task_id')
            if task_id:
                self.test_resource_allocation(task_id)
            else:
                # Try to find a task to test with
                first_task = Task.objects.filter(status__in=['not_started', 'in_progress']).first()
                if first_task:
                    self.test_resource_allocation(first_task.id)
                else:
                    self.stdout.write(self.style.WARNING('No suitable tasks found for allocation testing'))
        
        if feature in ['forecasting', 'all']:
            self.test_forecasting()
        
        self.stdout.write(self.style.SUCCESS('AI Features testing completed'))

    def test_skill_recommendations(self):
        self.stdout.write('\n--- Testing Skill Recommendations ---')
        
        try:
            skill_service = AISkillRecommendationService()
            recommendations = skill_service.generate_skill_recommendations(force_refresh=True)
            
            if 'error' in recommendations:
                self.stdout.write(self.style.ERROR(f'Error: {recommendations["error"]}'))
                return
            
            # Display results
            for category, items in recommendations.items():
                if items:
                    self.stdout.write(f'\n{category.replace("_", " ").title()}:')
                    for item in items[:3]:  # Show top 3
                        self.stdout.write(f'  • {item["skill_name"]} (Priority: {item["priority_score"]}/10)')
                        self.stdout.write(f'    {item["reasoning"][:100]}...')
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Skill recommendations test failed: {e}'))

    def test_resource_allocation(self, task_id):
        self.stdout.write(f'\n--- Testing Resource Allocation for Task {task_id} ---')
        
        try:
            allocation_service = AIResourceAllocationService()
            suggestions = allocation_service.suggest_optimal_resource_allocation(
                task_id=task_id, 
                force_refresh=True
            )
            
            if 'error' in suggestions:
                self.stdout.write(self.style.ERROR(f'Error: {suggestions["error"]}'))
                return
            
            # Display results
            if 'suggestions' in suggestions and suggestions['suggestions']:
                self.stdout.write(f'Task: {suggestions["task"]["name"]}')
                for suggestion in suggestions['suggestions'][:3]:  # Show top 3
                    resource = suggestion['resource']
                    self.stdout.write(
                        f'  • {resource["name"]} ({resource["role"]}) - '
                        f'Match: {suggestion["match_score"]*100:.0f}%'
                    )
                    self.stdout.write(f'    {suggestion["reasoning"][:100]}...')
            else:
                self.stdout.write('No suggestions generated')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Resource allocation test failed: {e}'))

    def test_forecasting(self):
        self.stdout.write('\n--- Testing AI-Enhanced Forecasting ---')
        
        try:
            # Generate statistical forecasts first
            analytics_service = PredictiveAnalyticsService()
            forecasts = analytics_service.generate_resource_demand_forecast(
                days_ahead=30, 
                include_ai_enhancement=True
            )
            
            if not forecasts:
                self.stdout.write(self.style.WARNING('No forecasts generated (insufficient data)'))
                return
            
            # Display results
            if isinstance(forecasts, dict) and 'ai_enhanced' in forecasts:
                self.stdout.write('AI-Enhanced forecasts generated successfully!')
                
                if 'enhanced_forecasts' in forecasts['ai_enhanced']:
                    enhanced = forecasts['ai_enhanced']['enhanced_forecasts']
                    self.stdout.write(f'Enhanced {len(enhanced)} forecasts')
                    
                    for forecast in enhanced[:3]:  # Show top 3
                        original = forecast['original_forecast']
                        adjusted = forecast['ai_adjustment']
                        self.stdout.write(
                            f'  • {original["resource_role"]}: '
                            f'{original["predicted_demand_hours"]}h → {adjusted["adjusted_demand_hours"]}h '
                            f'({adjusted["adjustment_percentage"]:+.1f}%)'
                        )
                        
                if 'insights' in forecasts['ai_enhanced']:
                    insights = forecasts['ai_enhanced']['insights']
                    if 'strategic_recommendations' in insights:
                        self.stdout.write(f'Strategic insight: {insights["strategic_recommendations"][:100]}...')
                        
            elif isinstance(forecasts, list):
                self.stdout.write(f'Generated {len(forecasts)} statistical forecasts (AI enhancement not available)')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Forecasting test failed: {e}'))
