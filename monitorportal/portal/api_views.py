# portal/api_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import random


def generate_realistic_data(report_type):
    """
    Generate realistic Informatica monitoring data
    """
    grid_names = ["GRID_PROD_01", "GRID_PROD_02", "GRID_UAT_01", "GRID_DEV_01"]
    subject_areas = ["Finance", "Sales", "HR", "Supply Chain", "Customer"]
    workflows = [
        "WF_DailyLoad_Customer",
        "WF_Monthly_Sales_Aggregation",
        "WF_HR_Payroll_Extract",
        "WF_Inventory_Update",
        "WF_Financial_Reporting",
        "WF_ETL_Master_Data",
        "WF_Real_Time_Integration",
        "WF_Data_Quality_Check"
    ]
    sessions = [
        "SQ_Extract_Customer_Data",
        "SQ_Transform_Sales_Records",
        "SQ_Load_Dimension_Table",
        "SQ_Aggregate_Monthly_Data",
        "SQ_Validate_Data_Quality",
        "SQ_Update_Master_Records",
        "SQ_Export_To_Warehouse",
        "SQ_Cleanse_Duplicate_Records"
    ]
    
    base_time = datetime.now()
    
    if report_type == "level3_failed":
        # Generate failed job data
        data = []
        num_records = random.randint(5, 15)
        
        for i in range(num_records):
            start_time = base_time - timedelta(hours=random.randint(1, 12))
            end_time = start_time + timedelta(minutes=random.randint(10, 120))
            
            record = {
                "grid_name": random.choice(grid_names),
                "subject_area": random.choice(subject_areas),
                "workflow_name": random.choice(workflows),
                "session_name": random.choice(sessions),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": random.choice(["Failed", "Stopped", "Terminated"]),
                "next_restart_time": (end_time + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.5 else None,
                "prev_failure": "Y" if random.random() > 0.6 else "N"
            }
            data.append(record)
        
        summary = {
            "total_failed": len(data),
            "today_failed": len([r for r in data if r["status"] == "Failed"]),
            "completed": random.randint(2, 8),
            "pending": len(data) - random.randint(2, 8)
        }
        
        return {"summary": summary, "data": data}
    
    elif report_type == "level3_error":
        # Generate sessions with errors
        data = []
        num_records = random.randint(8, 20)
        
        for i in range(num_records):
            start_time = base_time - timedelta(hours=random.randint(0, 10))
            end_time = start_time + timedelta(minutes=random.randint(5, 90))
            
            record = {
                "grid_name": random.choice(grid_names),
                "subject_area": random.choice(subject_areas),
                "workflow_name": random.choice(workflows),
                "session_name": random.choice(sessions),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": random.choice(["Failed", "Stopped", "Terminated"])
            }
            data.append(record)
        
        return {"data": data}
    
    elif report_type == "level3_long_running":
        # Generate long running sessions
        data = []
        num_records = random.randint(3, 10)
        
        for i in range(num_records):
            hours_running = random.randint(25, 48)
            start_time = base_time - timedelta(hours=hours_running)
            
            record = {
                "grid_name": random.choice(grid_names),
                "subject_area": random.choice(subject_areas),
                "workflow_name": random.choice(workflows),
                "session_name": random.choice(sessions),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": None,
                "running_hours": round(hours_running + random.random(), 2)
            }
            data.append(record)
        
        return {"data": data}
    
    elif report_type == "level3_all_jobs":
        # Generate realistic Level3 job statuses (matching production volume)
        data = []
        num_records = random.randint(500, 1500)  # Much larger dataset like production
        
        statuses = ["Succeeded", "Failed", "Running", "Stopped", "Aborted", "Suspended", "Waiting"]
        status_weights = [85, 5, 5, 2, 1, 1, 1]  # Most succeed
        
        # Generate sample sessions over the entire day
        base_start = base_time.replace(hour=0, minute=0, second=0)  # Start of today
        
        for i in range(num_records):
            # Spread throughout the day
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            start_time = base_start + timedelta(hours=hours_offset, minutes=minutes_offset)
            
            status = random.choices(statuses, weights=status_weights)[0]
            # Duration: 1-120 minutes for finished, None for running
            if status not in ["Running", "Waiting"]:
                duration_mins = random.randint(1, 120)
                end_time = start_time + timedelta(minutes=duration_mins)
            else:
                end_time = None
            
            record = {
                "folder": random.choice(subject_areas),
                "workflow_name": random.choice(workflows),
                "session_name": random.choice(sessions),
                "sess_start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "sess_end_time": end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else None,
                "duration_in_mins": str(duration_mins).zfill(2) + ":00" if status not in ["Running", "Waiting"] else None,
                "status": status
            }
            data.append(record)
        
        # Sort by start_time DESC (latest first) as requested
        data.sort(key=lambda x: x["sess_start_time"], reverse=True)
        
        # Calculate summary
        summary = {
            "total_jobs": len(data),
            "total_succeeded": sum(1 for r in data if r["status"] == "Succeeded"),
            "total_failed": sum(1 for r in data if r["status"] in ["Failed", "Stopped", "Aborted", "Terminated"]),
            "total_running": sum(1 for r in data if r["status"] == "Running"),
            "total_suspended": sum(1 for r in data if r["status"] == "Suspended"),
            "total_other": len(data) - sum(1 for r in data if r["status"] in ["Succeeded", "Failed", "Stopped", "Aborted", "Terminated", "Running", "Suspended"]),
        }
        
        return {"data": data, "summary": summary}
    
    elif report_type == "mdm_job_status":
        # Generate MDM job status
        data = []
        num_records = random.randint(15, 30)
        
        for i in range(num_records):
            start_time = base_time - timedelta(hours=random.randint(0, 8))
            end_time = start_time + timedelta(minutes=random.randint(5, 60))
            status = random.choices(["Succeeded", "Failed", "Running"], weights=[70, 20, 10])[0]
            
            record = {
                "grid_name": random.choice(grid_names),
                "subject_area": "MDM",
                "workflow_name": f"WF_MDM_{random.choice(['Customer', 'Product', 'Vendor', 'Material'])}",
                "session_name": f"SQ_MDM_{random.choice(['Extract', 'Transform', 'Load', 'Validate'])}",
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S") if status != "Running" else None,
                "status": status
            }
            data.append(record)
        
        return {"data": data}
    
    elif report_type == "erp_job_status":
        # Generate ERP job status
        data = []
        num_records = random.randint(20, 35)
        
        for i in range(num_records):
            start_time = base_time - timedelta(hours=random.randint(0, 12))
            end_time = start_time + timedelta(minutes=random.randint(10, 120))
            status = random.choices(["Succeeded", "Failed", "Running"], weights=[75, 15, 10])[0]
            
            record = {
                "grid_name": random.choice(grid_names),
                "subject_area": "ERP",
                "workflow_name": f"WF_ERP_{random.choice(['Finance', 'Procurement', 'Inventory', 'Sales'])}",
                "session_name": f"SQ_ERP_{random.choice(['AR', 'AP', 'GL', 'PO', 'SO', 'INV'])}",
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S") if status != "Running" else None,
                "status": status
            }
            data.append(record)
        
        return {"data": data}
    
    return {"data": []}


@require_http_methods(["GET"])
def api_report_data(request, app_slug, report_slug):
    """
    API endpoint to fetch report data from Oracle database
    Falls back to mock data if Oracle fails
    PERFORMANCE: Added 2-minute caching + timing logs
    """
    from django.core.cache import cache
    import time
    
    # Import Oracle services
    from portal.services.level3_service import (
        get_level3_failed_jobs,
        get_level3_failed_with_error,
        get_level3_long_running,
        get_level3_all_jobs_status,
        get_mdm_job_status,
        get_erp_job_status,
        get_adf_run_status,
        get_adf_failed_jobs,
    )
    
    request_start = time.time()
    
    # Try cache first for slow endpoints (2 minutes)
    cache_key = f"api_report_{app_slug}_{report_slug}"
    cached_result = cache.get(cache_key)
    if cached_result:
        cached_result["cache_hit"] = True
        print(f"[CACHE HIT] {report_slug} returned from cache in {time.time() - request_start:.3f}s")
        return JsonResponse(cached_result, safe=False)
    
    print(f"[CACHE MISS] {report_slug} - fetching from Oracle...")
    
    result = {
        "app_slug": app_slug,
        "report_slug": report_slug,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success": False,
        "data": [],
        "summary": None,
        "error": None,
        "cache_hit": False,
    }
    
    try:
        fetch_start = time.time()
        
        # Fetch REAL data from Oracle database
        if report_slug == "lvl3-failed-job-status":
            summary, data = get_level3_failed_jobs()
            result["summary"] = summary
            result["data"] = data
            
        elif report_slug == "lvl3-failed-with-error":
            result["data"] = get_level3_failed_with_error()
            print(f"[QUERY TIME] Failed with error: {time.time() - fetch_start:.2f}s")
            
        elif report_slug == "lvl3-long-running-sessions":
            result["data"] = get_level3_long_running()
            
        elif report_slug == "lvl3-all-jobs-status":
            summary, data = get_level3_all_jobs_status()
            result["summary"] = summary
            result["data"] = data
            
        elif report_slug == "mdm-job-status":
            result["data"] = get_mdm_job_status()
            
        elif report_slug == "erp-job-status-latest":
            result["data"] = get_erp_job_status()
            
        elif report_slug == "adf-run-status":
            result["data"] = get_adf_run_status()
            
        elif report_slug == "adf-failed-jobs":
            result["data"] = get_adf_failed_jobs()
            
        else:
            result["error"] = f"Unknown report: {report_slug}"
            return JsonResponse(result, status=404)
        
        result["success"] = True
        result["source"] = "oracle_database"
        
        # Set cache duration based on report type
        # Failed jobs status: longer cache (2 min) due to slow 5-query process
        if report_slug == "lvl3-failed-jobs-status":
            cache_duration = 120  # 2 minutes for slow report
            cache_label = "2min"
        else:
            cache_duration = 30  # 30 seconds for other reports
            cache_label = "30sec"
        
        cache.set(cache_key, result, cache_duration)
        
        total_time = time.time() - request_start
        print(f"[API SUCCESS] {report_slug}: {len(result.get('data', []))} rows in {total_time:.2f}s (cached for {cache_label})")
        
    except Exception as e:
        # If Oracle fails, use mock data as fallback
        print(f"⚠️ Oracle error, using mock data: {e}")
        
        report_type_map = {
            "lvl3-all-jobs-status": "level3_all_jobs",
            "lvl3-failed-job-status": "level3_failed",
            "lvl3-failed-with-error": "level3_error",
            "lvl3-long-running-sessions": "level3_long_running",
            "mdm-job-status": "mdm_job_status",
            "erp-job-status-latest": "erp_job_status",
            "adf-run-status": "adf_run_status",
            "adf-failed-jobs": "adf_failed_jobs",
        }
        
        mock_result = generate_realistic_data(report_type_map.get(report_slug, "level3_failed"))
        result["data"] = mock_result.get("data", [])
        result["summary"] = mock_result.get("summary")
        result["success"] = True
        result["source"] = "mock_data"
        result["warning"] = f"Using mock data due to: {str(e)}"
    
    return JsonResponse(result, safe=False)


# ===================================
# LEVEL3 JOB DETAILS API ENDPOINTS
# ===================================

@require_http_methods(["GET"])
def level3_today_job_details(request):
    """
    Fetch today's job details by status type
    Query params: type=all|succeeded|failed|running
    """
    import time
    start_time = time.time()
    
    try:
        status_type = request.GET.get('type', 'all').lower()
        
        from portal.services.level3_service import (
            get_today_all_job_details,
            get_today_succeeded_job_details,
            get_today_failed_job_details,
            get_today_running_job_details
        )
        
        # Fetch based on type
        if status_type == 'succeeded':
            data = get_today_succeeded_job_details(limit=2000)
        elif status_type == 'failed':
            data = get_today_failed_job_details(limit=1000)
        elif status_type == 'running':
            data = get_today_running_job_details(limit=1000)
        else:
            data = get_today_all_job_details()
        
        # Convert cursor results to list of dicts
        rows = []
        if data:
            for row in data:
                rows.append(dict(row) if hasattr(row, '__getitem__') else row)
        
        elapsed = time.time() - start_time
        
        return JsonResponse({
            'success': True,
            'type': status_type,
            'count': len(rows),
            'data': rows,
            'query_time_ms': round(elapsed * 1000),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] Failed to fetch job details: {e}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'type': status_type,
            'query_time_ms': round(elapsed * 1000)
        }, status=500)


