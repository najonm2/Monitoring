"""
Service to fetch and store Informatica Cloud task status (ERP-related only)

Integration with: https://usw3.dm1-us.informaticacloud.com/active-bpel/services/tf/status/

Features:
- Fetches only ERP-related tasks (filters by workflow name)
- Captures suspended and restart data
- Memory-efficient: stores only 2 days of data (~50-100KB)
- Auto-cleanup of expired records
"""

import requests
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from portal.models import InformaticaTaskStatus

logger = logging.getLogger(__name__)

# ERP-specific keywords to filter tasks
ERP_KEYWORDS = [
    'ERP',
    'SAPS4',
    'DATAHUB',
    'CDW_DSL_ERP',
    'ASL_SAPS4',
    'ASL_ERP',
]

# Status codes to capture
CAPTURE_STATUSES = ['SUSPENDED', 'COMPLETED', 'FAILED', 'RESTARTED']


class InformaticaCloudAPI:
    """
    Informatica Cloud API client for fetching task status
    """
    
    def __init__(self):
        """Initialize with API credentials from settings"""
        self.base_url = getattr(settings, 'INFORMATICA_CLOUD_URL', 
                               'https://usw3.dm1-us.informaticacloud.com/active-bpel/services')
        self.username = getattr(settings, 'INFORMATICA_CLOUD_USER', '')
        self.password = getattr(settings, 'INFORMATICA_CLOUD_PASSWORD', '')
        self.timeout = 30
    
    def is_configured(self):
        """Check if API credentials are configured"""
        return bool(self.username and self.password)
    
    def fetch_task_status(self):
        """
        Fetch task status from Informatica Cloud API
        
        API: GET /tf/status/
        Returns: List of tasks (max 200 rows per request)
        
        Returns:
            list: Task data from API, or empty list if not configured/error
        """
        if not self.is_configured():
            logger.warning("Informatica Cloud API credentials not configured")
            return []
        
        try:
            url = f"{self.base_url}/tf/status/"
            
            # For paginated results (API returns max 200 rows)
            # You may need to implement pagination if >200 tasks
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=self.timeout,
                headers={'Accept': 'application/json'}
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse response (structure depends on Informatica API format)
            # Typical structure: {tasks: [{id, name, status, ...}]}
            tasks = data.get('tasks', []) if isinstance(data, dict) else data
            
            logger.info(f"Fetched {len(tasks)} tasks from Informatica Cloud API")
            return tasks
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Informatica Cloud API: {e}")
            return []
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching from Informatica Cloud API: {e}")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Informatica Cloud API: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching task status: {e}")
            return []
    
    @staticmethod
    def is_erp_related(task_name):
        """Check if task is ERP-related by matching keywords"""
        task_upper = str(task_name).upper()
        return any(keyword in task_upper for keyword in ERP_KEYWORDS)
    
    @staticmethod
    def extract_erp_location(task_name):
        """Extract ERP location from task name"""
        locations = {
            'CDW_DSL_ERP': 'CDW_DSL_ERP',
            'ASL_SAPS4': 'CDW_ASL_SAPS4',
            'ASL_ERP': 'ASL_ERP_DATAHUB',
        }
        
        task_upper = str(task_name).upper()
        for key, location in locations.items():
            if key in task_upper:
                return location
        return None
    
    def sync_task_status(self):
        """
        Fetch from API and store ERP-related tasks in database
        
        Returns:
            dict: Summary of synced data
        """
        # Fetch from API
        all_tasks = self.fetch_task_status()
        
        if not all_tasks:
            return {
                'status': 'error',
                'message': 'No tasks fetched from API',
                'tasks_processed': 0,
                'erp_tasks_stored': 0,
            }
        
        # Filter for ERP and capture statuses
        erp_tasks = [
            t for t in all_tasks
            if self.is_erp_related(t.get('name', ''))
            and t.get('status', '').upper() in CAPTURE_STATUSES
        ]
        
        logger.info(f"Filtered {len(erp_tasks)} ERP tasks from {len(all_tasks)} total")
        
        # Store in database
        stored_count = 0
        updated_count = 0
        
        for task in erp_tasks:
            task_id = task.get('id') or task.get('taskId')
            task_name = task.get('name', '')
            
            if not task_id:
                continue
            
            # Prepare data for storage
            task_status = task.get('status', 'UNKNOWN').upper()
            
            # Try to get or create record
            obj, created = InformaticaTaskStatus.objects.update_or_create(
                task_id=str(task_id),
                defaults={
                    'task_name': task_name,
                    'status': task_status,
                    'is_erp_related': True,
                    'erp_location': self.extract_erp_location(task_name),
                    'workflow_name': task.get('workflowName', task_name),
                    'restart_count': task.get('restartCount', 0),
                    'original_suspend_at': self._parse_datetime(
                        task.get('suspendedAt')
                    ),
                    'last_restart_at': self._parse_datetime(
                        task.get('lastRestartTime')
                    ),
                    'restart_completed_at': self._parse_datetime(
                        task.get('restartCompletedTime')
                    ),
                    'restart_completed_status': task.get('completionStatus'),
                    'restart_notes': task.get('notes', ''),
                }
            )
            
            if created:
                stored_count += 1
            else:
                updated_count += 1
        
        return {
            'status': 'success',
            'message': f'Synced {stored_count} new and {updated_count} updated ERP tasks',
            'tasks_processed': len(all_tasks),
            'erp_tasks_stored': stored_count,
            'erp_tasks_updated': updated_count,
        }
    
    @staticmethod
    def _parse_datetime(datetime_str):
        """Parse datetime string from Informatica API"""
        if not datetime_str:
            return None
        
        try:
            # Handle various datetime formats
            from dateutil import parser
            dt = parser.parse(str(datetime_str))
            # Ensure timezone aware
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        except Exception as e:
            logger.warning(f"Could not parse datetime '{datetime_str}': {e}")
            return None


def get_informatica_task_status():
    """
    Fetch and store ERP task status from Informatica Cloud
    
    This function:
    1. Connects to Informatica Cloud API
    2. Filters for ERP-related tasks only
    3. Captures suspended and restart data
    4. Stores in database with 2-day expiration
    5. Auto-cleans up expired records
    
    Returns:
        dict: Status and summary of operation
    """
    api = InformaticaCloudAPI()
    
    # Check if configured
    if not api.is_configured():
        return {
            'status': 'not_configured',
            'message': 'Informatica Cloud API credentials not configured in settings',
        }
    
    # Sync from API
    result = api.sync_task_status()
    
    # Cleanup expired records
    expired_count, _ = InformaticaTaskStatus.cleanup_expired()
    if expired_count > 0:
        logger.info(f"Cleaned up {expired_count} expired task records")
        result['expired_records_deleted'] = expired_count
    
    return result


def get_erp_suspended_tasks():
    """Get all currently suspended ERP tasks"""
    return InformaticaTaskStatus.get_suspended_tasks()


def get_erp_restarted_tasks():
    """Get all ERP tasks that have been restarted and completed"""
    return InformaticaTaskStatus.get_restarted_tasks()


def get_erp_task_summary():
    """Get summary statistics of ERP task tracking"""
    return InformaticaTaskStatus.get_erp_summary()
