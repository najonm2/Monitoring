"""
Databricks ODBC Client
DSN: DataBricks_For_DBX_APP_64B_PRD
"""

import pyodbc
from typing import List, Dict, Any


class DatabricksClient:
    """Client for connecting to Databricks via ODBC"""
    
    DSN = "DataBricks_For_DBX_APP_64B_PRD"
    
    @staticmethod
    def get_connection():
        """
        Get a connection to Databricks using ODBC DSN
        Returns: pyodbc.Connection object
        Raises: pyodbc.Error if connection fails
        """
        try:
            connection = pyodbc.connect(
                f"DSN={DatabricksClient.DSN}",
                timeout=30
            )
            return connection
        except pyodbc.Error as e:
            raise Exception(f"Failed to connect to Databricks: {e}")
    
    @staticmethod
    def fetch_all(query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query and fetch all results as list of dictionaries
        
        Args:
            query: SQL query string
            params: Optional tuple of query parameters
            
        Returns:
            List of dictionaries with column names as keys
        """
        connection = None
        cursor = None
        try:
            connection = DatabricksClient.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows and convert to list of dicts
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            
            return rows
            
        except Exception as e:
            raise Exception(f"Error executing Databricks query: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def test_connection() -> bool:
        """
        Test if connection to Databricks is working
        Returns: True if successful, False otherwise
        """
        try:
            connection = DatabricksClient.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result[0] == 1
        except Exception as e:
            print(f"Databricks connection test failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("Testing Databricks connection...")
    if DatabricksClient.test_connection():
        print("✅ Databricks connection successful!")
    else:
        print("❌ Databricks connection failed!")
        print("\n⚠️  ODBC DSN Setup Required:")
        print("   1. Open 'ODBC Data Sources (64-bit)' in Windows")
        print("   2. Go to 'System DSN' tab")
        print("   3. Add new data source: 'Simba Spark ODBC Driver'")
        print(f"   4. Name it: {DatabricksClient.DSN}")
        print("   5. Configure with Databricks connection details")
