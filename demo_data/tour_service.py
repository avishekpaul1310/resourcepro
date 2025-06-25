"""
Guided Tour Service
Implements the guided tour functionality described in the Curated Demo Scenario
"""
from typing import Dict, List


class GuidedTourService:
    """Service for managing guided tours for different user types"""
    
    TOUR_SCENARIOS = {
        'executive': {
            'name': 'Executive Overview',
            'duration': '2 minutes',
            'description': 'Perfect for busy recruiters - hits all major points quickly',
            'steps': [
                {
                    'title': 'Landing Impact',
                    'duration': 15,
                    'selector': '.demo-stats',
                    'content': 'See how AI optimizes resource allocation for a 45-person engineering team managing 8 concurrent projects with 180+ active tasks.',
                    'highlights': [
                        'Reduced planning time by 89%',
                        'Identified 12 resource conflicts automatically',
                        'Optimized utilization across 20+ skill areas',
                        'Forecasted capacity needs 3 months ahead'
                    ]
                },
                {
                    'title': 'AI Recommendations Engine',
                    'duration': 30,
                    'selector': '.ai-recommendations',
                    'content': 'Notice how the AI provides not just assignments, but strategic recommendations like task splitting and collaborative assignments when facing constraints.',
                    'action': 'highlight_ai_modal'
                },
                {
                    'title': 'Resource Forecasting Power',
                    'duration': 30,
                    'selector': '.forecasting-section',
                    'content': 'Machine learning algorithms analyze 12 months of historical data to predict future resource needs with 85% accuracy.',
                    'action': 'auto_scroll_forecast'
                },
                {
                    'title': 'Problem-Solving Showcase',
                    'duration': 30,
                    'selector': '.attention-tasks',
                    'content': 'The system doesn\'t just identify problems—it provides multiple strategic solutions with precise impact calculations.',
                    'highlights': [
                        'Overallocation detection',
                        'Task splitting recommendations', 
                        'Collaborative assignment suggestions',
                        'Capacity calculations'
                    ]
                },
                {
                    'title': 'Technical Excellence Summary',
                    'duration': 15,
                    'selector': '.summary-section',
                    'content': 'This system showcases advanced AI/ML algorithms, scalable architecture, real-time optimization, and predictive analytics.',
                    'call_to_action': {
                        'continue': 'Continue Exploring',
                        'architecture': 'View Architecture', 
                        'reset': 'Reset Demo'
                    }
                }
            ]
        },
        
        'technical': {
            'name': 'Technical Deep Dive',
            'duration': '5 minutes',
            'description': 'For recruiters who want to see technical depth',
            'steps': [
                {
                    'title': 'System Architecture Overview',
                    'duration': 60,
                    'content': 'Multi-tenant database design, microservices architecture, real-time WebSocket updates, ML pipeline integration, cloud-native deployment.',
                    'metrics': {
                        'response_time': 'Sub-second for complex queries',
                        'capacity': 'Handles 10,000+ task combinations',
                        'uptime': '99.9% with auto-scaling',
                        'optimization': 'Efficient caching and query optimization'
                    }
                },
                {
                    'title': 'AI Algorithm Demonstration',
                    'duration': 90,
                    'content': 'Live ML pipeline execution showing data ingestion, feature engineering, multi-objective optimization, and confidence scoring.',
                    'features': [
                        'Resource matching calculations',
                        'Utilization impact analysis',
                        'Skill compatibility scoring',
                        'Timeline optimization logic'
                    ]
                },
                {
                    'title': 'Advanced Features Tour',
                    'duration': 120,
                    'features': [
                        'Bulk task operations',
                        'Advanced filtering and search',
                        'Real-time collaboration',
                        'Automated conflict resolution',
                        'Integration capabilities',
                        'Custom reporting and analytics'
                    ]
                },
                {
                    'title': 'Scale and Performance',
                    'duration': 60,
                    'enterprise_features': [
                        'Multi-project management',
                        'Role-based access control',
                        'Audit trails and compliance',
                        'Data export/import',
                        'Custom workflows',
                        'Performance monitoring'
                    ]
                },
                {
                    'title': 'Innovation Highlights',
                    'duration': 30,
                    'cutting_edge': [
                        'Predictive resource planning',
                        'Intelligent workload balancing',
                        'Automated capacity planning',
                        'Skills gap analysis',
                        'ROI optimization algorithms'
                    ]
                }
            ]
        }
    }
    
    @classmethod
    def get_tour_config(cls, tour_type: str = 'executive') -> Dict:
        """Get tour configuration for the specified type"""
        return cls.TOUR_SCENARIOS.get(tour_type, cls.TOUR_SCENARIOS['executive'])
    
    @classmethod
    def get_available_tours(cls) -> List[Dict]:
        """Get list of all available tours"""
        return [
            {
                'key': key,
                'name': config['name'],
                'duration': config['duration'],
                'description': config['description']
            }
            for key, config in cls.TOUR_SCENARIOS.items()
        ]
    
    @classmethod
    def generate_tour_js(cls, tour_type: str = 'executive') -> str:
        """Generate JavaScript configuration for the tour"""
        tour_config = cls.get_tour_config(tour_type)
        
        js_config = f"""
        const tourConfig = {{
            name: '{tour_config["name"]}',
            duration: '{tour_config["duration"]}',
            description: '{tour_config["description"]}',
            steps: {tour_config["steps"]}
        }};
        
        // Initialize tour when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            if (window.initializeGuidedTour) {{
                window.initializeGuidedTour(tourConfig);
            }}
        }});
        """
        
        return js_config
