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
