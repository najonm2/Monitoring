"""
Test Databricks ODBC Connection
DSN: DataBricks_For_DBX_APP_64B_PRD
"""

try:
    import pyodbc
    print("✅ pyodbc module found")
    
    # Try to connect using the DSN
    dsn = "DataBricks_For_DBX_APP_64B_PRD"
    print(f"\n🔌 Attempting to connect to DSN: {dsn}")
    
    try:
        connection = pyodbc.connect(f"DSN={dsn}", timeout=10)
        print("✅ Databricks connection SUCCESSFUL!")
        
        # Test a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✅ Test query result: {result}")
        
        # Get connection info
        print(f"\n📊 Connection Info:")
        print(f"   Database: {connection.getinfo(pyodbc.SQL_DATABASE_NAME)}")
        print(f"   Server: {connection.getinfo(pyodbc.SQL_SERVER_NAME)}")
        print(f"   Driver: {connection.getinfo(pyodbc.SQL_DRIVER_NAME)}")
        
        cursor.close()
        connection.close()
        print("\n✅ Connection closed successfully")
        
    except pyodbc.Error as e:
        print(f"❌ Connection failed: {e}")
        print("\nAvailable DSNs:")
        try:
            dsns = pyodbc.dataSources()
            for dsn_name in sorted(dsns.keys()):
                print(f"   - {dsn_name}: {dsns[dsn_name]}")
        except:
            print("   Unable to list DSNs")
            
except ImportError:
    print("❌ pyodbc module not found")
    print("   Install with: pip install pyodbc")
