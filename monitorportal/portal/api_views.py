# portal/api_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
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
        # Generate all Level3 job statuses
        data = []
        num_records = random.randint(30, 50)
        
        statuses = ["Succeeded", "Failed", "Running", "Stopped", "Terminated", "Waiting"]
        status_weights = [60, 15, 10, 5, 5, 5]
        
        for i in range(num_records):
            start_time = base_time - timedelta(hours=random.randint(0, 12))
            status = random.choices(statuses, weights=status_weights)[0]
            end_time = start_time + timedelta(minutes=random.randint(10, 120)) if status not in ["Running", "Waiting"] else None
            
            record = {
                "grid_name": random.choice(grid_names),
                "subject_area": random.choice(subject_areas),
                "workflow_name": random.choice(workflows),
                "session_name": random.choice(sessions),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else None,
                "status": status
            }
            data.append(record)
        
        # Sort by subject_area first, then status priority
        priority = {"Failed": 1, "Stopped": 1, "Terminated": 1, "Running": 2, "Succeeded": 3, "Waiting": 4}
        data.sort(key=lambda x: (x["subject_area"], priority.get(x["status"], 5), x["start_time"]), reverse=False)
        
        # Create app-wise summary
        from collections import defaultdict
        app_summary = defaultdict(lambda: {"total": 0, "succeeded": 0, "failed": 0, "running": 0, "other": 0})
        for record in data:
            app = record["subject_area"]
            app_summary[app]["total"] += 1
            status_lower = record["status"].lower()
            if status_lower == "succeeded":
                app_summary[app]["succeeded"] += 1
            elif status_lower in ["failed", "stopped", "terminated"]:
                app_summary[app]["failed"] += 1
            elif status_lower == "running":
                app_summary[app]["running"] += 1
            else:
                app_summary[app]["other"] += 1
        
        summary = {
            "total_jobs": len(data),
            "by_application": dict(app_summary),
            "total_succeeded": sum(r["status"] == "Succeeded" for r in data),
            "total_failed": sum(r["status"] in ["Failed", "Stopped", "Terminated"] for r in data),
            "total_running": sum(r["status"] == "Running" for r in data),
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
    """
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
    
    result = {
        "app_slug": app_slug,
        "report_slug": report_slug,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success": False,
        "data": [],
        "summary": None,
        "error": None,
    }
    
    try:
        # Fetch REAL data from Oracle database
        if report_slug == "lvl3-failed-job-status":
            summary, data = get_level3_failed_jobs()
            result["summary"] = summary
            result["data"] = data
            
        elif report_slug == "lvl3-failed-with-error":
            result["data"] = get_level3_failed_with_error()
            
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
