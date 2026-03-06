# Databricks ODBC Setup Guide

## Overview
This guide explains how to set up the Databricks ODBC connection for the ADF Application monitoring.

## Prerequisites
- **ODBC Driver**: Simba Spark ODBC Driver (for Databricks)
- **Python Package**: `pyodbc` (already installed)
- **DSN Name**: `DataBricks_For_DBX_APP_64B_PRD`

## Installation Steps

### 1. Install Simba Spark ODBC Driver
1. Download the **Simba Spark ODBC Driver for Windows (64-bit)** from:
   - Databricks official website, or
   - Your organization's software repository

2. Run the installer and follow the installation wizard

### 2. Configure ODBC Data Source (DSN)

#### Open ODBC Data Source Administrator
1. Press `Windows + R`
2. Type: `odbcad32.exe` (64-bit version)
3. Click OK

#### Add System DSN
1. Go to the **"System DSN"** tab
2. Click **"Add..."**
3. Select **"Simba Spark ODBC Driver"**
4. Click **"Finish"**

#### Configure Connection
Enter the following details:
- **Data Source Name**: `DataBricks_For_DBX_APP_64B_PRD`
- **Description**: Databricks Production Connection
- **Host(s)**: `<Your Databricks workspace URL>` (e.g., `dbc-12345678-9abc.cloud.databricks.com`)
- **Port**: `443` (default for HTTPS)
- **HTTP Path**: `<Your cluster/endpoint HTTP path>` (e.g., `/sql/1.0/warehouses/abc123def456`)
- **Authentication**: 
  - **Mechanism**: `User Name and Password` or `Personal Access Token`
  - **Token**: `<Your Databricks Personal Access Token>` (if using token auth)
- **SSL Options**: Enable SSL
- **Thrift Transport**: `HTTP`

#### Test Connection
1. Click **"Test"** button in DSN configuration
2. Should show: "Connection Successful"
3. Click **"OK"** to save

### 3. Get Databricks Connection Details

If you don't have the connection details, get them from Databricks:

1. Log into your Databricks workspace
2. Go to **SQL Warehouses** or **Clusters**
3. Select your warehouse/cluster
4. Click **"Connection Details"** tab
5. Copy:
   - Server hostname
   - Port
   - HTTP path

### 4. Verify Connection in Python

Run the test script:
```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal
python test_databricks_connection.py
```

Expected output:
```
✅ pyodbc module found
🔌 Attempting to connect to DSN: DataBricks_For_DBX_APP_64B_PRD
✅ Databricks connection SUCCESSFUL!
✅ Test query result: (1,)
```

### 5. Integration in Portal

Once DSN is configured, the portal will automatically use it through:
- **Module**: `portal/db/databricks_client.py`
- **Function**: `DatabricksClient.fetch_all(query)`

## Usage Example

```python
from portal.db.databricks_client import DatabricksClient

# Test connection
if DatabricksClient.test_connection():
    print("Connected!")

# Execute query
query = "SELECT * FROM adf_failed_jobs LIMIT 10"
results = DatabricksClient.fetch_all(query)
for row in results:
    print(row)
```

## Troubleshooting

### Error: Data source name not found
- **Cause**: DSN not configured in ODBC
- **Solution**: Follow steps 2.1-2.6 above

### Error: Connection timeout
- **Cause**: Network/firewall issues or wrong host/port
- **Solution**: Verify host, port, and network connectivity

### Error: Authentication failed
- **Cause**: Invalid token or credentials
- **Solution**: Generate new Personal Access Token in Databricks

### Error: SSL certificate verification failed
- **Cause**: SSL/TLS certificate issues
- **Solution**: Enable "Allow Host Name CN Mismatch" in DSN SSL Options

## Security Notes
- **Never commit** Databricks tokens to source control
- Use **System DSN** (not User DSN) for service accounts
- Tokens should be stored in **Windows Credential Manager** or **environment variables**
- Rotate tokens regularly per security policy

## Contact
For Databricks access issues, contact:
- Your Databricks Administrator
- IT/Data Platform team
