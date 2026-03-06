"""
ERP and MDM AI Insights
========================

Provides job status insights for ERP and MDM applications:
- Failed job counts
- Succeeded job counts  
- Running/Pending job counts
- Summary statistics
"""

from typing import Dict, List, Any
from portal.services.level3_service import get_erp_job_status, get_mdm_job_status, get_erp_last_8_runs, get_erp_current_run_details


def get_erp_run_history():
    """
    Get last 8 ERP runs with AI insights for each run.
    ERP runs every 4 hours: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
    
    Returns:
        Dictionary with last 8 runs summary and current run details
    """
    try:
        # Get last 8 runs summary
        last_8_runs = get_erp_last_8_runs()
        
        # Get current (latest) run full details
        current_run_jobs = get_erp_current_run_details()
        
        if not last_8_runs:
            return {
                'success': False,
                'message': 'No ERP run history available',
                'last_8_runs': [],
                'current_run': {
                    'total_jobs': 0,
                    'completed': 0,
                    'running': 0,
                    'failed': 0,
                    'suspended': 0,
                    'jobs': [],
                    'failed_jobs': [],
                    'succeeded_jobs': [],
                    'running_jobs': [],
                    'suspended_jobs': [],
                }
            }
        
        # Process last 8 runs data with Duration and SLA
        from datetime import datetime
        runs_summary = []
        for run in last_8_runs:
            start_time = run.get('start_time_mst', '')
            end_time = run.get('end_time_mst', '')
            duration_mins = run.get('duration_minutes', 0)
            sla_minutes = run.get('sla_minutes', 240)  # 4 hours SLA
            
            # Calculate SLA status
            if run.get('run_status') == 'RUNNING':
                sla_status = 'IN PROGRESS'
                sla_met_by = None
            elif duration_mins and duration_mins > 0:
                sla_diff = sla_minutes - duration_mins
                if sla_diff >= 0:
                    sla_status = 'MET'
                    sla_met_by = sla_diff
                else:
                    sla_status = 'MISSED'
                    sla_met_by = abs(sla_diff)
            else:
                sla_status = 'UNKNOWN'
                sla_met_by = None
            
            runs_summary.append({
                'run_label': run.get('run_label', 'Unknown'),
                'start_time': start_time,
                'end_time': end_time if end_time else 'N/A',
                'total_jobs': run.get('total_jobs', 0),
                'succeeded': run.get('succeeded', 0),
                'running': run.get('running', 0),
                'failed': run.get('failed', 0),
                'suspended': run.get('suspended', 0),
                'success_rate': run.get('success_rate', 0),
                'run_status': run.get('run_status', 'UNKNOWN'),
                'duration_minutes': duration_mins,
                'sla_status': sla_status,
                'sla_met_by': sla_met_by,
            })
        
        # Process current run details
        failed_jobs = []
        succeeded_jobs = []
        running_jobs = []
        suspended_jobs = []
        
        for job in current_run_jobs:
            status = str(job.get('status', 'UNKNOWN')).upper()
            duration_mins = job.get('duration_minutes', 0)
            
            job_info = {
                'asset_name': job.get('asset_name', 'Unknown'),
                'subtask_asset_name': job.get('subtask_asset_name', 'Unknown'),
                'location': job.get('location', 'Unknown'),
                'start_time': job.get('start_time_mst', 'N/A'),
                'end_time': job.get('end_time_mst', 'N/A') if job.get('end_time_mst') else 'Running...',
                'subtask_count': job.get('subtask_count', 0),
                'duration_minutes': duration_mins,
                'status': status,
            }
            
            if status == 'FAILED':
                failed_jobs.append(job_info)
            elif status == 'SUCCESS':
                succeeded_jobs.append(job_info)
            elif status == 'RUNNING':
                running_jobs.append(job_info)
            elif status in ['SUSPENDED', 'CHILD_SUSPENDED']:
                suspended_jobs.append(job_info)
        
        total_current = len(current_run_jobs)
        completed_current = len(succeeded_jobs)
        running_current = len(running_jobs)
        failed_current = len(failed_jobs)
        suspended_current = len(suspended_jobs)
        
        return {
            'success': True,
            'last_8_runs': runs_summary,
            'current_run': {
                'total_jobs': total_current,
                'completed': completed_current,
                'running': running_current,
                'failed': failed_current,
                'suspended': suspended_current,
                'success_rate': round((completed_current / total_current * 100), 1) if total_current > 0 else 0,
                'jobs': current_run_jobs,
                'failed_jobs': failed_jobs,
                'succeeded_jobs': succeeded_jobs,
                'running_jobs': running_jobs,
                'suspended_jobs': suspended_jobs,
            }
        }
        
    except Exception as e:
        print(f"Error getting ERP run history: {e}")
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'last_8_runs': [],
            'current_run': {
                'total_jobs': 0,
                'completed': 0,
                'running': 0,
                'failed': 0,
                'suspended': 0,
                'jobs': [],
                'failed_jobs': [],
                'succeeded_jobs': [],
                'running_jobs': [],
                'suspended_jobs': [],
            }
        }


