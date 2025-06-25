from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
import logging

from .services import DemoDataService

logger = logging.getLogger(__name__)


@login_required
def demo_management_view(request):
    """Main demo management page"""
    service = DemoDataService()
    status = service.get_demo_status()
    
    context = {
        'demo_status': status,
        'page_title': 'Demo Data Management'
    }
    
    return render(request, 'demo_data/management.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def load_demo_data(request):
    """Load TechCorp Enterprise demo scenario"""
    try:
        data = json.loads(request.body) if request.body else {}
        scenario = data.get('scenario', 'techcorp_enterprise')
        
        service = DemoDataService()
        
        if scenario == 'techcorp_enterprise':
            result = service.load_techcorp_enterprise_scenario()
        else:
            result = {
                'success': False,
                'error': f'Unknown scenario: {scenario}'
            }
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error loading demo data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def clear_demo_data(request):
    """Clear all demo data"""
    try:
        service = DemoDataService()
        result = service.clear_demo_data()
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error clearing demo data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def demo_status(request):
    """Get current demo data status"""
    try:
        service = DemoDataService()
        status = service.get_demo_status()
        
        return JsonResponse({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting demo status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def recruiter_showcase(request):
    """Recruiter-friendly showcase page"""
    service = DemoDataService()
    status = service.get_demo_status()
    
    context = {
        'demo_status': status,
        'page_title': 'ResourcePro Demo Showcase'
    }
    
    return render(request, 'demo_data/recruiter_showcase.html', context)


@login_required
@require_http_methods(["GET"])
def api_demo_status(request):
    """API endpoint for demo status"""
    try:
        service = DemoDataService()
        status = service.get_demo_status()
        
        return JsonResponse({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting demo status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_load_scenario(request):
    """API endpoint for loading demo scenarios"""
    try:
        data = json.loads(request.body) if request.body else {}
        scenario = data.get('scenario', 'techcorp_enterprise')
        
        service = DemoDataService()
        
        if scenario == 'techcorp_enterprise':
            result = service.load_techcorp_enterprise_scenario()
        else:
            result = {
                'success': False,
                'error': f'Unknown scenario: {scenario}'
            }
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error loading demo scenario: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_clear_data(request):
    """API endpoint for clearing demo data"""
    try:
        service = DemoDataService()
        result = service.clear_all_data()
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error clearing demo data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def demo_completion_summary(request):
    """Demo completion summary page for recruiters"""
    context = {
        'page_title': 'Demo Completion Summary'
    }
    
    return render(request, 'demo_data/completion_summary.html', context)