def level3_failed_jobs_details(request):
    """
    Fetch failed jobs details filtered by status type.
    Query params: type=total|completed|pending|running
    """
    import time
    start_time = time.time()
    
    try:
        status_filter = request.GET.get('type', 'total').lower()
        
        from portal.services.level3_service import get_all_failed_jobs_status_details
        
        # Fetch all failed jobs, optionally filtered by type
        if status_filter == 'total':
            # Return all failed jobs
            data = get_all_failed_jobs_status_details(status_filter=None)
        elif status_filter in ['completed', 'pending', 'running']:
            # Return filtered by status type
            data = get_all_failed_jobs_status_details(status_filter=status_filter)
        else:
            # Invalid type, return all
            data = get_all_failed_jobs_status_details(status_filter=None)
        
        # Convert cursor results to list of dicts
        rows = []
        if data:
            for row in data:
                rows.append(dict(row) if hasattr(row, '__getitem__') else row)
        
        elapsed = time.time() - start_time
        
        return JsonResponse({
            'success': True,
            'type': status_filter,
            'count': len(rows),
            'data': rows,
            'query_time_ms': round(elapsed * 1000),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] Failed to fetch failed jobs details: {e}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'type': status_filter,
            'query_time_ms': round(elapsed * 1000)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def restart_workflow(request):
    """
    API endpoint to restart an Informatica PowerCenter workflow or session
    
    POST body (JSON):
    {
        "workflow_name": "WF_DailyLoad_Customer",
        "session_name": "s_Load_Customer",  // Optional - if provided, restarts specific session
        "folder_name": "Production", 
        "restart_from_task": "optional_task_name"  // Only used when restarting full workflow
    }
    """
    import json
    from portal.services.informatica_restart_service import InformaticaRestartService
    from django.conf import settings
    
    try:
        body = json.loads(request.body)
        workflow_name = body.get('workflow_name')
        session_name = body.get('session_name')
        folder_name = body.get('folder_name', settings.INFORMATICA_DEFAULT_FOLDER)
        restart_from_task = body.get('restart_from_task')
        
        if not workflow_name:
            return JsonResponse({
                'success': False,
                'message': 'workflow_name is required'
            }, status=400)
        
        # Initialize restart service
        service = InformaticaRestartService()
        
        # Check configuration
        if not service.is_configured():
            return JsonResponse({
                'success': False,
                'message': 'Informatica PowerCenter is not configured. Please configure credentials in settings.',
                'help': 'Set INFORMATICA_DOMAIN, INFORMATICA_REPOSITORY, INFORMATICA_INTEGRATION_SERVICE, INFORMATICA_USERNAME, INFORMATICA_PASSWORD in settings or environment variables.'
            }, status=503)
        
        # Restart session if session_name provided, otherwise restart workflow
        if session_name:
            result = service.restart_session(
                workflow_name=workflow_name,
                session_name=session_name,
                folder_name=folder_name,
                wait=False
            )
        else:
            result = service.restart_workflow(
                workflow_name=workflow_name,
                folder_name=folder_name,
                restart_from_task=restart_from_task,
                wait=False  # Don't wait for completion
            )
        
        status_code = 200 if result['success'] else 500
        return JsonResponse(result, status=status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error restarting workflow: {str(e)}',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_workflow_status(request):
    """
    API endpoint to check workflow status
    
    POST body (JSON):
    {
        "workflow_name": "WF_DailyLoad_Customer",
        "folder_name": "Production"
    }
    """
    import json
    from portal.services.informatica_restart_service import InformaticaRestartService
    from django.conf import settings
    
    try:
        body = json.loads(request.body)
        workflow_name = body.get('workflow_name')
        folder_name = body.get('folder_name', settings.INFORMATICA_DEFAULT_FOLDER)
        
        if not workflow_name:
            return JsonResponse({
                'success': False,
                'message': 'workflow_name is required'
            }, status=400)
        
        service = InformaticaRestartService()
        result = service.get_workflow_status(workflow_name, folder_name)
        
        status_code = 200 if result['success'] else 500
        return JsonResponse(result, status=status_code)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error checking status: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def restart_workflow_with_options(request):
    """
    API endpoint to restart workflow/session with 4 different options
    
    POST body (JSON):
    {
        "workflow_name": "wkf_Load_CDW_ASL_ICG_GRANITE",
        "folder_name": "B_CDW_ASL_ICG_GRANITE",
        "restart_option": 1,  // 1=Task, 2=From Task, 3=Workflow, 4=Recover
        "session_name": "s_m_Load_SITE_INST"  // Required for options 1, 2, 4
    }
    """
    import json
    from portal.services.informatica_restart_service import InformaticaRestartService
    from django.conf import settings
    
    try:
        body = json.loads(request.body)
        workflow_name = body.get('workflow_name')
        folder_name = body.get('folder_name', settings.INFORMATICA_DEFAULT_FOLDER)
        restart_option = int(body.get('restart_option', 1))
        session_name = body.get('session_name')
        integration_service = body.get('integration_service', settings.INFORMATICA_INTEGRATION_SERVICE)
        
        if not workflow_name or not folder_name:
            return JsonResponse({
                'success': False,
                'message': 'workflow_name and folder_name are required'
            }, status=400)
        
        # Initialize restart service
        service = InformaticaRestartService()
        
        # Check configuration
        if not service.is_configured():
            return JsonResponse({
                'success': False,
                'message': 'Informatica PowerCenter is not configured.'
            }, status=503)
        
        # Execute restart with selected option
        result = service.restart_with_options(
            workflow_name=workflow_name,
            folder_name=folder_name,
            restart_option=restart_option,
            session_name=session_name,
            integration_service=integration_service
        )
        
        status_code = 200 if result['success'] else 500
        return JsonResponse(result, status=status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON in request body'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': f'Invalid restart_option: {str(e)}'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stop_workflow(request):
    """
    API endpoint to stop or abort a running workflow or task
    
    POST body (JSON):
    {
        "workflow_name": "wkf_Load_CDW_ASL_ICG_GRANITE",
        "folder_name": "B_CDW_ASL_ICG_GRANITE",
        "integration_service": "IS_GRID_BI",
        "action": "stop",  // "stop" or "abort"
        "level": "workflow",  // "workflow" or "task"
        "session_name": "session_name_here"  // Required if level="task"
    }
    """
    import json
    from portal.services.informatica_restart_service import InformaticaRestartService
    from django.conf import settings
    
    try:
        body = json.loads(request.body)
        workflow_name = body.get('workflow_name')
        folder_name = body.get('folder_name', settings.INFORMATICA_DEFAULT_FOLDER)
        integration_service = body.get('integration_service', settings.INFORMATICA_INTEGRATION_SERVICE)
        action = body.get('action', 'stop')  # Default to stop
        level = body.get('level', 'workflow')  # Default to workflow
        session_name = body.get('session_name')
        
        if not workflow_name or not folder_name:
            return JsonResponse({
                'success': False,
                'message': 'workflow_name and folder_name are required'
            }, status=400)
        
        if level == 'task' and not session_name:
            return JsonResponse({
                'success': False,
                'message': 'session_name is required when level="task"'
            }, status=400)
        
        # Initialize restart service
        service = InformaticaRestartService()
        
        # Check configuration
        if not service.is_configured():
            return JsonResponse({
                'success': False,
                'message': 'Informatica PowerCenter is not configured.'
            }, status=503)
        
        # Execute stop/abort based on level and action
        if level == 'workflow':
            if action == 'stop':
                result = service.stop_workflow(
                    workflow_name=workflow_name,
                    folder_name=folder_name,
                    integration_service=integration_service
                )
            elif action == 'abort':
                result = service.abort_workflow(
                    workflow_name=workflow_name,
                    folder_name=folder_name,
                    integration_service=integration_service
                )
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action. Must be "stop" or "abort"'
                }, status=400)
        
        elif level == 'task':
            if action == 'stop':
                result = service.stop_task(
                    workflow_name=workflow_name,
                    session_name=session_name,
                    folder_name=folder_name,
                    integration_service=integration_service
                )
            elif action == 'abort':
                result = service.abort_task(
                    workflow_name=workflow_name,
                    session_name=session_name,
                    folder_name=folder_name,
                    integration_service=integration_service
                )
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action. Must be "stop" or "abort"'
                }, status=400)
        
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid level. Must be "workflow" or "task"'
            }, status=400)
        
        status_code = 200 if result['success'] else 500
        return JsonResponse(result, status=status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def schedule_workflow(request):
    """
    API endpoint to schedule or unschedule a workflow
    
    POST body (JSON):
    {
        "workflow_name": "wkf_Load_CDW_ASL_ICG_GRANITE",
        "folder_name": "B_CDW_ASL_ICG_GRANITE",
        "integration_service": "IS_GRID_BI",
        "schedule_action": "schedule"  // "schedule" or "unschedule"
    }
    """
    import json
    from portal.services.informatica_restart_service import InformaticaRestartService
    from django.conf import settings
    
    try:
        body = json.loads(request.body)
        workflow_name = body.get('workflow_name')
        folder_name = body.get('folder_name', settings.INFORMATICA_DEFAULT_FOLDER)
        integration_service = body.get('integration_service', settings.INFORMATICA_INTEGRATION_SERVICE)
        schedule_action = body.get('schedule_action', 'schedule')
        
        if not workflow_name or not folder_name:
            return JsonResponse({
                'success': False,
                'message': 'workflow_name and folder_name are required'
            }, status=400)
        
        if schedule_action not in ['schedule', 'unschedule']:
            return JsonResponse({
                'success': False,
                'message': 'schedule_action must be "schedule" or "unschedule"'
            }, status=400)
        
        # Initialize restart service
        service = InformaticaRestartService()
        
        # Check configuration
        if not service.is_configured():
            return JsonResponse({
                'success': False,
                'message': 'Informatica PowerCenter is not configured.'
            }, status=503)
        
        # Execute schedule or unschedule
        if schedule_action == 'schedule':
            result = service.schedule_workflow(
                workflow_name=workflow_name,
                folder_name=folder_name,
                integration_service=integration_service
            )
        else:  # unschedule
            result = service.unschedule_workflow(
                workflow_name=workflow_name,
                folder_name=folder_name,
                integration_service=integration_service
            )
        
        status_code = 200 if result['success'] else 500
        return JsonResponse(result, status=status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def test_informatica_connection(request):
    """
    API endpoint to test Informatica PowerCenter connection and authentication
    Returns detailed connection status
    """
    from portal.services.informatica_restart_service import InformaticaRestartService
    
    try:
        service = InformaticaRestartService()
        
        # Check configuration
        if not service.is_configured():
            return JsonResponse({
                'success': False,
                'message': 'Informatica PowerCenter is not configured',
                'details': 'Check settings.py for INFORMATICA_* configuration'
            }, status=503)
        
        # Test connection
        result = service.establish_connection()
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': '✅ Connection successful! Authentication verified.',
                'details': {
                    'host': service.host,
                    'port': service.port,
                    'domain': service.domain,
                    'repository': service.repository,
                    'username': service.username,
                    'user_security_domain': service.user_security_domain
                }
            })
        else:
            error_msg = result.get('error', result.get('message', 'Unknown error'))
            
            # Detect authentication errors
            if 'CCM_10821' in str(error_msg) or 'Authentication failed' in str(error_msg):
                return JsonResponse({
                    'success': False,
                    'message': '🔒 Authentication Failed (CCM_10821)',
                    'error': error_msg,
                    'troubleshooting': [
                        'Your password may have expired - contact IT to reset',
                        'Your account might be locked - try logging into Informatica Workflow Manager',
                        'Verify username and password in settings.py',
                        'Check if User Security Domain (CTL) is correct',
                        'Ensure you have permissions on the Integration Service'
                    ]
                }, status=401)
            else:
                return JsonResponse({
                    'success': False,
                    'message': '❌ Connection failed',
                    'error': error_msg
                }, status=500)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error testing connection: {str(e)}',
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_scheduled_workflows(request):
    """
    API endpoint to get list of recent workflows from Informatica repository
    Returns workflows from last 30 days that you can test scheduling on
    """
    from portal.db.oracle_client import fetch_all
    
    try:
        # Simple query: get all recent workflows from execution history
        # This gives you a list of real workflows to test scheduling on
        query = '''
        SELECT 
            WORKFLOW_NAME,
            FOLDER_NAME,
            LAST_RUN_TIME,
            RUN_COUNT
        FROM (
            SELECT DISTINCT
                WORKFLOW_NAME,
                SUBJECT_AREA AS FOLDER_NAME,
                MAX(START_TIME) AS LAST_RUN_TIME,
                COUNT(*) AS RUN_COUNT,
                ROW_NUMBER() OVER (PARTITION BY WORKFLOW_NAME, SUBJECT_AREA ORDER BY MAX(START_TIME) DESC) as rn
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE START_TIME >= TRUNC(SYSDATE) - 30
            AND WORKFLOW_NAME IS NOT NULL
            AND SUBJECT_AREA IS NOT NULL
            GROUP BY WORKFLOW_NAME, SUBJECT_AREA
        )
        WHERE rn = 1
        ORDER BY LAST_RUN_TIME DESC
        '''
        
        workflows = fetch_all(query)
        
        # Format last run time for display
        for wf in workflows:
            if wf.get('last_run_time'):
                wf['last_run_display'] = wf['last_run_time'].strftime('%Y-%m-%d %H:%M') if hasattr(wf['last_run_time'], 'strftime') else str(wf['last_run_time'])
            else:
                wf['last_run_display'] = 'N/A'
        
        return JsonResponse({
            'success': True,
            'workflows': workflows,
            'count': len(workflows),
            'message': f'Found {len(workflows)} workflows from last 30 days - pick any to test scheduling'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error fetching workflows: {str(e)}',
            'workflows': [],
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_informatica_folders(request):
    '''
    API endpoint to get list of Informatica folders (SUBJECT_AREA)
    Returns unique folder names from the repository
    '''
    from portal.db.oracle_client import fetch_all
    
    try:
        query = '''
        SELECT DISTINCT SUBJECT_AREA
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE SUBJECT_AREA IS NOT NULL
        AND START_TIME >= TRUNC(SYSDATE) - 30
        ORDER BY SUBJECT_AREA
        '''
        
        folders = fetch_all(query)
        folder_names = [f.get('subject_area') for f in folders if f.get('subject_area')]
        
        return JsonResponse({
            'success': True,
            'folders': folder_names,
            'count': len(folder_names)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching folders: {str(e)}',
            'folders': []
        }, status=500)


@require_http_methods(["GET"])
def get_informatica_workflows(request):
    '''
    API endpoint to get list of workflows for a specific folder
    Query parameter: folder_name
    '''
    from portal.db.oracle_client import fetch_all
    
    folder_name = request.GET.get('folder_name')
    
    if not folder_name:
        return JsonResponse({
            'success': False,
            'message': 'folder_name query parameter is required',
            'workflows': []
        }, status=400)
    
    try:
        query = '''
        SELECT DISTINCT WORKFLOW_NAME
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE SUBJECT_AREA = :folder_name
        AND START_TIME >= TRUNC(SYSDATE) - 30
        ORDER BY WORKFLOW_NAME
        '''
        
        workflows = fetch_all(query, {'folder_name': folder_name})
        workflow_names = [w.get('workflow_name') for w in workflows if w.get('workflow_name')]
        
        return JsonResponse({
            'success': True,
            'workflows': workflow_names,
            'count': len(workflow_names),
            'folder': folder_name
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching workflows: {str(e)}',
            'workflows': []
        }, status=500)


@require_http_methods(["GET"])
def get_informatica_tasks(request):
    '''
    API endpoint to get list of tasks/sessions for a specific workflow in a folder
    Query parameters: folder_name, workflow_name
    '''
    from portal.db.oracle_client import fetch_all
    
    folder_name = request.GET.get('folder_name')
    workflow_name = request.GET.get('workflow_name')
    
    if not folder_name or not workflow_name:
        return JsonResponse({
            'success': False,
            'message': 'folder_name and workflow_name query parameters are required',
            'tasks': []
        }, status=400)
    
    try:
        query = '''
        SELECT DISTINCT INSTANCE_NAME
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE SUBJECT_AREA = :folder_name
        AND WORKFLOW_NAME = :workflow_name
        AND TASK_TYPE_NAME = 'Session'
        AND START_TIME >= TRUNC(SYSDATE) - 30
        ORDER BY INSTANCE_NAME
        '''
        
        tasks = fetch_all(query, {'folder_name': folder_name, 'workflow_name': workflow_name})
        task_names = [t.get('instance_name') for t in tasks if t.get('instance_name')]
        
        return JsonResponse({
            'success': True,
            'tasks': task_names,
            'count': len(task_names),
            'folder': folder_name,
            'workflow': workflow_name
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching tasks: {str(e)}',
            'tasks': []
        }, status=500)


@require_http_methods(["GET"])
def get_workflow_session_status(request):
    '''
    API endpoint to get detailed status of all sessions in a workflow
    Query parameters: workflow_name, folder_name
    Returns all sessions with their current status, start/end times, and error messages
    '''
    from portal.db.oracle_client import fetch_all
    
    workflow_name = request.GET.get('workflow_name')
    folder_name = request.GET.get('folder_name')
    
    if not workflow_name or not folder_name:
        return JsonResponse({
            'success': False,
            'message': 'workflow_name and folder_name query parameters are required',
            'sessions': []
        }, status=400)
    
    try:
        # Enhanced query to show all workflow tasks including not-started ones and workflow structure
        query = '''
        WITH WorkflowTasks AS (
            -- Get all tasks defined in the workflow from execution history
            SELECT DISTINCT 
                WORKFLOW_NAME,
                SUBJECT_AREA,
                INSTANCE_NAME,
                TASK_TYPE_NAME
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE WORKFLOW_NAME = :workflow_name
            AND SUBJECT_AREA = :folder_name
        ),
        LatestRuns AS (
            SELECT 
                WORKFLOW_NAME,
                SUBJECT_AREA,
                INSTANCE_NAME,
                TASK_TYPE_NAME,
                START_TIME,
                END_TIME,
                RUN_STATUS_CODE,
                SUBSTR(RUN_ERR_MSG, 1, 500) AS RUN_ERROR_MESSAGE,
                DECODE(RUN_STATUS_CODE, 
                    1, 'Success',
                    2, 'Disabled',
                    3, 'Failed',
                    4, 'Stopped',
                    5, 'Aborted',
                    6, 'Running',
                    7, 'Suspending',
                    8, 'Suspended',
                    9, 'Stopping',
                    10, 'Aborting',
                    11, 'Waiting',
                    12, 'Scheduled',
                    13, 'Unscheduled',
                    14, 'Unknown',
                    15, 'Terminated',
                    'Unknown'
                ) AS STATUS,
                ROW_NUMBER() OVER (
                    PARTITION BY INSTANCE_NAME 
                    ORDER BY START_TIME DESC
                ) AS rn
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE WORKFLOW_NAME = :workflow_name
            AND SUBJECT_AREA = :folder_name
            AND START_TIME >= TRUNC(SYSDATE) - 30
        )
        SELECT 
            wt.WORKFLOW_NAME,
            wt.SUBJECT_AREA AS FOLDER_NAME,
            wt.INSTANCE_NAME AS SESSION_NAME,
            wt.TASK_TYPE_NAME,
            TO_CHAR(lr.START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS START_TIME,
            TO_CHAR(lr.END_TIME, 'YYYY-MM-DD HH24:MI:SS') AS END_TIME,
            lr.RUN_STATUS_CODE,
            lr.RUN_ERROR_MESSAGE,
            CASE 
                WHEN lr.START_TIME IS NULL THEN 'Not Started'
                ELSE lr.STATUS
            END AS STATUS,
            CASE 
                WHEN lr.END_TIME IS NOT NULL THEN 
                    ROUND((lr.END_TIME - lr.START_TIME) * 24 * 60, 2)
                WHEN lr.START_TIME IS NOT NULL THEN 
                    ROUND((SYSDATE - lr.START_TIME) * 24 * 60, 2)
                ELSE NULL
            END AS DURATION_MINUTES,
            CASE 
                WHEN lr.START_TIME IS NULL THEN 1
                ELSE 0
            END AS IS_NOT_STARTED
        FROM WorkflowTasks wt
        LEFT JOIN LatestRuns lr ON wt.INSTANCE_NAME = lr.INSTANCE_NAME 
            AND lr.rn = 1
        ORDER BY 
            IS_NOT_STARTED ASC,
            CASE WHEN lr.START_TIME IS NOT NULL THEN lr.START_TIME ELSE TO_DATE('2099-12-31', 'YYYY-MM-DD') END DESC,
            wt.INSTANCE_NAME
        '''
        
        sessions = fetch_all(query, {
            'workflow_name': workflow_name,
            'folder_name': folder_name
        })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions,
            'count': len(sessions),
            'workflow': workflow_name,
            'folder': folder_name
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error fetching workflow status: {str(e)}',
            'sessions': []
        }, status=500)


