"""
Databricks ODBC Service Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Uses the same SSRS Databricks DSN: DataBricks_For_DBX_APP_64B_PRD
Provides QueryExecution service matching SSRS data source configuration
"""

import pyodbc
import logging
from datetime import datetime, timedelta
from django.conf import settings
from typing import List, Dict, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class DatabricksConnectionError(Exception):
    """Raised when Databricks connection fails"""
    pass


class DatabricksQueryError(Exception):
    """Raised when Databricks query fails"""
    pass


class DatabricksODBCService:
    """
    Service for querying Databricks via ODBC DSN
    Uses same connection as SSRS ADF_DATASOURCE
    """
    
    def __init__(self, dsn: Optional[str] = None):
        """
        Initialize Databricks Service
        
        Args:
            dsn: DSN name (default: DataBricks_For_DBX_APP_64B_PRD from settings)
        """
        if dsn:
            self.dsn = dsn
        else:
            # Default: Use same DSN as SSRS
            self.dsn = getattr(
                settings, 
                'DATABRICKS_DSN', 
                'DataBricks_For_DBX_APP_64B_PRD'
            )
        
        self.connection_string = f'DSN={self.dsn};'
        self.timeout = 30
        
        logger.info(f"🔗 Databricks ODBC Service initialized with DSN: {self.dsn}")
    
    @property
    def is_configured(self) -> bool:
        """Check if Databricks DSN is configured"""
        return bool(self.dsn)
    
    def connect(self) -> pyodbc.Connection:
        """
        Create ODBC connection to Databricks
        
        Returns:
            pyodbc.Connection: Database connection
            
        Raises:
            DatabricksConnectionError: If connection fails
        """
        try:
            conn = pyodbc.connect(self.connection_string, timeout=self.timeout)
            logger.info(f"✅ Connected to Databricks DSN: {self.dsn}")
            return conn
        except pyodbc.Error as e:
            error_msg = f"Databricks Connection failed: {str(e)}"
            logger.error(error_msg)
            raise DatabricksConnectionError(error_msg)
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test Databricks connection
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            
            message = f"✅ Connected successfully to {self.dsn}"
            logger.info(message)
            return True, message
        
        except Exception as e:
            message = f"❌ Connection failed: {str(e)}"
            logger.error(message)
            return False, message
    
    def execute_query(
        self,
        sql: str,
        params: Optional[Tuple] = None
    ) -> List[Tuple]:
        """
        Execute SQL query against Databricks
        
        Args:
            sql: SQL query string
            params: Optional query parameters
            
        Returns:
            List[Tuple]: Query results
            
        Raises:
            DatabricksQueryError: If query fails
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            results = cursor.fetchall()
            conn.close()
            
            logger.info(f"✅ Query executed successfully, {len(results)} rows returned")
            return results
        
        except pyodbc.Error as e:
            error_msg = f"Databricks query failed: {str(e)}"
            logger.error(error_msg)
            raise DatabricksQueryError(error_msg)
    
    def execute_query_dict(
        self,
        sql: str,
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute query and return results as list of dictionaries
        
        Args:
            sql: SQL query
            params: Optional parameters
            
        Returns:
            List[Dict]: Results with column names as keys
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch and convert to dicts
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            
            logger.info(f"✅ Query executed, {len(results)} rows returned as dicts")
            return results
        
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            raise DatabricksQueryError(error_msg)
    
    def get_tables(self, database: str = 'default') -> List[str]:
        """
        Get list of tables in database
        
        Args:
            database: Database name (default: 'default')
            
        Returns:
            List[str]: Table names
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Databricks SQL command
            cursor.execute(f"SHOW TABLES IN {database}")
            
            tables = [row[1] for row in cursor.fetchall()]  # Get table name column
            conn.close()
            
            logger.info(f"✅ Found {len(tables)} tables in {database}")
            return tables
        
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """
        Get table schema (columns and types)
        
        Args:
            table_name: Table name
            
        Returns:
            List[Dict]: Column definitions
        """
        try:
            results = self.execute_query(f"DESCRIBE {table_name}")
            
            schema = []
            for row in results:
                schema.append({
                    'column': row[0],
                    'type': row[1],
                    'nullable': row[2] if len(row) > 2 else 'YES'
                })
            
            logger.info(f"✅ Retrieved schema for {table_name}")
            return schema
        
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_data_sample(
        self,
        table_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get sample data from table
        
        Args:
            table_name: Table name
            limit: Number of rows to return
            
        Returns:
            List[Dict]: Sample data
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = self.execute_query_dict(query)
            
            logger.info(f"✅ Retrieved {len(results)} sample rows from {table_name}")
            return results
        
        except Exception as e:
            logger.error(f"Failed to get sample data: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_column_distinct(
        self,
        table_name: str,
        column: str,
        limit: int = 100
    ) -> List[Any]:
        """
        Get distinct values from column
        
        Args:
            table_name: Table name
            column: Column name
            limit: Max results
            
        Returns:
            List: Distinct values
        """
        try:
            query = f"SELECT DISTINCT {column} FROM {table_name} LIMIT {limit}"
            results = self.execute_query(query)
            
            values = [row[0] for row in results]
            logger.info(f"✅ Retrieved {len(values)} distinct values from {table_name}.{column}")
            return values
        
        except Exception as e:
            logger.error(f"Failed to get distinct values: {e}")
            raise DatabricksQueryError(str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADF SPECIFIC SERVICE (For ADF Metadata queries)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ADF_DatabricksService(DatabricksODBCService):
    """Service for querying ADF data stored in Databricks"""
    
    def __init__(self):
        """Initialize ADF service using configured DSN"""
        super().__init__()
        # Use the table name from settings
        self.adf_table = getattr(settings, 'DATABRICKS_ADF_TABLE', 'asl.metadata_framework.ingestion_log')
    
    def get_adf_status_today(self) -> List[Dict[str, Any]]:
        """
        Get ADF job status for today (latest run per job)
        
        Returns:
            List[Dict]: ADF job status records
        """
        try:
            query = f"""
            WITH ranked_jobs AS (
                SELECT 
                    job_name,
                    resource_type AS Job_Type,
                    frequency AS Schedule_run_time,
                    from_utc_timestamp(start_time, 'Asia/Kolkata') AS Start_Time_IST,
                    from_utc_timestamp(end_time, 'Asia/Kolkata') AS End_Time_IST,
                    job_status AS Run_Status,
                    error_message AS Error_Message,
                    ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY start_time DESC) AS rn
                FROM 
                    {self.adf_table}
                WHERE 
                    CAST(start_time AS DATE) = CURRENT_DATE
                    AND resource_type = 'ADF'
            )
            SELECT 
                job_name,
                Job_Type,
                Schedule_run_time,
                Start_Time_IST,
                End_Time_IST,
                Run_Status,
                Error_Message
            FROM 
                ranked_jobs
            WHERE 
                rn = 1
            ORDER BY 
                Start_Time_IST
            """
            
            results = self.execute_query_dict(query)
            logger.info(f"✅ Retrieved {len(results)} ADF status records for today")
            return results
        
        except Exception as e:
            logger.error(f"Failed to get ADF status: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_failed_jobs_today(self) -> List[Dict[str, Any]]:
        """
        Get failed Databricks & ADF jobs for today (latest run per job)
        
        Returns:
            List[Dict]: Failed job records
        """
        try:
            query = f"""
            WITH RankedJobs AS (
                SELECT 
                    job_name, 
                    resource_type, 
                    start_time, 
                    end_time, 
                    job_status, 
                    error_message,
                    ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY start_time DESC) AS rn
                FROM {self.adf_table}
                WHERE DATE(start_time) = CURRENT_DATE()
                  AND job_status = 'Failed'
            )
            SELECT 
                job_name, 
                resource_type, 
                start_time, 
                end_time, 
                job_status, 
                error_message
            FROM RankedJobs
            WHERE rn = 1
            ORDER BY job_status DESC
            """
            
            results = self.execute_query_dict(query)
            logger.info(f"✅ Retrieved {len(results)} failed jobs for today")
            return results
        
        except Exception as e:
            logger.error(f"Failed to get failed jobs: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_recent_pipeline_runs(
        self,
        days: int = 7,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent ADF pipeline runs from Databricks
        
        Args:
            days: Days to look back
            limit: Max results
            
        Returns:
            List[Dict]: Pipeline run records
        """
        try:
            query = f"""
            SELECT 
                run_id,
                pipeline_name,
                start_time,
                end_time,
                status,
                CAST((unix_timestamp(end_time) - unix_timestamp(start_time)) / 60 as INT) as duration_minutes
            FROM {self.adf_database}.pipeline_runs
            WHERE start_time >= date_sub(current_date(), {days})
            ORDER BY start_time DESC
            LIMIT {limit}
            """
            
            results = self.execute_query_dict(query)
            logger.info(f"✅ Retrieved {len(results)} ADF pipeline runs")
            return results
        
        except Exception as e:
            logger.error(f"Failed to get ADF pipeline runs: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_failed_pipelines(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get failed ADF pipelines"""
        try:
            query = f"""
            SELECT 
                run_id,
                pipeline_name,
                start_time,
                end_time,
                status,
                error_message
            FROM {self.adf_database}.pipeline_runs
            WHERE status = 'FAILED'
            AND start_time >= date_sub(current_date(), {days})
            ORDER BY start_time DESC
            """
            
            return self.execute_query_dict(query)
        
        except Exception as e:
            logger.error(f"Failed to get failed pipelines: {e}")
            raise DatabricksQueryError(str(e))
    
    def get_pipeline_statistics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get pipeline execution statistics"""
        try:
            query = f"""
            SELECT 
                pipeline_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as success_rate
            FROM {self.adf_database}.pipeline_runs
            WHERE start_time >= date_sub(current_date(), {days})
            GROUP BY pipeline_name
            ORDER BY total_runs DESC
            """
            
            return self.execute_query_dict(query)
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise DatabricksQueryError(str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_databricks_service(dsn: Optional[str] = None) -> DatabricksODBCService:
    """Get Databricks service instance"""
    return DatabricksODBCService(dsn=dsn)


def get_adf_databricks_service() -> ADF_DatabricksService:
    """Get ADF Databricks service instance"""
    return ADF_DatabricksService()


def test_databricks_connection(dsn: Optional[str] = None) -> Tuple[bool, str]:
    """Test Databricks connection"""
    service = DatabricksODBCService(dsn=dsn)
    return service.test_connection()


def execute_databricks_query(sql: str, dsn: Optional[str] = None) -> List[Tuple]:
    """Execute query against Databricks"""
    service = DatabricksODBCService(dsn=dsn)
    return service.execute_query(sql)