def get_erp_insights() -> Dict[str, Any]:
    """
    Get AI insights for ERP jobs.
    
    Returns:
        Dictionary with ERP job statistics and details
    """
    try:
        erp_jobs = get_erp_job_status()
        
        if not erp_jobs:
            return {
                'success': False,
                'message': 'No ERP job data available',
                'total_jobs': 0,
                'failed_count': 0,
                'succeeded_count': 0,
                'running_count': 0,
                'suspended_count': 0,
                'not_started_count': 0,
                'fail_rate': 0,
                'success_rate': 0,
                'failed_jobs': [],
                'succeeded_jobs': [],
                'running_jobs': [],
                'suspended_jobs': [],
                'not_started_jobs': [],
            }
        
        # Categorize jobs by status
        failed_jobs = []
        succeeded_jobs = []
        running_jobs = []
        suspended_jobs = []
        not_started_jobs = []
        
        for job in erp_jobs:
            status = str(job.get('status', 'UNKNOWN')).upper()
            
            job_info = {
                'asset_name': job.get('asset_name', 'Unknown'),
                'subtask_asset_name': job.get('subtask_asset_name', 'Unknown'),
                'location': job.get('location', 'Unknown'),
                'start_time': job.get('start_time_mst', 'N/A'),
                'end_time': job.get('end_time_mst', 'N/A'),
                'status': status,
            }
            
            if status == 'FAILED':
                failed_jobs.append(job_info)
            elif status == 'SUCCESS':
                succeeded_jobs.append(job_info)
            elif status == 'RUNNING':
                running_jobs.append(job_info)
            elif status in ['SUSPENDED', 'CHILD_SUSPENDED']:
                suspended_jobs.append(job_info)
            else:
                not_started_jobs.append(job_info)
        
        # Calculate summary
        total_jobs = len(erp_jobs)
        failed_count = len(failed_jobs)
        succeeded_count = len(succeeded_jobs)
        running_count = len(running_jobs)
        suspended_count = len(suspended_jobs)
        not_started_count = len(not_started_jobs)
        fail_rate = round((failed_count / total_jobs * 100), 1) if total_jobs > 0 else 0
        success_rate = round((succeeded_count / total_jobs * 100), 1) if total_jobs > 0 else 0
        
        return {
            'success': True,
            'total_jobs': total_jobs,
            'failed_count': failed_count,
            'succeeded_count': succeeded_count,
            'running_count': running_count,
            'suspended_count': suspended_count,
            'not_started_count': not_started_count,
            'fail_rate': fail_rate,
            'success_rate': success_rate,
            'failed_jobs': failed_jobs,
            'succeeded_jobs': succeeded_jobs,
            'running_jobs': running_jobs,
            'suspended_jobs': suspended_jobs,
            'not_started_jobs': not_started_jobs,
        }
        
    except Exception as e:
        print(f"Error getting ERP insights: {e}")
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'total_jobs': 0,
            'failed_count': 0,
            'succeeded_count': 0,
            'running_count': 0,
            'suspended_count': 0,
            'not_started_count': 0,
            'fail_rate': 0,
            'success_rate': 0,
            'failed_jobs': [],
            'succeeded_jobs': [],
            'running_jobs': [],
            'suspended_jobs': [],
            'not_started_jobs': [],
        }


def get_mdm_insights() -> Dict[str, Any]:
    """
    Get AI insights for MDM jobs.
    
    Returns:
        Dictionary with MDM job statistics and details
    """
    try:
        mdm_jobs = get_mdm_job_status()
        
        if not mdm_jobs:
            return {
                'success': False,
                'message': 'No MDM job data available',
                'total_jobs': 0,
                'failed_count': 0,
                'succeeded_count': 0,
                'running_count': 0,
                'not_started_count': 0,
                'fail_rate': 0,
                'success_rate': 0,
                'failed_jobs': [],
                'succeeded_jobs': [],
                'running_jobs': [],
                'not_started_jobs': [],
            }
        
        # Categorize jobs by status
        failed_jobs = []
        succeeded_jobs = []
        running_jobs = []
        not_started_jobs = []
        
        for job in mdm_jobs:
            status = str(job.get('status', 'UNKNOWN')).upper()
            
            job_info = {
                'asset_name': job.get('asset_name', 'Unknown'),
                'start_time': job.get('start_time', 'N/A'),
                'end_time': job.get('end_time', 'N/A'),
                'status': status,
                'location': 'MAPDQPRD',  # MDM jobs don't have location field
            }
            
            if status == 'FAILED':
                failed_jobs.append(job_info)
            elif status == 'SUCCESS':
                succeeded_jobs.append(job_info)
            elif status == 'RUNNING':
                running_jobs.append(job_info)
            else:
                not_started_jobs.append(job_info)
        
        # Calculate summary
        total_jobs = len(mdm_jobs)
        failed_count = len(failed_jobs)
        succeeded_count = len(succeeded_jobs)
        running_count = len(running_jobs)
        not_started_count = len(not_started_jobs)
        fail_rate = round((failed_count / total_jobs * 100), 1) if total_jobs > 0 else 0
        success_rate = round((succeeded_count / total_jobs * 100), 1) if total_jobs > 0 else 0
        
        return {
            'success': True,
            'total_jobs': total_jobs,
            'failed_count': failed_count,
            'succeeded_count': succeeded_count,
            'running_count': running_count,
            'not_started_count': not_started_count,
            'fail_rate': fail_rate,
            'success_rate': success_rate,
            'failed_jobs': failed_jobs,
            'succeeded_jobs': succeeded_jobs,
            'running_jobs': running_jobs,
            'not_started_jobs': not_started_jobs,
        }
        
    except Exception as e:
        print(f"Error getting MDM insights: {e}")
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'total_jobs': 0,
            'failed_count': 0,
            'succeeded_count': 0,
            'running_count': 0,
            'not_started_count': 0,
            'fail_rate': 0,
            'success_rate': 0,
            'failed_jobs': [],
            'succeeded_jobs': [],
            'running_jobs': [],
            'not_started_jobs': [],
        }
