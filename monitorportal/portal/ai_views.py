"""
AI Views and API Endpoints
============================

Django views for AI functionality including:
- AI Dashboard with Practical Insights
- Analysis endpoints
- Training endpoints
- Status monitoring
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging

from .practical_insights import get_practical_insights, get_insights_for_team

logger = logging.getLogger(__name__)


# ==================== Dashboard View ====================

def ai_dashboard(request):
    """
    Main AI Dashboard view with practical insights.
    """
    try:
        # Get practical insights
        insights = get_practical_insights()
        
        context = {
            'insights': insights,
            'page_title': 'AI Insights Dashboard',
        }
        
        return render(request, 'portal/ai_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading AI dashboard: {str(e)}")
        context = {
            'error': str(e),
            'page_title': 'AI Insights Dashboard',
        }
        return render(request, 'portal/ai_dashboard.html', context)


# ==================== Analysis Endpoints ====================

@require_http_methods(["GET", "POST"])
def run_analysis(request):
    """
    Run AI analysis on current job data (practical insights).
    """
    try:
        # Get practical insights
        results = get_practical_insights()
        
        return JsonResponse({
            'success': True,
            'data': results,
        })
        
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_insights_summary(request):
    """
    Get high-level summary of AI insights (practical insights).
    """
    try:
        insights = get_practical_insights()
        
        return JsonResponse({
            'success': True,
            'data': insights.get('summary', {}),
        })
        
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_anomalies(request):
    """
    Get long-running sessions (anomalies).
    """
    try:
        insights = get_practical_insights()
        
        return JsonResponse({
            'success': True,
            'data': {
                'long_running_sessions': insights.get('long_running_sessions', []),
                'count': len(insights.get('long_running_sessions', [])),
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting anomalies: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_predictions(request):
    """
    Get failure predictions (failed sessions with analysis).
    """
    try:
        insights = get_practical_insights()
        
        return JsonResponse({
            'success': True,
            'data': {
                'failed_sessions': insights.get('failed_sessions', []),
                'count': len(insights.get('failed_sessions', [])),
                'dba_count': insights.get('summary', {}).get('dba_tasks_count', 0),
                'dev_count': insights.get('summary', {}).get('dev_tasks_count', 0),
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_patterns(request):
    """
    Get pattern identification results (team-based tasks).
    """
    try:
        insights = get_practical_insights()
        
        return JsonResponse({
            'success': True,
            'data': {
                'dba_tasks': insights.get('dba_tasks', []),
                'dev_tasks': insights.get('dev_tasks', []),
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting patterns: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_alerts(request):
    """
    Get current alerts and recommendations (team filter supported).
    """
    try:
        team = request.GET.get('team', 'all').upper()
        
        if team in ['DBA', 'DEV']:
            tasks = get_insights_for_team(team)
            return JsonResponse({
                'success': True,
                'data': {
                    'team': team,
                    'tasks': tasks,
                    'count': len(tasks),
                }
            })
        else:
            insights = get_practical_insights()
            return JsonResponse({
                'success': True,
                'data': {
                    'dba_tasks': insights.get('dba_tasks', []),
                    'dev_tasks': insights.get('dev_tasks', []),
                }
            })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# ==================== Status Endpoints ====================

@require_http_methods(["GET"])
def get_agent_status(request):
    """
    Get system status.
    """
    try:
        insights = get_practical_insights()
        
        return JsonResponse({
            'success': True,
            'data': {
                'health_status': insights.get('health_status', {}),
                'summary': insights.get('summary', {}),
                'timestamp': insights.get('timestamp'),
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# Alias for backward compatibility
agent_status = get_agent_status
system_health = get_agent_status