@require_http_methods(["GET"])
def get_workflow_session_status_any_folder(request):
    '''
    API endpoint to get detailed status of all sessions in a workflow
    Searches across ALL folders (faster for command task lookups)
    Query parameter: workflow_name
    Returns all sessions with their current status, start/end times, and error messages
    '''
    from portal.db.oracle_client import fetch_all
    
    workflow_name = request.GET.get('workflow_name')
    
    if not workflow_name:
        return JsonResponse({
            'success': False,
            'message': 'workflow_name query parameter is required',
            'sessions': []
        }, status=400)
    
    try:
        # Search for workflow across all folders in one query
        query = '''
        WITH WorkflowTasks AS (
            -- Get all tasks defined in the workflow from execution history
            SELECT DISTINCT 
                WORKFLOW_NAME,
                SUBJECT_AREA,
                INSTANCE_NAME,
                TASK_TYPE_NAME
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE WORKFLOW_NAME = :workflow_name
        ),
        LatestRuns AS (
            SELECT 
                WORKFLOW_NAME,
                SUBJECT_AREA,
                INSTANCE_NAME,
                TASK_TYPE_NAME,
                START_TIME,
                END_TIME,
                RUN_STATUS_CODE,
                SUBSTR(RUN_ERR_MSG, 1, 500) AS RUN_ERROR_MESSAGE,
                DECODE(RUN_STATUS_CODE, 
                    1, 'Success',
                    2, 'Disabled',
                    3, 'Failed',
                    4, 'Stopped',
                    5, 'Aborted',
                    6, 'Running',
                    7, 'Suspending',
                    8, 'Suspended',
                    9, 'Stopping',
                    10, 'Aborting',
                    11, 'Waiting',
                    12, 'Scheduled',
                    13, 'Unscheduled',
                    14, 'Unknown',
                    15, 'Terminated',
                    'Unknown'
                ) AS STATUS,
                ROW_NUMBER() OVER (
                    PARTITION BY INSTANCE_NAME 
                    ORDER BY START_TIME DESC
                ) AS rn
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE WORKFLOW_NAME = :workflow_name
            AND START_TIME >= TRUNC(SYSDATE) - 30
        )
        SELECT 
            wt.WORKFLOW_NAME,
            wt.SUBJECT_AREA AS FOLDER_NAME,
            wt.INSTANCE_NAME AS SESSION_NAME,
            wt.TASK_TYPE_NAME,
            TO_CHAR(lr.START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS START_TIME,
            TO_CHAR(lr.END_TIME, 'YYYY-MM-DD HH24:MI:SS') AS END_TIME,
            lr.RUN_STATUS_CODE,
            lr.RUN_ERROR_MESSAGE,
            CASE 
                WHEN lr.START_TIME IS NULL THEN 'Not Started'
                ELSE lr.STATUS
            END AS STATUS,
            CASE 
                WHEN lr.END_TIME IS NOT NULL THEN 
                    ROUND((lr.END_TIME - lr.START_TIME) * 24 * 60, 2)
                WHEN lr.START_TIME IS NOT NULL THEN 
                    ROUND((SYSDATE - lr.START_TIME) * 24 * 60, 2)
                ELSE NULL
            END AS DURATION_MINUTES,
            CASE 
                WHEN lr.START_TIME IS NULL THEN 1
                ELSE 0
            END AS IS_NOT_STARTED
        FROM WorkflowTasks wt
        LEFT JOIN LatestRuns lr ON wt.INSTANCE_NAME = lr.INSTANCE_NAME 
            AND lr.rn = 1
        WHERE ROWNUM <= 1000
        ORDER BY 
            IS_NOT_STARTED ASC,
            CASE WHEN lr.START_TIME IS NOT NULL THEN lr.START_TIME ELSE TO_DATE('2099-12-31', 'YYYY-MM-DD') END DESC,
            wt.INSTANCE_NAME
        '''
        
        sessions = fetch_all(query, {'workflow_name': workflow_name})
        
        # Get the folder name from the first session (they should all be in the same folder)
        folder_name = sessions[0].get('folder_name') if sessions else None
        
        return JsonResponse({
            'success': True,
            'sessions': sessions,
            'count': len(sessions),
            'workflow': workflow_name,
            'folder': folder_name
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error fetching workflow status: {str(e)}',
            'sessions': []
        }, status=500)


