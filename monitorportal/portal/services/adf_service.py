"""
Azure Data Factory (ADF) Integration Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Handles connection to ADF metadata database via ODBC DSN
Fetches pipeline runs, activities, and execution history
"""

import pyodbc
import logging
from datetime import datetime, timedelta
from django.conf import settings
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ADFConnectionError(Exception):
    """Raised when ADF connection fails"""
    pass


class ADFQueryError(Exception):
    """Raised when ADF query fails"""
    pass


class ADFDataService:
    """Service for fetching data from Azure Data Factory metadata"""
    
    def __init__(self):
        """Initialize ADF Service with DSN from settings"""
        self.dsn = getattr(settings, 'ADF_DSN', 'ADF_Metadata_DSN')
        self.connection_string = f'DSN={self.dsn};'
        self.timeout = 30
    
    @property
    def is_configured(self) -> bool:
        """Check if ADF DSN is configured"""
        return bool(self.dsn)
    
    def connect(self) -> pyodbc.Connection:
        """
        Create ODBC connection to ADF database
        
        Returns:
            pyodbc.Connection: Database connection
            
        Raises:
            ADFConnectionError: If connection fails
        """
        try:
            conn = pyodbc.connect(self.connection_string, timeout=self.timeout)
            logger.info(f"✅ Connected to ADF DSN: {self.dsn}")
            return conn
        except pyodbc.Error as e:
            error_msg = f"ADF Connection failed: {str(e)}"
            logger.error(error_msg)
            raise ADFConnectionError(error_msg)
    
    def test_connection(self) -> bool:
        """
        Test ADF database connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            logger.info("✅ ADF connection test passed")
            return True
        except Exception as e:
            logger.error(f"❌ ADF connection test failed: {e}")
            return False
    
    def get_recent_pipeline_runs(
        self,
        days: int = 7,
        limit: int = 100
    ) -> List[Tuple]:
        """
        Fetch recent ADF pipeline runs
        
        Args:
            days: Number of days to look back (default: 7)
            limit: Maximum number of runs to return (default: 100)
        
        Returns:
            List[Tuple]: Pipeline run records
            
        Example return:
            [
                (run_id, pipeline_name, start_time, end_time, status, duration_minutes),
                ...
            ]
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = f"""
            SELECT TOP {limit}
                run_id,
                pipeline_name,
                start_time,
                end_time,
                status,
                DATEDIFF(minute, start_time, ISNULL(end_time, GETDATE())) as duration_minutes
            FROM adf_pipeline_runs
            WHERE start_time >= DATEADD(day, -{days}, GETDATE())
            ORDER BY start_time DESC
            """
            
            cursor.execute(query)
            runs = cursor.fetchall()
            conn.close()
            
            logger.info(f"✅ Fetched {len(runs)} pipeline runs from last {days} days")
            return runs
        
        except pyodbc.Error as e:
            error_msg = f"Failed to fetch pipeline runs: {str(e)}"
            logger.error(error_msg)
            raise ADFQueryError(error_msg)
    
    def get_pipeline_run_by_id(self, run_id: str) -> Optional[Tuple]:
        """
        Get specific pipeline run by ID
        
        Args:
            run_id: Pipeline run ID
            
        Returns:
            Tuple: Pipeline run record or None if not found
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                run_id,
                pipeline_name,
                start_time,
                end_time,
                status,
                DATEDIFF(minute, start_time, ISNULL(end_time, GETDATE())) as duration_minutes
            FROM adf_pipeline_runs
            WHERE run_id = ?
            """
            
            cursor.execute(query, (run_id,))
            run = cursor.fetchone()
            conn.close()
            
            if run:
                logger.info(f"✅ Found pipeline run: {run_id}")
            else:
                logger.warning(f"⚠️  Pipeline run not found: {run_id}")
            
            return run
        
        except pyodbc.Error as e:
            logger.error(f"Failed to fetch pipeline run: {e}")
            raise ADFQueryError(str(e))
    
    def get_failed_pipeline_runs(
        self,
        days: int = 7,
        limit: int = 50
    ) -> List[Tuple]:
        """
        Get failed pipeline runs
        
        Args:
            days: Number of days to look back
            limit: Maximum results
            
        Returns:
            List[Tuple]: Failed pipeline runs
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = f"""
            SELECT TOP {limit}
                run_id,
                pipeline_name,
                start_time,
                end_time,
                status,
                error_message,
                DATEDIFF(minute, start_time, ISNULL(end_time, GETDATE())) as duration_minutes
            FROM adf_pipeline_runs
            WHERE status = 'FAILED'
            AND start_time >= DATEADD(day, -{days}, GETDATE())
            ORDER BY start_time DESC
            """
            
            cursor.execute(query)
            runs = cursor.fetchall()
            conn.close()
            
            logger.info(f"⚠️  Found {len(runs)} failed pipeline runs")
            return runs
        
        except pyodbc.Error as e:
            logger.error(f"Failed to fetch failed runs: {e}")
            raise ADFQueryError(str(e))
    
    def get_pipeline_statistics(self, days: int = 30) -> List[Dict]:
        """
        Get pipeline execution statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List[Dict]: Statistics per pipeline
            
        Example:
            [
                {
                    'pipeline_name': 'MasterERP',
                    'total_runs': 30,
                    'successful': 29,
                    'failed': 1,
                    'success_rate': 96.7,
                    'avg_duration_minutes': 45.5
                },
                ...
            ]
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = f"""
            SELECT 
                pipeline_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                CAST(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as DECIMAL(5,1)) as success_rate,
                AVG(CAST(DATEDIFF(minute, start_time, ISNULL(end_time, GETDATE())) as FLOAT)) as avg_duration_minutes
            FROM adf_pipeline_runs
            WHERE start_time >= DATEADD(day, -{days}, GETDATE())
            GROUP BY pipeline_name
            ORDER BY total_runs DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dictionaries
            stats = []
            for row in rows:
                stats.append({
                    'pipeline_name': row[0],
                    'total_runs': row[1],
                    'successful': row[2],
                    'failed': row[3],
                    'success_rate': float(row[4]) if row[4] else 0,
                    'avg_duration_minutes': float(row[5]) if row[5] else 0
                })
            
            logger.info(f"✅ Computed statistics for {len(stats)} pipelines")
            return stats
        
        except Exception as e:
            logger.error(f"Failed to compute statistics: {e}")
            raise ADFQueryError(str(e))
    
    def get_activity_runs(
        self,
        pipeline_name: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> List[Tuple]:
        """
        Get activity runs (tasks within pipelines)
        
        Args:
            pipeline_name: Filter by pipeline (optional)
            days: Days to look back
            limit: Max results
            
        Returns:
            List[Tuple]: Activity run records
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if pipeline_name:
                query = f"""
                SELECT TOP {limit}
                    activity_run_id,
                    pipeline_name,
                    activity_name,
                    activity_type,
                    start_time,
                    end_time,
                    status,
                    input,
                    output,
                    error_message
                FROM adf_activity_runs
                WHERE pipeline_name = ?
                AND start_time >= DATEADD(day, -{days}, GETDATE())
                ORDER BY start_time DESC
                """
                cursor.execute(query, (pipeline_name,))
            else:
                query = f"""
                SELECT TOP {limit}
                    activity_run_id,
                    pipeline_name,
                    activity_name,
                    activity_type,
                    start_time,
                    end_time,
                    status,
                    input,
                    output,
                    error_message
                FROM adf_activity_runs
                WHERE start_time >= DATEADD(day, -{days}, GETDATE())
                ORDER BY start_time DESC
                """
                cursor.execute(query)
            
            runs = cursor.fetchall()
            conn.close()
            
            logger.info(f"✅ Fetched {len(runs)} activity runs")
            return runs
        
        except pyodbc.Error as e:
            logger.error(f"Failed to fetch activity runs: {e}")
            raise ADFQueryError(str(e))
    
    def get_long_running_activities(
        self,
        min_duration_minutes: int = 60,
        days: int = 7,
        limit: int = 30
    ) -> List[Dict]:
        """
        Get activities that took longer than threshold
        
        Args:
            min_duration_minutes: Minimum duration in minutes
            days: Days to look back
            limit: Max results
            
        Returns:
            List[Dict]: Long-running activities
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = f"""
            SELECT TOP {limit}
                activity_name,
                pipeline_name,
                start_time,
                end_time,
                DATEDIFF(minute, start_time, end_time) as duration_minutes,
                status
            FROM adf_activity_runs
            WHERE status = 'SUCCESS'
            AND DATEDIFF(minute, start_time, end_time) > ?
            AND start_time >= DATEADD(day, -{days}, GETDATE())
            ORDER BY duration_minutes DESC
            """
            
            cursor.execute(query, (min_duration_minutes,))
            rows = cursor.fetchall()
            conn.close()
            
            activities = []
            for row in rows:
                activities.append({
                    'activity_name': row[0],
                    'pipeline_name': row[1],
                    'start_time': row[2],
                    'end_time': row[3],
                    'duration_minutes': row[4],
                    'status': row[5]
                })
            
            logger.info(f"✅ Found {len(activities)} long-running activities")
            return activities
        
        except Exception as e:
            logger.error(f"Failed to fetch long-running activities: {e}")
            raise ADFQueryError(str(e))
    
    def sync_adf_records(self):
        """
        Sync ADF data to local cache/database (optional)
        Useful if you want to cache ADF data for faster queries
        """
        try:
            logger.info("🔄 Starting ADF data sync...")
            
            # Get recent runs
            runs = self.get_recent_pipeline_runs(days=7, limit=200)
            logger.info(f"✅ Synced {len(runs)} pipeline records")
            
            # Get recent activities
            activities = self.get_activity_runs(days=7, limit=500)
            logger.info(f"✅ Synced {len(activities)} activity records")
            
            return {
                'status': 'success',
                'pipeline_runs': len(runs),
                'activities': len(activities),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ ADF sync failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Helper functions

def get_adf_service() -> ADFDataService:
    """Get ADF service instance"""
    return ADFDataService()


def test_adf_connection() -> bool:
    """Test ADF connection - useful for health checks"""
    service = ADFDataService()
    return service.test_connection()


def get_adf_pipeline_runs(days: int = 7) -> List[Tuple]:
    """Get recent ADF pipeline runs"""
    service = ADFDataService()
    return service.get_recent_pipeline_runs(days=days)


def get_adf_failed_runs(days: int = 7) -> List[Tuple]:
    """Get failed ADF pipeline runs"""
    service = ADFDataService()
    return service.get_failed_pipeline_runs(days=days)


def get_adf_statistics(days: int = 30) -> List[Dict]:
    """Get ADF pipeline statistics"""
    service = ADFDataService()
    return service.get_pipeline_statistics(days=days)
