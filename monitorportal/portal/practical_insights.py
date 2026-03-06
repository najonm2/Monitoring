"""
Practical Insights Service
===========================

Provides real-time insights for Informatica job monitoring:
- Long-running sessions analysis
- Failed sessions with error details
- Error pattern matching and recommendations
- Team assignment (DBA vs DEV) support
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from portal.services.level3_service import (
    get_level3_long_running,
    get_level3_failed_with_error,
    get_level3_failed_jobs,
)


# ==================== Error Pattern Matching ====================

ERROR_PATTERNS = {
    # Database connection errors
    'db_connection': {
        'patterns': [
            r'ORA-\d+.*connection',
            r'unable to connect',
            r'connection refused',
            r'connection timeout',
            r'network.*error',
            r'TNS.*error',
            r'listener.*not.*available',
        ],
        'category': 'Database Connection',
        'severity': 'HIGH',
        'recommendations': [
            'Check database connectivity (ping/tnsping)',
            'Verify TNS configuration and listener status',
            'Check network firewalls and routing',
            'Verify database credentials',
            'Contact DBA team for database status',
        ],
        'assigned_to': 'DBA',
    },
    
    # Table/Object not found
    'object_not_found': {
        'patterns': [
            r'ORA-00942',  # Table or view does not exist
            r'table.*not.*found',
            r'view.*not.*found',
            r'object.*not.*found',
            r'invalid.*object',
        ],
        'category': 'Database Object Missing',
        'severity': 'CRITICAL',
        'recommendations': [
            'Check if source/target table exists',
            'Verify schema permissions and grants',
            'Check for recent DDL changes',
            'Confirm table naming and schema prefix',
            'Contact DBA team to create/restore object',
        ],
        'assigned_to': 'DBA',
    },
    
    # Space/Tablespace issues
    'space_issue': {
        'patterns': [
            r'ORA-01653',  # Unable to extend table
            r'tablespace.*full',
            r'out of space',
            r'disk.*full',
            r'unable to extend',
        ],
        'category': 'Space/Tablespace Full',
        'severity': 'CRITICAL',
        'recommendations': [
            'Check tablespace utilization',
            'Add datafiles or extend tablespace',
            'Purge/archive old data',
            'Check for runaway queries filling temp space',
            'Contact DBA team to add space',
        ],
        'assigned_to': 'DBA',
    },
    
    # Lock/Deadlock issues
    'lock_issue': {
        'patterns': [
            r'ORA-00060',  # Deadlock detected
            r'deadlock',
            r'lock.*timeout',
            r'resource.*busy',
            r'ORA-00054',  # Resource busy
        ],
        'category': 'Lock/Deadlock',
        'severity': 'HIGH',
        'recommendations': [
            'Identify blocking sessions and kill if needed',
            'Review concurrent job schedules',
            'Check for long-running transactions',
            'Optimize query to reduce lock time',
            'Schedule jobs to avoid conflicts',
        ],
        'assigned_to': 'DBA',
    },
    
    # Data type/conversion errors
    'data_type_error': {
        'patterns': [
            r'ORA-01722',  # Invalid number
            r'ORA-01858',  # Non-numeric character in date
            r'ORA-06502',  # Numeric or value error
            r'data type.*mismatch',
            r'invalid.*datatype',
            r'conversion.*error',
        ],
        'category': 'Data Type/Conversion Error',
        'severity': 'MEDIUM',
        'recommendations': [
            'Check source data for invalid values',
            'Add data validation/cleansing rules',
            'Use TO_NUMBER/TO_DATE with error handling',
            'Review mapping data type compatibility',
            'Contact DEV team to fix transformation logic',
        ],
        'assigned_to': 'DEV',
    },
    
    # File/Directory errors
    'file_error': {
        'patterns': [
            r'file.*not.*found',
            r'directory.*not.*found',
            r'permission.*denied',
            r'access.*denied',
            r'cannot.*open.*file',
        ],
        'category': 'File/Directory Error',
        'severity': 'HIGH',
        'recommendations': [
            'Verify file path and existence',
            'Check file permissions and ownership',
            'Ensure directory structure exists',
            'Check for typos in file path',
            'Verify shared drive/mount availability',
        ],
        'assigned_to': 'DEV',
    },
    
    # Memory errors
    'memory_error': {
        'patterns': [
            r'out of memory',
            r'memory.*allocation.*failed',
            r'java.*heap.*space',
            r'ORA-04030',  # Out of process memory
        ],
        'category': 'Memory Error',
        'severity': 'HIGH',
        'recommendations': [
            'Increase session memory allocation',
            'Optimize transformation to use less memory',
            'Process data in smaller batches',
            'Check for memory leaks in custom code',
            'Contact infrastructure team for server memory',
        ],
        'assigned_to': 'DEV',
    },
    
    # Source/Target errors
    'source_target_error': {
        'patterns': [
            r'source.*error',
            r'target.*error',
            r'failed to read',
            r'failed to write',
            r'no rows.*read',
        ],
        'category': 'Source/Target Error',
        'severity': 'MEDIUM',
        'recommendations': [
            'Verify source data availability',
            'Check target table structure',
            'Verify connection objects configuration',
            'Check for data freshness issues',
            'Review session logs for specific errors',
        ],
        'assigned_to': 'DEV',
    },
    
    # Workflow/Scheduling errors
    'workflow_error': {
        'patterns': [
            r'workflow.*failed',
            r'session.*failed',
            r'task.*failed',
            r'scheduler.*error',
            r'dependency.*not.*met',
        ],
        'category': 'Workflow/Scheduling Error',
        'severity': 'MEDIUM',
        'recommendations': [
            'Check workflow dependency chain',
            'Verify preceding task completion',
            'Review workflow schedule and triggers',
            'Check for parallel execution conflicts',
            'Review workflow logic and links',
        ],
        'assigned_to': 'DEV',
    },
}


def analyze_error(error_message: str) -> Dict[str, Any]:
    """
    Analyze error message and provide recommendations.
    
    Args:
        error_message: Error message from failed job
        
    Returns:
        Dictionary with error analysis and recommendations
    """
    if not error_message:
        return {
            'category': 'Unknown Error',
            'severity': 'MEDIUM',
            'recommendations': [
                'Check session logs for detailed error information',
                'Review workflow run history',
                'Contact support with job details',
            ],
            'assigned_to': 'DEV',
            'matched_pattern': None,
        }
    
    error_lower = error_message.lower()
    
    # Try to match error patterns
    for pattern_key, pattern_info in ERROR_PATTERNS.items():
        for pattern in pattern_info['patterns']:
            if re.search(pattern, error_lower, re.IGNORECASE):
                return {
                    'category': pattern_info['category'],
                    'severity': pattern_info['severity'],
                    'recommendations': pattern_info['recommendations'],
                    'assigned_to': pattern_info['assigned_to'],
                    'matched_pattern': pattern_key,
                    'error_snippet': error_message[:200],  # First 200 chars
                }
    
    # No pattern matched - generic response
    return {
        'category': 'General Error',
        'severity': 'MEDIUM',
        'recommendations': [
            'Review full error message in session logs',
            'Check for recent code/configuration changes',
            'Search Informatica knowledge base',
            'Contact support if error persists',
        ],
        'assigned_to': 'DEV',
        'matched_pattern': None,
        'error_snippet': error_message[:200],
    }


# ==================== Insights Generation ====================

def get_practical_insights(long_running=None, failed_with_errors=None, all_failed=None) -> Dict[str, Any]:
    """
    Get practical insights for job monitoring dashboard.
    
    Args:
        long_running: Pre-fetched long running sessions (optional, fetches if None)
        failed_with_errors: Pre-fetched failed sessions (optional, fetches if None)
        all_failed: Pre-fetched all failed jobs (optional, fetches if None)
    
    Returns:
        Dictionary with all insights including:
        - Long-running sessions
        - Failed sessions with errors
        - Summary statistics
        - Recommendations
    """
    try:
        # Fetch data only if not provided (avoid duplicate queries)
        if long_running is None:
            long_running = get_level3_long_running()
        if failed_with_errors is None:
            failed_with_errors = get_level3_failed_with_error()
        if all_failed is None:
            summary, all_failed = get_level3_failed_jobs()
        else:
            summary = {'total_failed': len(all_failed)}
        
        # Process long-running sessions
        long_running_insights = []
        for session in long_running:
            current_min = session.get('CURRENT_DURATION_MIN', 0)
            avg_min = session.get('AVG_DURATION_MIN', 0)
            
            if avg_min > 0:
                percent_over = ((current_min - avg_min) / avg_min) * 100
            else:
                percent_over = 0
            
            long_running_insights.append({
                'session_name': session.get('SESSION_NAME', 'Unknown'),
                'workflow_name': session.get('WORKFLOW_NAME', 'Unknown'),
                'grid_name': session.get('GRID_NAME', 'Unknown'),
                'subject_area': session.get('SUBJECT_AREA', 'Unknown'),
                'start_time': session.get('START_TIME'),
                'current_duration_min': current_min,
                'avg_duration_min': avg_min,
                'percent_over_avg': round(percent_over, 1),
                'severity': 'CRITICAL' if percent_over > 200 else 'HIGH' if percent_over > 100 else 'MEDIUM',
            })
        
        # Process failed sessions with error analysis
        failed_insights = []
        dba_tasks = []
        dev_tasks = []
        
        for failed_job in failed_with_errors:
            error_msg = failed_job.get('ERROR_MESSAGE', '')
            error_analysis = analyze_error(error_msg)
            
            insight = {
                'session_name': failed_job.get('SESSION_NAME', 'Unknown'),
                'workflow_name': failed_job.get('WORKFLOW_NAME', 'Unknown'),
                'grid_name': failed_job.get('GRID_NAME', 'Unknown'),
                'subject_area': failed_job.get('SUBJECT_AREA', 'Unknown'),
                'start_time': failed_job.get('START_TIME'),
                'end_time': failed_job.get('END_TIME'),
                'status': failed_job.get('STATUS', 'Failed'),
                'error_message': error_msg,
                'error_category': error_analysis['category'],
                'error_severity': error_analysis['severity'],
                'recommendations': error_analysis['recommendations'],
                'assigned_to': error_analysis['assigned_to'],
            }
            
            failed_insights.append(insight)
            
            # Categorize by team
            if error_analysis['assigned_to'] == 'DBA':
                dba_tasks.append(insight)
            else:
                dev_tasks.append(insight)
        
        # Calculate summary statistics
        total_failed = len(all_failed)
        failed_with_errors_count = len(failed_with_errors)
        failed_without_errors = total_failed - failed_with_errors_count
        long_running_count = len(long_running)
        
        # Critical issues (high severity failures + long running over 200% avg)
        critical_failures = sum(1 for f in failed_insights if f['error_severity'] == 'CRITICAL')
        critical_long_running = sum(1 for lr in long_running_insights if lr['severity'] == 'CRITICAL')
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_failed': total_failed,
                'failed_pending_restart': failed_with_errors_count,
                'failed_already_restarted': failed_without_errors,
                'long_running_sessions': long_running_count,
                'critical_issues': critical_failures + critical_long_running,
                'dba_tasks_count': len(dba_tasks),
                'dev_tasks_count': len(dev_tasks),
            },
            'long_running_sessions': long_running_insights,
            'failed_sessions': failed_insights,
            'dba_tasks': dba_tasks,
            'dev_tasks': dev_tasks,
            'health_status': _calculate_health_status(
                total_failed,
                failed_with_errors_count,
                long_running_count,
                critical_failures + critical_long_running
            ),
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
        }


def _calculate_health_status(total_failed: int, pending_failed: int, long_running: int, critical: int) -> Dict[str, Any]:
    """Calculate overall system health status."""
    
    if critical > 5 or pending_failed > 10:
        status = 'CRITICAL'
        color = 'danger'
        message = 'Multiple critical issues require immediate attention'
    elif critical > 0 or pending_failed > 5 or long_running > 10:
        status = 'WARNING'
        color = 'warning'
        message = 'Several issues detected, monitor closely'
    elif total_failed > 0 or long_running > 0:
        status = 'ATTENTION'
        color = 'info'
        message = 'Minor issues detected, routine monitoring recommended'
    else:
        status = 'HEALTHY'
        color = 'success'
        message = 'All systems operating normally'
    
    return {
        'status': status,
        'color': color,
        'message': message,
    }


# ==================== Export Functions ====================

def get_insights_for_team(team: str) -> List[Dict[str, Any]]:
    """
    Get insights filtered by team (DBA or DEV).
    
    Args:
        team: 'DBA' or 'DEV'
        
    Returns:
        List of insights assigned to that team
    """
    insights = get_practical_insights()
    
    if not insights.get('success'):
        return []
    
    if team.upper() == 'DBA':
        return insights.get('dba_tasks', [])
    elif team.upper() == 'DEV':
        return insights.get('dev_tasks', [])
    else:
        return insights.get('failed_sessions', [])