@require_http_methods(["GET"])
def application_monitoring_data(request):
    """
    API endpoint for application-wise monitoring
    Returns workflows for a specific application (ignoring priority levels)
    Uses LIKE pattern matching to find workflows
    """
    from django.http import JsonResponse
    from portal.db.oracle_client import fetch_all
    import traceback
    
    application = request.GET.get('application', '').strip()
    
    if not application:
        return JsonResponse({
            'success': False,
            'message': 'Application parameter is required',
            'workflows': []
        }, status=400)
    
    try:
        # Define EXACT workflow lists from RDL report for each application
        workflow_mappings = {
            'DSL_SD': [
                'wkf_Load_CDW_ASL_3SCAPE', 'wkf_Load_ASL_3SCAPE_LATAM', 'wkf_Load_CDW_ASL_ACCTMGT', 'wkf_Load_CDW_ASL_AMDOCS_ODO_SST2', 
                'wkf_Load_CDW_ASL_AMDOCS_RM_SST2', 'wkf_Load_CDW_ASL_AMDOCS_RM_3RD_SST2', 'wkf_Load_CDW_ASL_AMDOCS_RM_2ND_SST2', 
                'wkf_Load_CDW_ASL_AMDOCS_USM_SST2', 'wkf_Load_CDW_ASL_AMS', 'wkf_Load_CDW_ASL_AMT', 'wkf_Load_CDW_ASL_APOLLO', 
                'wkf_Load_CDW_ASL_APPNOTES_SST2', 'wkf_Load_CDW_ASL_APPSECURE_SST2', 'wkf_Load_CDW_ASL_APTTUS_CODS', 'wkf_Load_CDW_ASL_APTTUS_Init', 
                'wkf_Load_CDW_ASL_ARBOR_L3_DLT2', 'wkf_Load_CDW_ASL_ARBOR_L3_SST2', 'wkf_Load_CDW_ASL_ARS', 'wkf_Load_CDW_ASL_ARSYSTEM', 
                'wkf_Load_CDW_ASL_ASRC_SST2', 'wkf_Load_CDW_ASL_BART', 'wkf_Load_CDW_ASL_BILLVIZ_SST1', 'wkf_Load_CDW_ASL_BILLVIZ_SST2', 
                'wkf_Update_ASL_LOAD_STATUS_BM', 'wkf_Load_CDW_ASL_BRM_SST2', 'wkf_Load_CDW_ASL_BRM', 'wkf_Load_ASL_BTOD_SST2', 
                'wkf_Load_ASL_BTOD_MAIN', 'wkf_Load_ASL_BTOD_CLMCTR_SST2', 'wkf_Load_CDW_ASL_EASE_CABS_STG', 'wkf_Load_CDW_ASL_CABS_STG', 
                'wkf_Load_CDW_ASL_CAT', 'wkf_Load_ASL_CDMT_BATCH_SST2', 'wkf_Load_CDW_ASL_CFGN', 'wkf_Load_ASL_CFS_DASHBOARD_SST2', 
                'wkf_Load_CDW_ASL_TABLE_NOTES_LOG', 'wkf_Load_CDW_ASL_CLONES', 'wkf_Load_CDW_ASL_CNS', 'wkf_Load_CDW_ASL_CNS_SST2', 
                'wkf_Load_CDW_ASL_CNS_DLT2', 'wkf_Load_CDW_ASL_COASTAL_SST2', 'wkf_Load_CDW_ASL_COASTAL_DLT2', 'wkf_Validate_CDL_ASL_CA2PD_USECASE5', 
                'wkf_Validate_CDL_ASL_CRIS_USECASE11', 'wkf_Validate_CDL_ASL_CCSS_USECASE', 'wkf_Load_ASL_COMMON_RESTRICTED', 
                'wkf_Load_ASL_COMMON_RESTRICTED_SST2', 'wkf_Load_CDW_ASL_CORE_SST2', 'wkf_Load_CDW_ASL_CORE_DLT2', 'wkf_Load_CDW_ASL_CORE', 
                'wkf_Load_CDW_ASL_CPE_SST2', 'wkf_Load_CDW_ASL_CPO_SST2', 'wkf_Load_CDW_ASL_CPO_DLT2', 'wkf_Load_CDW_ASL_CPO_STG', 
                'wkf_Load_CDW_ASL_CPO_SST1', 'wkf_Load_CDW_ASL_CPO', 'wkf_Load_CDW_ASL_CV_SST2', 'wkf_Load_CDW_ASL_CV_Init', 
                'wkf_Load_CDW_ASL_EBG_SST2', 'wkf_Load_CDW_ASL_EM', 'wkf_Load_CDW_ASL_ENGDB', 'wkf_Load_CDW_ASL_ENS_STG', 
                'wkf_Load_CDW_ASL_ENS_CIRCUIT_ASSET_STG', 'wkf_Load_CDW_ASL_ENTNOTE_DLT2', 'wkf_Load_CDW_ASL_ENTNOTE', 
                'wkf_Load_CDW_ASL_EON_CODS_WRKFL', 'wkf_Load_CDW_ASL_EON_SST1', 'wkf_Load_CDW_ASL_EON_SST2', 'wkf_Load_CDW_ASL_EON_STG', 
                'wkf_Load_CDW_ASL_EWFM_SST2', 'wkf_Load_ASL_FI_SOX_SST2', 'wkf_Load_ASL_FIREWORKS_SST2', 'wkf_Load_CDW_ASL_FIREWORKS', 
                'wkf_Load_ASL_FIREWORKS_DLT2', 'wkf_Load_CDW_ASL_GAM', 'wkf_Load_CDW_ASL_GETS', 'wkf_Load_CDW_ASL_GLM', 
                'wkf_Load_CDW_ASL_GLM_SITE_INFO_STG', 'wkf_Load_CDW_ASL_GLOBAL_CONTACT_SST2', 'wkf_Load_CDW_ASL_GLOBAL_CONTACT', 
                'wkf_Load_CDW_ASL_GLOBAL_CONTACT_DLT2', 'wkf_Load_CDW_ASL_GRANITE_SST2', 'wkf_Load_CDW_ASL_HR_DATAHUB_SST2', 
                'wkf_Load_CDW_ASL_ICG_GRANITE', 'wkf_Load_CDW_ASL_IFO_SST1', 'wkf_Load_CDW_ASL_IFO_SST2', 'wkf_Load_CDW_ASL_IFO_DLT2', 
                'wkf_Load_CDW_ASL_IFO_4HR', 'wkf_Load_CDW_ASL_IFO_EMPLOYEE_MB', 'wkf_Load_CDW_ASL_IFO', 'wkf_Load_CDW_ASL_INGRESOS', 
                'wkf_Load_CDW_ASL_IPNMS', 'wkf_Load_CDW_ASL_IQONS', 'wkf_Load_CDW_ASL_ISM', 'wkf_Load_CDW_ASL_ISOURCE_SST2', 
                'wkf_Load_CDW_ASL_ISOURCE_DLT2', 'wkf_Load_CDW_ASL_ISOURCE', 'wkf_Load_CDW_ASL_KENAN_CDC_SST2', 'wkf_Load_CDW_ASL_KENAN_CDC_DCT1', 
                'wkf_Load_CDW_ASL_KENANFX', 'wkf_Load_ASL_KENANFX_Master', 'wkf_Load_CDW_ASL_ICDSRAW', 'wkf_Load_CDW_ASL_LERG_L3_SST2', 
                'wkf_Load_CDW_ASL_LERG_L3', 'wkf_Load_CDW_ASL_LEXCIS_SST2', 'wkf_Load_CDW_ASL_LEXM_SST1', 'wkf_Load_CDW_ASL_LEXM_SST2', 
                'wkf_Load_CDW_ASL_LMS', 'wkf_Load_ASL_MDMFI_CTLGLCLOSE', 'wkf_Load_ASL_ONESTREAM_GL_ACCOUNT', 'wkf_Load_ASL_CAPEX_HIERARCHY', 
                'wkf_Load_ASL_ONESTREAM', 'wkf_Load_CDW_ASL_MDMFI_GLCLOSE_SST2', 'wkf_Load_ASL_MDS_ACCOUNT', 'wkf_Load_ASL_MDS_NETEX', 
                'wkf_Load_CDW_ASL_METASTORM_SST2', 'wkf_Load_CDW_ASL_NC_RSI_ODB_SST2', 'wkf_Load_CDW_ASL_NC_RSI_RDB_SST2', 
                'wkf_Load_CDW_ASL_NC_WORKVU_SST2', 'wkf_Load_CDW_ASL_NDAAMS_DLT2', 'wkf_Load_CDW_ASL_NDAAMS', 'wkf_Load_CDW_ASL_NDAAMS_SST2', 
                'wkf_Load_CDW_ASL_NDAAMS_BATCH_SST2', 'wkf_Load_CDW_ASL_NDAAMS_BATCH_DLT2', 'wkf_Load_CDW_ASL_NDAAMS_BATCH', 
                'wkf_Load_ASL_NETFLEX_SRVR2', 'wkf_Load_ASL_NETFLEX_SRVR1', 'wkf_Load_ASL_NETFLEX_NOKIA1830', 'wkf_Load_CDW_ASL_NETWORX_SST2', 
                'wkf_Load_CDW_ASL_NETWORX_DLT2', 'wkf_Load_CDW_ASL_NEXTGEN', 'wkf_Load_CDW_ASL_NID', 'wkf_Load_CDW_ASL_NS_DLT2', 
                'wkf_Load_CDW_ASL_NS_SST2', 'wkf_Load_CDW_ASL_NS', 'wkf_Load_ASL_DATADMIN_NUCLEUS', 'wkf_Load_CDW_ASL_NUMS', 
                'wkf_Load_CDW_ASL_NUTS', 'wkf_Load_CDW_ASL_NX', 'wkf_Load_CDW_ASL_NX_CONFIG_SST2', 'wkf_Load_CDW_ASL_ODIN_SST2', 
                'wkf_Load_CDW_ASL_OEOM', 'wkf_Load_ASL_OFFNET_VENDOR_PORTAL', 'wkf_Load_CDW_ASL_OMC', 'wkf_Load_CDW_ASL_AP', 
                'wkf_Load_CDW_ASL_AR', 'wkf_Load_CDW_ASL_OE', 'wkf_Load_CDW_ASL_PO', 'wkf_Load_CDW_ASL_APPLSYS', 'wkf_Load_CDW_ASL_INV', 
                'wkf_Load_CDW_ASL_HR', 'wkf_Load_CDW_ASL_XXQST', 'wkf_Load_CDW_ASL_GL', 'wkf_Load_CDW_ASL_OKC', 
                'wkf_Load_CDW_ASL_ORACLE2E_FED_SST3', 'wkf_Load_CDW_ASL_ORACLE2E_FED_SST2', 'wkf_Load_CDW_ASL_ORAFIN_DLT2', 
                'wkf_Load_CDW_ASL_ORAFIN_SST2', 'wkf_Load_CDW_ASL_ORAFIN', 'wkf_Load_ASL_ORAFIN_FOR_CURRENCY_EXCHANGE_RATE', 'wkf_Load_ASL_ORION', 
                'wkf_Load_CDW_ASL_PIPELINE_SST2', 'wkf_Load_CDW_ASL_PIPELINE_DLT2', 'wkf_Load_CDW_ASL_PIPELINE_SST2_4HR', 'wkf_Load_CDW_ASL_PIPELINE', 
                'wkf_Load_ASL_PRIME', 'wkf_Load_CDW_ASL_PRO', 'wkf_Load_CDW_ASL_PRO_IP', 'wkf_Load_CDW_ASL_PRO_MNS', 'wkf_Load_ASL_PRO_VOICE', 
                'wkf_Load_CDW_ASL_PROD_SST2', 'wkf_Load_CDW_ASL_PROD_STG', 'wkf_Load_CDW_ASL_PROD', 'wkf_Load_CDW_ASL_QMV_SST2', 
                'wkf_Load_CDW_ASL_QUOTESTORE_DLT2', 'wkf_Load_CDW_ASL_QUOTESTORE_SST2', 'wkf_Load_CDW_ASL_QUOTESTORE', 'wkf_Load_CDW_ASL_RANYW_LATAM', 
                'wkf_Load_CDW_ASL_RCR_CYGENT_SST2', 'wkf_Load_CDW_ASL_RCR_CYGENT', 'wkf_Load_CDW_ASL_RCR_CYGENT_DLT2', 'wkf_Load_CDW_ASL_ROC_SST2', 
                'wkf_Load_CDW_ASL_SAO_SST2', 'wkf_Load_ASL_SAP_SST2', 'wkf_Load_ASL_SAP_DLT2_DAILY_LOADS', 'wkf_Load_ASL_SAP_DLT2', 
                'wkf_Load_ASL_SAP_SST2_SB', 'wkf_Load_ASL_ONLY_SAP', 'wkf_Load_ASL_SAP_CAPEX', 'wkf_Load_ASL_SAP_CDHDR', 
                'wkf_Load_ASL_SAP_CURRENCY_EXCHANGE', 'wkf_Load_CDW_ASL_SAP', 'wkf_Load_CDW_ASL_SAVVION_SBM_Init', 'wkf_Load_CDW_ASL_SAVVION_SBM_NRT', 
                'wkf_Load_CDW_ASL_SAVVION_SBM_BPMS', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_SST2', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_NRT', 
                'wkf_Load_CDW_ASL_SAVVION_WRKFL_INCREMENTAL_ALL', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_Init', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_BPMS', 
                'wkf_Load_CDW_ASL_SDP_ORDER_STG', 'wkf_Load_CDW_ASL_SDP_ORDER_SST2', 'wkf_Load_CDW_ASL_SDP_ORDER', 'wkf_Load_CDW_ASL_SDR', 
                'wkf_Load_CDW_ASL_SDR_STG', 'wkf_Load_CDW_ASL_SDR_WIL', 'wkf_Load_ASL_SEO_SST2', 'wkf_Load_CDW_ASL_SES_SST2', 
                'wkf_Load_CDW_ASL_SES', 'wkf_Load_CDW_ASL_SES_DLT2', 'wkf_Load_CDW_ASL_SFDC_CTL_CODS', 'wkf_Load_CDW_ASL_SFDC_CTL_2_4HR', 
                'wkf_Load_CDW_ASL_SFDC_CTL_CODS_4HR', 'wkf_Load_CDW_ASL_SFDC_CTL_2', 'wkf_Load_CDW_ASL_SFDC_CTL_CODS_DLT2', 
                'wkf_Load_CDW_ASL_SFDC_CTL_Init', 'wkf_Load_CDW_ASL_SFDC_CTL_AGENT__C', 'wkf_Load_CDW_ASL_SFDC_CTL_ENS', 'wkf_Load_CDW_ASL_SFENT_SST2', 
                'wkf_Load_CDW_ASL_SFENT_DLT2', 'wkf_Load_CDW_ASL_SFENT', 'wkf_Load_CDW_ASL_SIEBEL_L3_Init', 'wkf_Load_CDW_ASL_SIEBEL_L3_SST2', 
                'wkf_Load_CDW_ASL_SIEBEL_L3_SST2_4HR', 'wkf_Load_CDW_ASL_SIEBEL_L3_Init_4HR', 'wkf_Load_CDW_ASL_SIEBEL6_WILTEL_SST1', 
                'wkf_Load_CDW_ASL_SIEBEL8_LATAM_SST2', 'wkf_Load_CDW_ASL_SIEBEL8_LATAM_STG', 'wkf_Load_CDW_ASL_SIEBEL8_LATAM', 
                'wkf_Load_CDW_ASL_SLDB_E911_SST2', 'wkf_Load_CDW_ASL_SLDB_E911', 'wkf_Load_CDW_ASL_SLDB_E911_DLT2', 'wkf_Load_CDW_ASL_SLDB_LNP_SST2', 
                'wkf_Load_CDW_ASL_SLDB_LNP_DLT2', 'wkf_Load_CDW_ASL_SLDB_LNP', 'wkf_Load_CDW_ASL_SLDB_SUBL_SST2', 'wkf_Load_CDW_ASL_SLDB_SUBL_DLT2', 
                'wkf_Load_CDW_ASL_SLDB_SUBL', 'wkf_Load_CDW_ASL_SMART_SST2', 'wkf_Load_CDW_ASL_SONUS_AUDIT', 'wkf_Load_CDW_ASL_SWAT', 
                'wkf_Load_CDW_ASL_SWIFT_SST2', 'wkf_Load_CDW_ASL_SWIFT_STG', 'wkf_Load_CDW_ASL_SWIFT_CIRCUIT_PRE_STG', 'wkf_Load_CDW_ASL_SWIFT_INV_SST2', 
                'wkf_Load_CDW_ASL_SWIFT_TRANS_SST2', 'wkf_Load_CDW_ASL_TNI', 'wkf_Load_CDW_ASL_UPCDR_CDR', 'wkf_Load_CDW_ASL_USER_OVERRIDE_CDMT', 
                'wkf_Load_CDW_ASL_VANTIVE_SST2', 'wkf_Load_CDW_ASL_VCLI', 'wkf_Load_CDW_ASL_WM_SST2', 'wkf_Load_CDW_ASL_WM_DLT2', 
                'wkf_Load_CDW_ASL_WM', 'wkf_Load_B_CDW_ASL_WM_STG', 'wkf_RECON_ASL_CDW', 'wkf_LOAD_ODS_LEAD_TO_ORDER', 'wkf_Load_ODS_ORDER', 
                'wkf_Load_DSL_ORDER', 'wkf_Load_CDW_DSL_SD'
            ],
            'DSL_SALES_PERIOD': [
                'wkf_Load_CDW_ASL_3SCAPE', 'wkf_Load_ASL_3SCAPE_LATAM', 'wkf_Load_CDW_ASL_ACCTMGT', 'wkf_Load_CDW_ASL_AMDOCS_ODO_SST2', 
                'wkf_Load_CDW_ASL_AMDOCS_RM_SST2', 'wkf_Load_CDW_ASL_AMDOCS_RM_3RD_SST2', 'wkf_Load_CDW_ASL_AMDOCS_RM_2ND_SST2', 
                'wkf_Load_CDW_ASL_AMDOCS_USM_SST2', 'wkf_Load_CDW_ASL_AMS', 'wkf_Load_CDW_ASL_AMT', 'wkf_Load_CDW_ASL_APOLLO', 
                'wkf_Load_CDW_ASL_APPNOTES_SST2', 'wkf_Load_CDW_ASL_APPSECURE_SST2', 'wkf_Load_CDW_ASL_APTTUS_CODS', 'wkf_Load_CDW_ASL_APTTUS_Init', 
                'wkf_Load_CDW_ASL_ARBOR_L3_DLT2', 'wkf_Load_CDW_ASL_ARBOR_L3_SST2', 'wkf_Load_CDW_ASL_ARS', 'wkf_Load_CDW_ASL_ARSYSTEM', 
                'wkf_Load_CDW_ASL_ASRC_SST2', 'wkf_Load_CDW_ASL_BART', 'wkf_Load_CDW_ASL_BILLVIZ_SST1', 'wkf_Load_CDW_ASL_BILLVIZ_SST2', 
                'wkf_Update_ASL_LOAD_STATUS_BM', 'wkf_Load_CDW_ASL_BRM_SST2', 'wkf_Load_CDW_ASL_BRM', 'wkf_Load_ASL_BTOD_SST2', 
                'wkf_Load_ASL_BTOD_MAIN', 'wkf_Load_ASL_BTOD_CLMCTR_SST2', 'wkf_Load_CDW_ASL_EASE_CABS_STG', 'wkf_Load_CDW_ASL_CABS_STG', 
                'wkf_Load_CDW_ASL_CAT', 'wkf_Load_ASL_CDMT_BATCH_SST2', 'wkf_Load_CDW_ASL_CFGN', 'wkf_Load_ASL_CFS_DASHBOARD_SST2', 
                'wkf_Load_CDW_ASL_TABLE_NOTES_LOG', 'wkf_Load_CDW_ASL_CLONES', 'wkf_Load_CDW_ASL_CNS', 'wkf_Load_CDW_ASL_CNS_SST2', 
                'wkf_Load_CDW_ASL_CNS_DLT2', 'wkf_Load_CDW_ASL_COASTAL_SST2', 'wkf_Load_CDW_ASL_COASTAL_DLT2', 'wkf_Validate_CDL_ASL_CA2PD_USECASE5', 
                'wkf_Validate_CDL_ASL_CRIS_USECASE11', 'wkf_Validate_CDL_ASL_CCSS_USECASE', 'wkf_Load_ASL_COMMON_RESTRICTED', 
                'wkf_Load_ASL_COMMON_RESTRICTED_SST2', 'wkf_Load_CDW_ASL_CORE_SST2', 'wkf_Load_CDW_ASL_CORE_DLT2', 'wkf_Load_CDW_ASL_CORE', 
                'wkf_Load_CDW_ASL_CPE_SST2', 'wkf_Load_CDW_ASL_CPO_SST2', 'wkf_Load_CDW_ASL_CPO_DLT2', 'wkf_Load_CDW_ASL_CPO_STG', 
                'wkf_Load_CDW_ASL_CPO_SST1', 'wkf_Load_CDW_ASL_CPO', 'wkf_Load_CDW_ASL_CV_SST2', 'wkf_Load_CDW_ASL_CV_Init', 
                'wkf_Load_CDW_ASL_EBG_SST2', 'wkf_Load_CDW_ASL_EM', 'wkf_Load_CDW_ASL_ENGDB', 'wkf_Load_CDW_ASL_ENS_STG', 
                'wkf_Load_CDW_ASL_ENS_CIRCUIT_ASSET_STG', 'wkf_Load_CDW_ASL_ENTNOTE_DLT2', 'wkf_Load_CDW_ASL_ENTNOTE', 
                'wkf_Load_CDW_ASL_EON_CODS_WRKFL', 'wkf_Load_CDW_ASL_EON_SST1', 'wkf_Load_CDW_ASL_EON_SST2', 'wkf_Load_CDW_ASL_EON_STG', 
                'wkf_Load_CDW_ASL_EWFM_SST2', 'wkf_Load_ASL_FI_SOX_SST2', 'wkf_Load_ASL_FIREWORKS_SST2', 'wkf_Load_CDW_ASL_FIREWORKS', 
                'wkf_Load_ASL_FIREWORKS_DLT2', 'wkf_Load_CDW_ASL_GAM', 'wkf_Load_CDW_ASL_GETS', 'wkf_Load_CDW_ASL_GLM', 
                'wkf_Load_CDW_ASL_GLM_SITE_INFO_STG', 'wkf_Load_CDW_ASL_GLOBAL_CONTACT_SST2', 'wkf_Load_CDW_ASL_GLOBAL_CONTACT', 
                'wkf_Load_CDW_ASL_GLOBAL_CONTACT_DLT2', 'wkf_Load_CDW_ASL_GRANITE_SST2', 'wkf_Load_CDW_ASL_HR_DATAHUB_SST2', 
                'wkf_Load_CDW_ASL_ICG_GRANITE', 'wkf_Load_CDW_ASL_IFO_SST1', 'wkf_Load_CDW_ASL_IFO_SST2', 'wkf_Load_CDW_ASL_IFO_DLT2', 
                'wkf_Load_CDW_ASL_IFO_4HR', 'wkf_Load_CDW_ASL_IFO_EMPLOYEE_MB', 'wkf_Load_CDW_ASL_IFO', 'wkf_Load_CDW_ASL_INGRESOS', 
                'wkf_Load_CDW_ASL_IPNMS', 'wkf_Load_CDW_ASL_IQONS', 'wkf_Load_CDW_ASL_ISM', 'wkf_Load_CDW_ASL_ISOURCE_SST2', 
                'wkf_Load_CDW_ASL_ISOURCE_DLT2', 'wkf_Load_CDW_ASL_ISOURCE', 'wkf_Load_CDW_ASL_KENAN_CDC_SST2', 'wkf_Load_CDW_ASL_KENAN_CDC_DCT1', 
                'wkf_Load_CDW_ASL_KENANFX', 'wkf_Load_ASL_KENANFX_Master', 'wkf_Load_CDW_ASL_ICDSRAW', 'wkf_Load_CDW_ASL_LERG_L3_SST2', 
                'wkf_Load_CDW_ASL_LERG_L3', 'wkf_Load_CDW_ASL_LEXCIS_SST2', 'wkf_Load_CDW_ASL_LEXM_SST1', 'wkf_Load_CDW_ASL_LEXM_SST2', 
                'wkf_Load_CDW_ASL_LMS', 'wkf_Load_ASL_MDMFI_CTLGLCLOSE', 'wkf_Load_ASL_ONESTREAM_GL_ACCOUNT', 'wkf_Load_ASL_CAPEX_HIERARCHY', 
                'wkf_Load_ASL_ONESTREAM', 'wkf_Load_CDW_ASL_MDMFI_GLCLOSE_SST2', 'wkf_Load_ASL_MDS_ACCOUNT', 'wkf_Load_ASL_MDS_NETEX', 
                'wkf_Load_CDW_ASL_METASTORM_SST2', 'wkf_Load_CDW_ASL_NC_RSI_ODB_SST2', 'wkf_Load_CDW_ASL_NC_RSI_RDB_SST2', 
                'wkf_Load_CDW_ASL_NC_WORKVU_SST2', 'wkf_Load_CDW_ASL_NDAAMS_DLT2', 'wkf_Load_CDW_ASL_NDAAMS', 'wkf_Load_CDW_ASL_NDAAMS_SST2', 
                'wkf_Load_CDW_ASL_NDAAMS_BATCH_SST2', 'wkf_Load_CDW_ASL_NDAAMS_BATCH_DLT2', 'wkf_Load_CDW_ASL_NDAAMS_BATCH', 
                'wkf_Load_ASL_NETFLEX_SRVR2', 'wkf_Load_ASL_NETFLEX_SRVR1', 'wkf_Load_ASL_NETFLEX_NOKIA1830', 'wkf_Load_CDW_ASL_NETWORX_SST2', 
                'wkf_Load_CDW_ASL_NETWORX_DLT2', 'wkf_Load_CDW_ASL_NEXTGEN', 'wkf_Load_CDW_ASL_NID', 'wkf_Load_CDW_ASL_NS_DLT2', 
                'wkf_Load_CDW_ASL_NS_SST2', 'wkf_Load_CDW_ASL_NS', 'wkf_Load_ASL_DATADMIN_NUCLEUS', 'wkf_Load_CDW_ASL_NUMS', 
                'wkf_Load_CDW_ASL_NUTS', 'wkf_Load_CDW_ASL_NX', 'wkf_Load_CDW_ASL_NX_CONFIG_SST2', 'wkf_Load_CDW_ASL_ODIN_SST2', 
                'wkf_Load_CDW_ASL_OEOM', 'wkf_Load_ASL_OFFNET_VENDOR_PORTAL', 'wkf_Load_CDW_ASL_OMC', 'wkf_Load_CDW_ASL_AP', 
                'wkf_Load_CDW_ASL_AR', 'wkf_Load_CDW_ASL_OE', 'wkf_Load_CDW_ASL_PO', 'wkf_Load_CDW_ASL_APPLSYS', 'wkf_Load_CDW_ASL_INV', 
                'wkf_Load_CDW_ASL_HR', 'wkf_Load_CDW_ASL_XXQST', 'wkf_Load_CDW_ASL_GL', 'wkf_Load_CDW_ASL_OKC', 
                'wkf_Load_CDW_ASL_ORACLE2E_FED_SST3', 'wkf_Load_CDW_ASL_ORACLE2E_FED_SST2', 'wkf_Load_CDW_ASL_ORAFIN_DLT2', 
                'wkf_Load_CDW_ASL_ORAFIN_SST2', 'wkf_Load_CDW_ASL_ORAFIN', 'wkf_Load_ASL_ORAFIN_FOR_CURRENCY_EXCHANGE_RATE', 'wkf_Load_ASL_ORION', 
                'wkf_Load_CDW_ASL_PIPELINE_SST2', 'wkf_Load_CDW_ASL_PIPELINE_DLT2', 'wkf_Load_CDW_ASL_PIPELINE_SST2_4HR', 'wkf_Load_CDW_ASL_PIPELINE', 
                'wkf_Load_ASL_PRIME', 'wkf_Load_CDW_ASL_PRO', 'wkf_Load_CDW_ASL_PRO_IP', 'wkf_Load_CDW_ASL_PRO_MNS', 'wkf_Load_ASL_PRO_VOICE', 
                'wkf_Load_CDW_ASL_PROD_SST2', 'wkf_Load_CDW_ASL_PROD_STG', 'wkf_Load_CDW_ASL_PROD', 'wkf_Load_CDW_ASL_QMV_SST2', 
                'wkf_Load_CDW_ASL_QUOTESTORE_DLT2', 'wkf_Load_CDW_ASL_QUOTESTORE_SST2', 'wkf_Load_CDW_ASL_QUOTESTORE', 'wkf_Load_CDW_ASL_RANYW_LATAM', 
                'wkf_Load_CDW_ASL_RCR_CYGENT_SST2', 'wkf_Load_CDW_ASL_RCR_CYGENT', 'wkf_Load_CDW_ASL_RCR_CYGENT_DLT2', 'wkf_Load_CDW_ASL_ROC_SST2', 
                'wkf_Load_CDW_ASL_SAO_SST2', 'wkf_Load_ASL_SAP_SST2', 'wkf_Load_ASL_SAP_DLT2_DAILY_LOADS', 'wkf_Load_ASL_SAP_DLT2', 
                'wkf_Load_ASL_SAP_SST2_SB', 'wkf_Load_ASL_ONLY_SAP', 'wkf_Load_ASL_SAP_CAPEX', 'wkf_Load_ASL_SAP_CDHDR', 
                'wkf_Load_ASL_SAP_CURRENCY_EXCHANGE', 'wkf_Load_CDW_ASL_SAP', 'wkf_Load_CDW_ASL_SAVVION_SBM_Init', 'wkf_Load_CDW_ASL_SAVVION_SBM_NRT', 
                'wkf_Load_CDW_ASL_SAVVION_SBM_BPMS', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_SST2', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_NRT', 
                'wkf_Load_CDW_ASL_SAVVION_WRKFL_INCREMENTAL_ALL', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_Init', 'wkf_Load_CDW_ASL_SAVVION_WRKFL_BPMS', 
                'wkf_Load_CDW_ASL_SDP_ORDER_STG', 'wkf_Load_CDW_ASL_SDP_ORDER_SST2', 'wkf_Load_CDW_ASL_SDP_ORDER', 'wkf_Load_CDW_ASL_SDR', 
                'wkf_Load_CDW_ASL_SDR_STG', 'wkf_Load_CDW_ASL_SDR_WIL', 'wkf_Load_ASL_SEO_SST2', 'wkf_Load_CDW_ASL_SES_SST2', 
                'wkf_Load_CDW_ASL_SES', 'wkf_Load_CDW_ASL_SES_DLT2', 'wkf_Load_CDW_ASL_SFDC_CTL_CODS', 'wkf_Load_CDW_ASL_SFDC_CTL_2_4HR', 
                'wkf_Load_CDW_ASL_SFDC_CTL_CODS_4HR', 'wkf_Load_CDW_ASL_SFDC_CTL_2', 'wkf_Load_CDW_ASL_SFDC_CTL_CODS_DLT2', 
                'wkf_Load_CDW_ASL_SFDC_CTL_Init', 'wkf_Load_CDW_ASL_SFDC_CTL_AGENT__C', 'wkf_Load_CDW_ASL_SFDC_CTL_ENS', 'wkf_Load_CDW_ASL_SFENT_SST2', 
                'wkf_Load_CDW_ASL_SFENT_DLT2', 'wkf_Load_CDW_ASL_SFENT', 'wkf_Load_CDW_ASL_SIEBEL_L3_Init', 'wkf_Load_CDW_ASL_SIEBEL_L3_SST2', 
                'wkf_Load_CDW_ASL_SIEBEL_L3_SST2_4HR', 'wkf_Load_CDW_ASL_SIEBEL_L3_Init_4HR', 'wkf_Load_CDW_ASL_SIEBEL6_WILTEL_SST1', 
                'wkf_Load_CDW_ASL_SIEBEL8_LATAM_SST2', 'wkf_Load_CDW_ASL_SIEBEL8_LATAM_STG', 'wkf_Load_CDW_ASL_SIEBEL8_LATAM', 
                'wkf_Load_CDW_ASL_SLDB_E911_SST2', 'wkf_Load_CDW_ASL_SLDB_E911', 'wkf_Load_CDW_ASL_SLDB_E911_DLT2', 'wkf_Load_CDW_ASL_SLDB_LNP_SST2', 
                'wkf_Load_CDW_ASL_SLDB_LNP_DLT2', 'wkf_Load_CDW_ASL_SLDB_LNP', 'wkf_Load_CDW_ASL_SLDB_SUBL_SST2', 'wkf_Load_CDW_ASL_SLDB_SUBL_DLT2', 
                'wkf_Load_CDW_ASL_SLDB_SUBL', 'wkf_Load_CDW_ASL_SMART_SST2', 'wkf_Load_CDW_ASL_SONUS_AUDIT', 'wkf_Load_CDW_ASL_SWAT', 
                'wkf_Load_CDW_ASL_SWIFT_SST2', 'wkf_Load_CDW_ASL_SWIFT_STG', 'wkf_Load_CDW_ASL_SWIFT_CIRCUIT_PRE_STG', 'wkf_Load_CDW_ASL_SWIFT_INV_SST2', 
                'wkf_Load_CDW_ASL_SWIFT_TRANS_SST2', 'wkf_Load_CDW_ASL_TNI', 'wkf_Load_CDW_ASL_UPCDR_CDR', 'wkf_Load_CDW_ASL_USER_OVERRIDE_CDMT', 
                'wkf_Load_CDW_ASL_VANTIVE_SST2', 'wkf_Load_CDW_ASL_VCLI', 'wkf_Load_CDW_ASL_WM_SST2', 'wkf_Load_CDW_ASL_WM_DLT2', 
                'wkf_Load_CDW_ASL_WM', 'wkf_Load_B_CDW_ASL_WM_STG', 'wkf_RECON_ASL_CDW', 'wkf_LOAD_ODS_LEAD_TO_ORDER', 'wkf_Load_ODS_ORDER', 
                'wkf_Load_DSL_ORDER', 'wkf_Load_DSL_ORDER_ENS', 'wkf_Load_DSL_SALES_PERIOD', 'wkf_Load_CALCULATE_DATE_RANGE', 
                'wkf_Load_CODS_SALES_ORDER_LINE_STG', 'wkf_Load_CODS_TN_SALES_ORDER_LINE_STG', 'wkf_Load_REVISE_SALES_ORDER_LINE_STG', 
                'wkf_Load_ADJ_STG', 'wkf_Load_BULK_SALES_ORDER_LINE_STG', 'wkf_Load_CLARIFY_SALES_ORDER_LINE_STG', 'wkf_Load_ODS_SSQ_Customer_Only', 
                'wkf_Load_ODS_FINANCE_DIM_DAILY_REFRESH', 'wkf_Load_SALES_ORDER_LINE_HIST', 'wkf_Update_CODS_TN_DW_SECURE_COMPANY_NBR_SLDB', 
                'wkf_Load_TN_CODS_DK2', 'wkf_Load_DIGRS', 'wkf_Load_CODS_TN', 'wkf_Load_ODS_SOURCE_BILLING_ACCOUNT', 'wkf_Load_CDW_ASL_ACCTMGT', 
                'wkf_Load_CDW_ASL_ARBOR_L3_SST2', 'wkf_Load_CDW_ASL_BRM_SST2', 'wkf_Load_CDW_ASL_CABS_SST2', 'wkf_Load_CDW_ASL_KENANFX', 
                'wkf_Load_CDW_ASL_LEXCIS', 'wkf_Load_CDW_ASL_MBS', 'wkf_Load_CDW_ASL_PROD', 'wkf_Load_ASL_SAP_SST2_SB', 
                'wkf_Load_CDW_ASL_SFDC_CTL_CODS_DLT2', 'wkf_Load_CDW_ASL_SFDC_CTL_CODS_4HR', 'wkf_Load_CDW_ASL_SFDC_FIBER_SST2', 
                'wkf_Load_CDW_ASL_SIEBEL6_WILTEL', 'wkf_Load_CDW_ASL_SIEBEL8_LATAM_SST2', 'wkf_Load_CDW_ASL_SIEBEL_L3_Init', 
                'wkf_Load_CDW_ASL_SIEBEL_L3_Init_4HR', 'wkf_Load_CDW_ASL_SIEBEL_L3_SST2_4HR', 'wkf_Load_CDW_ASL_VANTIVE_SST2', 
                'wkf_Load_CDW_ASL_ORACLE2E_FED_SST2', 'wkf_Load_CDW_ASL_LEXM', 'wkf_Load_CDW_ASL_CPE_SST2', 'wkf_Load_CDW_ASL_ORAFIN', 
                'wkf_Load_ODS_SSQ_Customer_Only'
            ],
            'SMMART': [
                'wkf_Load_W_CASE_SLA_HIST', 'wkf_LOAD_W_EVENT', 'wkf_UPDATE_PREV_DATE', 'wkf_Load_SMMART1', 'wkf_Load_SMMART2', 
                'wkf_SM_TTR_NET_DURATION_INCREMENTAL_1', 'wkf_Generate_Parameter_File_Hist', 'wkf_Load_W_SUBCASE', 'wkf_load_W_CASE', 
                'wkf_Load_W_CASE_ARCHIVE', 'wkf_Generate_Parameter_File', 'wkf_SMMART_Controller', 'wkf_Load_CDW_ASL_CLARIFY_SA', 
                'wkf_Load_CDW_ASL_CLARIFY_SA_Hourly', 'wkf_Load_LDW_NRL_CASC', 'wkf_Load_ORSM_W_CASE', 'wkf_Load_ORSM', 'wkf_Load_ORSM_DIM'
            ],
            'AML': [
                'wkf_Load_MASTER_AML_CONTROL', 'wkf_Load_NETEX_SUPPLIER_INV_DETAIL_SAM_EMEA', 'wkf_Load_CODS_NETINV_LEGACY', 
                'wkf_Load_NETINV_Controller', 'wkf_Load_ASR_workflow', 'wkf_Load_NETEX_SUPPLIER_INV_DETAIL_SAM_LATAM', 
                'wkf_Load_ASL_SAM_SYNCH_EMEA_Master', 'wkf_Load_NETEX_SUPPLIER_INV_DETAIL_SAM', 'wkf_Load_AML_ALL', 
                'wkf_Upd_NETEX_SUPPLIER_INV_DETAIL_SAM_EMEA', 'wkf_Load_NETEX_SUPP_INV_DTL_SAM_EMEA', 'wkf_Load_NETEX_SUPPLIER_INV_GL_SAM_EMEA_Incremental', 
                'wkf_m_Load_NETEX_STG_CIRCUIT_ASG_TSC_ALLOC_SAM_EMEA', 'wkf_Load_NETEX_USOC_BILLED_CCD_SAM_EMEA_Incremental', 
                'wkf_Load_NETEX_SUPPLIER_INV_DETAIL_USAGE_SAM_EMEA_Incremental', 'Wkf_LOAD_LOCATION_STG_TO_GEOCODING', 'wkf_UPDATE_PHYS_STRUCT_GEOCODE_GLM', 
                'wkf_update_CODS_NETINV_DW_SECURE_COMPANY_NBR', 'wkf_update_phys_struct_geocode_mars', 'wkf_Load_CODS_NETINV_LEVEL3_LEGACY', 
                'wkf_Load_LOCATION_ALL_LMS', 'wkf_Load_CIRCUIT_ALL_AMDOCS_RM', 'wkf_Load_AMDOCS_RM_SERVICE', 'wkf_Load_CIRCUIT_ALL', 
                'wkf_Load_FIBER', 'wkf_Load_EQUIPMENT_All_AMDOCS_RM', 'wkf_LOAD_LOCATION_ALL_PRO', 'wkf_Load_CARD_CHASSIS_PHYSICAL_PORT', 
                'wkf_Load_LOCATION_ALL_AMDOCS_FRAB', 'wkf_Load_EQUIPMENT_ALL_GRANITE', 'wkf_Load_LOCATION_ALL_GLM', 'wkf_Load_NETEX_USOC_BILLED_CCD_SAM_LATAM_Incremental', 
                'wkf_Upd_NETEX_SUPPLIER_INV_DETAIL_SAM_LATAM', 'wkf_Load_NETEX_SUPP_INV_DTL_SAM_LATAM', 'wkf_m_Load_NETEX_STG_CIRCUIT_ASG_TSC_ALLOC_SAM_LATAM', 
                'wkf_Upd_NETEX_SUPPLIER_INV_DETAIL_SAM', 'wkf_Load_NETEX_SUPPLIER_INV_DETAIL_USAGE_SAM_Incremental', 'wkf_Load_NETEX_SUPPLIER_INV_GL_SAM_Incremental', 
                'wkf_Load_NETEX_USOC_BILLED_CCD_SAM_Incremental', 'wkf_Load_NETEX_SUPP_INV_DTL_SAM', 'wkf_m_Load_NETEX_STG_CIRCUIT_ASG_TSC_ALLOC_SAM', 
                'wkf_Load_CDW_ASL_SAM_SYNCH_NA', 'wkf_Load_CDW_ASL_SAM_SYNCH_LATAM_Tables_Refresh', 'wkf_Load_LOCATION_GLM', 
                'wkf_Load_CDW_ASL_GRANITE_SST2', 'wkf_Load_AML', 'wkf_Load_TLC_NICONV_Del', 'wkf_Update_Trail'
            ],
            'DSL_FINANCE': [
                'wkf_DSL_FINANCE_DAILY_REFRESH_MASTER', 'wkf_Load_CDW_ASL_ORAFIN', 'wkf_Load_CDW_ASL_ORAFIN_SST2', 'wkf_Load_CDW_ASL_ORAFIN_DLT2', 
                'wkf_Load_CDW_ASL_MDMFI_GLCLOSE_SST2', 'wkf_Load_CDW_ASL_SAP', 'wkf_Load_RECON_SAP', 'wkf_Invoke_GETL_MERLIN_CDW_ASL_SAP', 
                'wkf_Load_CDW_ASL_SAP_SST2', 'wkf_Load_CDW_ASL_ONLY_SAP', 'wkf_Load_CDW_ASL_SAP_DLT2', 'wkf_Load_ASL_MDMFI_CTLGLCLOSE', 
                'wkf_Load_ONESTREAM', 'wkf_Load_ONESTREAM_GL_ACCOUNT', 'wkf_Load_ASL_CDMT_BATCH_SST2', 'wkf_Load_ASL_FI_SOX_SST2', 
                'wkf_Load_DSL_FINANCE_DH_DIM_CODS_DAILY_REFRESH', 'wkf_Load_GOAT_DATA', 'wkf_Load_TMP_REV_EBS_SUM', 'wkf_Load_GOAT_ERT_DATA_ESSBASE', 
                'wkf_Load_TMP_ALL_ERT_SUM', 'wkf_Load_ASL_SAP_ONESTREAM_FLASH', 'wkf_Invoke_GETL_MERLIN_CDW_ASL_SAP_ONESTREAM_FLASH', 
                'wkf_Load_ASL_SAP_ONESTREAM_CONSOL', 'wkf_Invoke_GETL_MERLIN_CDW_ASL_SAP_ONESTREAM_CONSOL', 'wkf_Load_TMP_ALL_EBS_ORAFIN_DIFF', 
                'wkf_Load_TMP_ALL_ORAFIN_SUM', 'wkf_Load_TMP_REV_EBS_ORAFIN_DIFF', 'wkf_Load_TMP_REV_ORAFIN_SUM', 'wkf_Load_CDW_ODS_FINANCE', 
                'wkf_Load_ODS_FINANCE_DAILY_REFRESH', 'wkf_Load_CDW_ODS_FINANCE_DIM_DAILY_REFRESH', 'wkf_Load_AR_TRXN_LINE_DIST_JL', 
                'wkf_Load_AR_ACCRUAL_DETAIL_JL', 'wkf_Load_ODS_FINANCE_TABLE_REFRESH_MERLIN', 'wkf_Load_ODS_FINANCE_TABLE_REFRESH_APOLLO', 
                'wkf_Load_CDW_DSL_FINANCE', 'wkf_Load_DSL_FINANCE_DAILY_REFRESH', 'wkf_Reprocess_Missing_Values_In_FRD', 
                'wkf_Load_DH_GL_CO_ACCT_PROD_ACCT_PROD_XREF', 'wkf_Load_ZUORA', 'wkf_Load_CABS', 'wkf_Load_DASSIAN', 'wkf_Load_ENS', 
                'wkf_Load_DH_LEGACY_GL_MASTER_XREFD', 'wkf_Load_KENAN', 'wkf_Load_SWP_AVG_CUST_REVENUE_SALES', 'wkf_Load_STG_FRD_ALLOWED_ACCOUNTS', 
                'wkf_Load_NIBS', 'wkf_Load_CDW_DSL_FINANCE_DIM_DAILY_REFRESH', 'wkf_Load_MBS', 'wkf_Load_REFRESH_MATERIALIZED_VIEWS', 
                'wkf_Generate_CONTROLS_REPORT', 'wkf_COMPRESS_TABLE_PARTITIONS', 'wkf_Load_DSL_FINANCE_TABLE_REFRESH_MERLIN', 
                'wkf_Load_DSL_FINANCE_TABLE_REFRESH_APOLLO', 'wkf_Load_ASL_SAP_CURRENCY_EXCHANGE', 'wkf_Load_CURRENCY_EXCHANGE_RATE'
            ],
            'CAPEX': [
                'wkf_SCM_DAILY_CAPEX_REFRESH', 'wkf_Load_ASL_ORAFIN_SCM_CAPEX_Refresh', 'wkf_Load_CDW_ASL_FIREWORKS', 'wkf_Load_CDW_ASL_FIREWORKS_DLT2', 
                'wkf_Load_CDW_ASL_FIREWORKS_SST2', 'wkf_Load_ASL_SAP_CAPEX', 'wkf_Load_CDW_ASL_FI_SOX', 'wkf_m_Load_CAPEX_ADJUSTMENT', 
                'wkf_Load_ODS_SCM_SAP', 'wkf_Load_ODS_SCM_CAPEX_REFRESH', 'wkf_Load_DSL_SCM_CAPEX_REFRESH'
            ],
            'DATAMKTP': [
                'wkf_Generate_Past_Due_Invoices_Parameter_File', 'wkf_Load_DATAMKTP', 'wkf_Load_DATAMKTP_NPS', 'wkf_Load_DATAMKTP_STEELTHREAD_BU_UTILIZATION_file', 
                'wkf_Load_DATAMKTP_ORDERS_dlt', 'wkf_Load_DATAMKTP_REVENUE_DSLF', 'wkf_Load_DATAMKTP_MAIN_BILLING_TICKET', 'wkf_Generate_Billing_Tickets_Parameter_File', 
                'wkf_Load_DATAMKTP_CUSTOMER_BAN', 'wkf_Load_DATAMKTP_PARTNER_SALES_ORDER_LINE', 'wkf_Load_DATAMKTP_MAIN_PAST_DUE_INVOICES', 
                'wkf_Load_DATAMKTP_BILLING_TICKET', 'wkf_Load_DATAMKTP_BAN_PARTNER_SALES_ATTRIBUTES', 'wkf_Load_DATAMKTP_sleep_PAST_DUE_INVOICES', 
                'wkf_Load_DATAMKTP_Revenue_Commit_Attribution_file', 'wkf_Load_DATAMKTP_TROUBLE_TICKETS', 'wkf_Load_DATAMKTP_SURGE_SCORE', 
                'wkf_Load_DATAMKTP_CUSTOMER_dlt', 'wkf_Load_DATAMKTP_CheckStatus', 'wkf_Load_DATAMKTP_PAST_DUE_INVOICES', 'wkf_Load_DATAMKTP_PENDED_BILLING_DATA', 
                'wkf_Load_DATAMKTP_ORDER', 'wkf_Load_DATAMKTP_CUSTOMER', 'wkf_Load_ODS_SSQ_Customer_Only'
            ],
            'CODS_TN': [
                'wkf_Load_CODS_TN', 'wkf_Load_TN_CODS_DK2', 'wkf_Load_DIGRS', 'wkf_Load_ODS_SOURCE_BILLING_ACCOUNT', 'wkf_Load_CDW_ASL_SLDB_E911_SST2', 
                'wkf_Load_CDW_ASL_SLDB_E911', 'wkf_Load_CDW_ASL_SLDB_E911_DLT2', 'wkf_Load_CDW_ASL_SLDB_LNP_SST2', 'wkf_Load_CDW_ASL_SLDB_LNP_DLT2', 
                'wkf_Load_CDW_ASL_SLDB_LNP', 'wkf_Load_CDW_ASL_SLDB_SUBL_SST2', 'wkf_Load_CDW_ASL_SLDB_SUBL_DLT2', 'wkf_Load_CDW_ASL_SLDB_SUBL'
            ],
            'AIM': [
                'wkf_Load_DSL_AIM', 'wkf_Load_ACCRUAL_INSTANCE', 'wkf_Load_AML_PLANNED_COST', 'wkf_Load_ECCKT_CUST_SERV'
            ],
            'SOLAR_LUCENSE': [
                'wkf_Refresh_Solr_Lucene_Index_TNLookup', 'wkf_CONTROLLER_TN_ODS', 'wkf_LOAD_NS_TN_SERVICE_IMAGE', 'wkf_LOAD_NUMS_TN_INVENTORY', 
                'wkf_Load_UKDW_TN_DATA', 'wkf_Load_LATAM_TN_INVENTORY', 'wkf_LOAD_TNI_TN_INVENTORY', 'wkf_LOAD_NUTS_TN_INVENTORY', 
                'wkf_LOAD_PROD_TN_SERVICE_IMAGE', 'wkf_LOAD_CRIS_TN_SERVICE_IMAGE', 'wkf_Load_CNUM_NAT_TN', 'wkf_Load_CNUM_CTS_TN', 
                'wkf_Load_MARTENS_TN', 'wkf_LOAD_SDWF_TN_SERVICE_IMAGE', 'wkf_LOAD_SLDB_TN_SERVICE_IMAGE', 'wkf_LOAD_REM_TC_TN_INVENTORY', 
                'wkf_LOAD_PPL_TN_SERVICE_IMAGE', 'wkf_LOAD_PRISM_TN_INVENTORY', 'wkf_Load_LEXM_TN_INVENTORY', 'wkf_Load_PRO_TN_FEATURE_PACK_ROUTE_PLAN', 
                'wkf_Load_TN_DISCONNECT', 'wkf_LOAD_TN_LOOKUP_DELTA_MERGE'
            ],
            'DSL_MARGIN': [
                'wkf_Load_ECCKT_CUST_SERV', 'wkf_Load_DSL_Margin'
            ],
            'PLANNED_BILLED_COST': [
                'wkf_Load_AML_PLANNED_COST', 'wkf_Load_ORDER_ELEM_ECCKT_XREF', 'wkf_Load_PBC'
            ],
            'SLV': [
                'wkf_Load_Service_Lookup_Refresh', 'wkf_load_ERM_SM', 'wkf_Load_SERVICE_LOCATION_ASSET', 'wkf_Load_SERVICE_LOCATION_BILLING', 
                'wkf_Load_SERVICE_LOCATION_CLARIFY', 'wkf_Load_SERVICE_LOCATION_CODS_NETINV_ICG', 'wkf_Load_SERVICE_LOCATION_NI', 'wkf_Load_SERVICE_LOCATION_VLOCITY', 
                'wkf_Load_ODS_ASSET_VIEW', 'wkf_Load_BILLING_PRODUCT_COMPNT', 'wkf_Load_EQUIPMENT_All_LUMEN_SERVICENOW'
            ],
            'OTHERS': []  # Will be fetched from database as NOT IN all above workflows
        }
        
        # Get workflow list for the selected application
        workflow_list = workflow_mappings.get(application, [])
        
        if not workflow_list:
            return JsonResponse({
                'success': True,
                'workflows': [],
                'total': 0,
                'running': 0,
                'succeeded': 0,
                'failed': 0,
                'application': application,
                'message': f'No workflows configured for application: {application}. Please add workflow list in api_views.py'
            })
        
        # Build IN clause with workflow names
        placeholders = ', '.join([f":wf{i}" for i in range(len(workflow_list))])
        params = {f'wf{i}': wf for i, wf in enumerate(workflow_list)}
        
        # Query matching the exact RDL report structure
        query = f"""
        SELECT 
            TIR.SERVER_NAME AS grid_name,
            TIR.SUBJECT_AREA AS subject_area,
            TIR.WORKFLOW_NAME AS workflow_name,
            TIR.INSTANCE_NAME AS session_name,
            TO_CHAR(TIR.START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS start_time,
            CASE WHEN TIR.RUN_STATUS_CODE = '6' THEN NULL 
                 ELSE TO_CHAR(TIR.END_TIME, 'YYYY-MM-DD HH24:MI:SS') 
            END AS end_time,
            DECODE(RUN_STATUS_CODE, 1, 'Succeeded', 2, 'Disabled', 3, 'Failed', 
                   4, 'Stopped', 5, 'Aborted', 6, 'Running') AS status
        FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
        WHERE RUN_STATUS_CODE IN (1,3,4,5,6)
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        AND WORKFLOW_NAME IN ({placeholders})
        ORDER BY START_TIME DESC
        """
        
        rows = fetch_all(query, params)
        
        # Calculate statistics
        total = len(rows)
        running = sum(1 for r in rows if r.get('status') == 'Running')
        succeeded = sum(1 for r in rows if r.get('status') == 'Succeeded')
        failed = sum(1 for r in rows if r.get('status') in ['Failed', 'Stopped', 'Aborted'])
        
        # Convert rows to list of dicts
        workflows = []
        for row in rows:
            workflows.append({
                'grid_name': row.get('grid_name'),
                'subject_area': row.get('subject_area'),
                'workflow_name': row.get('workflow_name'),
                'session_name': row.get('session_name'),
                'start_time': row.get('start_time'),
                'end_time': row.get('end_time'),
                'status': row.get('status')
            })
        
        return JsonResponse({
            'success': True,
            'workflows': workflows,
            'total': total,
            'running': running,
            'succeeded': succeeded,
            'failed': failed,
            'application': application,
            'workflow_count': len(workflow_list)
        })
    
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error fetching application data: {str(e)}',
            'workflows': []
        }, status=500)


@require_http_methods(["POST"])
def icsm_check_entry(request):
    """
    API endpoint to insert a success entry into ICSM.APP_CONTROL_STATUS table
    """
    import json
    from portal.db.oracle_client import execute_query
    
    try:
        data = json.loads(request.body)
        application_name = data.get('application_name', '').strip()
        dependency_name = data.get('dependency_name', '').strip()
        
        if not application_name or not dependency_name:
            return JsonResponse({
                'success': False,
                'message': 'Application Name and Dependency Name are required'
            }, status=400)
        
        # Prepare the INSERT statement
        insert_query = """
            INSERT INTO ICSM.APP_CONTROL_STATUS 
            (APPLICATION_NAME, DEPENDENCY_NAME, START_DT, END_DT, STATUS_CD)
            VALUES (:app_name, :dep_name, SYSDATE, SYSDATE, 'Succeeded')
        """
        
        # Execute the INSERT
        execute_query(insert_query, {
            'app_name': application_name,
            'dep_name': dependency_name
        })
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully inserted entry for {application_name} - {dependency_name} with status "Succeeded"'
        })
        
    except Exception as e:
        print(f"Error inserting ICSM check entry: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Failed to insert entry: {str(e)}'
        }, status=500)

