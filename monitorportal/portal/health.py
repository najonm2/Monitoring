# Health Check View for Kubernetes Liveness/Readiness Probes
# Add this to portal/views.py or create a new health.py file

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import sys


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Kubernetes probes
    Returns 200 OK if application is healthy
    """
    health_status = {
        "status": "healthy",
        "service": "informatica-monitor-portal",
        "python_version": sys.version,
    }
    
    # Add optional database check (uncomment if needed)
    # try:
    #     from portal.db.oracle_client import oracle_cursor
    #     with oracle_cursor() as cur:
    #         cur.execute("SELECT 1 FROM DUAL")
    #         cur.fetchone()
    #     health_status["database"] = "connected"
    # except Exception as e:
    #     health_status["database"] = f"error: {str(e)}"
    #     return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status, status=200)
