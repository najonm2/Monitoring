# Azure Data Factory (ADF) Job - DSN Connection Setup Guide

## 📋 Overview

This guide will help you set up DSN (Data Source Name) connections for monitoring **Azure Data Factory (ADF)** jobs in your Django dashboard.

**What you'll be able to do:**
- ✅ Query ADF job execution history
- ✅ Monitor pipeline runs and status
- ✅ Track job performance metrics
- ✅ Integrate ADF data into your ERP dashboard

---

## 🎯 Which DSN Do You Need?

### **Option 1: Direct SQL Server Connection (Recommended for ADF)**
If your ADF metadata is stored in Azure SQL Database or SQL Server:
- DSN Name: `ADF_Metadata_DSN`
- Driver: ODBC Driver 17 for SQL Server
- Server: Your Azure SQL server or on-prem SQL Server
- Database: ADF metadata store

### **Option 2: Azure Files/Blob Storage Connection**
If ADF outputs logs to Azure Storage:
- Requires different approach (REST API or Python SDK)
- More complex setup

### **Option 3: Analytics/Data Warehouse**
If ADF data is synced to:
- Azure Synapse (formerly SQL DW)
- Databricks
- Data Lake

---

## 🚀 Step 1: Identify Your ADF Data Source

Before creating the DSN, determine where ADF stores its execution data:

### **Check With Your ADF Admin:**
```
Q: Where is ADF metadata stored?
   - Azure SQL Database?
   - SQL Server on-premises?
   - Azure Synapse?
   - Databricks?
   - Azure Data Lake Storage?

Q: What are the connection details?
   - Server hostname/IP
   - Port (default: 1433 for SQL Server)
   - Database name
   - Username/password or managed identity
```

---

## 📝 Step 2: Gather Required Information

Create a note with these details:

```
ADF Connection Details:
┌─────────────────────────────────────────┐
│ Server Type: [SQL Server / Synapse / Databricks]
│ Server: ___________________
│ Port: ___________________
│ Database: ___________________
│ Username: ___________________
│ Password: ___________________
│ Integrated Auth (Windows): [Yes/No]
│ Encryption: [Required/Optional/Disabled]
│ Firewall Rules: [Configured/Need to add IP]
└─────────────────────────────────────────┘
```

---

## 🔧 Step 3: Create ADF DSN in Windows

### **For SQL Server / Azure SQL Database:**

#### **Method 1: Using ODBC Administrator (GUI)**

1. **Open ODBC Administrator:**
   ```powershell
   Start-Process odbcad32.exe
   ```

2. **Select "System DSN" tab**
   - System DSN: Available to all users
   - User DSN: Only current user

3. **Click "Add..." button**
   - Select "ODBC Driver 17 for SQL Server"
   - Click "Finish"

4. **Fill in the Configuration:**
   ```
   Name:              ADF_Metadata_DSN
   Description:       Azure Data Factory Metadata Connection
   Server:            [your-server].database.windows.net  (for Azure SQL)
                      OR
                      [your-ip-or-hostname]  (for on-prem SQL Server)
   ```

5. **Set Authentication:**
   ```
   ○ SQL Server Authentication
     Login ID:     [username]
     Password:     [password]
   
   OR
   
   ○ Windows Authentication
     (Uses your Windows credentials)
   ```

6. **Database Selection:**
   - Default database: [your-adf-metadata-database]

7. **Encryption Options:**
   ```
   ○ Encrypt connection (Recommended)
   ○ Trust server certificate
   ```

8. **Click "Test Data Source"**
   - Should show: ✅ "Tests completed successfully!"

9. **Click "OK"**

---

#### **Method 2: Using PowerShell Script**

Save this as `create_adf_dsn.ps1`:

```powershell
# Create ADF DSN via PowerShell

$DsnName = "ADF_Metadata_DSN"
$DriverName = "ODBC Driver 17 for SQL Server"
$ServerName = "your-adf-server.database.windows.net"  # Change this
$UserName = "adf_user"  # Change this
$Password = "your_password"  # Change this
$Database = "adf_metadata_db"  # Change this
$Port = "1433"

# Create registry entry for System DSN
$RegPath = "HKLM:\Software\ODBC\ODBC.INI\$DsnName"

# Check if driver exists
$driver = Get-OdbcDriver | Where-Object {$_.Name -eq $DriverName}
if (-not $driver) {
    Write-Error "ODBC Driver 17 for SQL Server not found. Install it first."
    exit
}

# Create System DSN
New-OdbcDsn -Name $DsnName `
    -DriverName $DriverName `
    -SetPropertyValue @(
        "Server=$ServerName",
        "Database=$Database",
        "UID=$UserName",
        "PWD=$Password",
        "Encrypt=yes",
        "TrustServerCertificate=no"
    ) `
    -DsnType "System" `
    -Force

Write-Host "✅ ADF DSN created: $DsnName" -ForegroundColor Green
```

**Run it:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\create_adf_dsn.ps1
```

---

### **For Databricks:**

If your ADF metadata is in Databricks, use the Simba Spark ODBC Driver:

1. **Open ODBC Administrator**
2. **Create System DSN:**
   ```
   Name:           ADF_Databricks_DSN
   Driver:         Simba Spark ODBC Driver
   Host:           dbc-XXXXXXXX.cloud.databricks.com
   Port:           443
   HTTP Path:      /sql/1.0/warehouses/xxxxx
   Auth Type:      User/Password
   Username:       token
   Password:       [Databricks PAT Token]
   ```

3. **Test connection**

---

## ✅ Step 4: Verify DSN Creation

### **Check via PowerShell:**
```powershell
# List all System DSNs
Get-OdbcDsn -DsnType "System"

# Check specific DSN
$dsn = Get-OdbcDsn -Name "ADF_Metadata_DSN" -DsnType "System"
$dsn | Select-Object Name, DriverName, Platform

# Test connection
$conn = New-Object System.Data.Odbc.OdbcConnection
$conn.ConnectionString = "DSN=ADF_Metadata_DSN;"
Try {
    $conn.Open()
    Write-Host "✅ Connection successful!" -ForegroundColor Green
    $conn.Close()
}
Catch {
    Write-Host "❌ Connection failed: $_" -ForegroundColor Red
}
```

### **Check via GUI:**
```powershell
odbcad32.exe
# Browse to "System DSN" tab
# Look for "ADF_Metadata_DSN"
```

---

## 🐍 Step 5: Use DSN in Python/Django Code

### **Connection Method 1: Using pyodbc**

```python
import pyodbc

# Connect using DSN
conn = pyodbc.connect('DSN=ADF_Metadata_DSN;')
cursor = conn.cursor()

# Example query
query = """
SELECT 
    run_id,
    pipeline_name,
    start_time,
    end_time,
    status,
    duration_minutes
FROM adf_pipeline_runs
WHERE start_time >= DATEADD(day, -7, GETDATE())
ORDER BY start_time DESC
"""

cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    print(f"Pipeline: {row[1]}, Status: {row[4]}")

conn.close()
```

### **Connection Method 2: Using Connection String**

```python
import pyodbc

# Direct connection without DSN
conn_str = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=your-server.database.windows.net;'
    'Database=adf_metadata;'
    'UID=username;'
    'PWD=password;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
# ... rest of code
```

### **Connection Method 3: In Django Settings**

```python
# settings.py

# ADF Database Configuration
ADF_DATABASE = {
    'engine': 'pyodbc',
    'driver': 'ODBC Driver 17 for SQL Server',
    'dsn': 'ADF_Metadata_DSN',  # Use DSN
    'host': None,  # DSN handles this
}

# Or without DSN:
ADF_DATABASE = {
    'engine': 'pyodbc',
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'your-server.database.windows.net',
    'database': 'adf_metadata',
    'user': 'username',
    'password': 'password',
    'host': None,
}
```

---

## 🏗️ Step 6: Create Django Model for ADF Jobs

```python
# models.py
from django.db import models

class ADFPipelineRun(models.Model):
    run_id = models.CharField(max_length=100, unique=True)
    pipeline_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('RUNNING', 'Running'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
            ('CANCELLED', 'Cancelled'),
        ]
    )
    duration_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.pipeline_name} - {self.status}"
```

---

## 🔗 Step 7: Create Service to Fetch ADF Data

```python
# services/adf_service.py
import pyodbc
from datetime import datetime, timedelta
from django.conf import settings

class ADFDataService:
    def __init__(self):
        self.dsn = settings.ADF_DATABASE.get('dsn', 'ADF_Metadata_DSN')
    
    def connect(self):
        """Create ODBC connection"""
        try:
            conn = pyodbc.connect(f'DSN={self.dsn};')
            return conn
        except pyodbc.Error as e:
            raise Exception(f"ADF Connection failed: {e}")
    
    def get_recent_pipeline_runs(self, days=7):
        """Fetch recent ADF pipeline runs"""
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
        WHERE start_time >= DATEADD(day, -?, GETDATE())
        ORDER BY start_time DESC
        """
        
        cursor.execute(query, days)
        runs = cursor.fetchall()
        conn.close()
        
        return runs
    
    def get_failed_runs(self, days=7):
        """Get failed pipeline runs"""
        conn = self.connect()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            run_id,
            pipeline_name,
            start_time,
            end_time,
            status,
            error_message
        FROM adf_pipeline_runs
        WHERE status = 'FAILED'
        AND start_time >= DATEADD(day, -?, GETDATE())
        ORDER BY start_time DESC
        """
        
        cursor.execute(query, days)
        runs = cursor.fetchall()
        conn.close()
        
        return runs
```

---

## 🧪 Step 8: Test the Connection

### **Test Script:**

```python
# test_adf_connection.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.adf_service import ADFDataService

print("Testing ADF DSN Connection...")
print("=" * 50)

try:
    service = ADFDataService()
    
    # Test basic connection
    print("\n1️⃣ Testing basic connection...")
    conn = service.connect()
    conn.close()
    print("   ✅ Connection successful!")
    
    # Fetch recent runs
    print("\n2️⃣ Fetching recent pipeline runs...")
    runs = service.get_recent_pipeline_runs(days=7)
    print(f"   ✅ Found {len(runs)} runs in last 7 days")
    
    # Show sample
    if runs:
        print("\n   Sample Runs:")
        for run in runs[:3]:
            print(f"   - {run[1]}: {run[4]} (started: {run[2]})")
    
    # Get failed runs
    print("\n3️⃣ Checking failed runs...")
    failed = service.get_failed_runs(days=7)
    print(f"   ⚠️  Found {len(failed)} failed runs")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
```

**Run test:**
```bash
python test_adf_connection.py
```

---

## 🚨 Troubleshooting

### **Error: "DSN not found"**
```powershell
# Verify DSN exists
Get-OdbcDsn -DsnType "System" | Where-Object {$_.Name -like "*ADF*"}

# If not found, recreate it using ODBC Administrator
Start-Process odbcad32.exe
```

### **Error: "Login failed for user"**
- ✅ Check username/password in DSN
- ✅ Check password hasn't changed
- ✅ Check user has database access
- ✅ Check IP firewall rules (Azure SQL)

### **Error: "Connection timeout"**
- ✅ Verify server is accessible: `Test-NetConnection -ComputerName your-server.database.windows.net -Port 1433`
- ✅ Check firewall rules allow port 1433
- ✅ Check VPN is connected (if required)

### **Error: "Driver not found"**
```powershell
# Install ODBC Driver 17
# Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Or check what drivers are available
Get-OdbcDriver | Select-Object Name
```

---

## 📊 Sample ADF Queries

### **Get Pipeline Run Status:**
```sql
SELECT 
    pipeline_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
    AVG(CAST(duration_minutes as FLOAT)) as avg_duration_min
FROM adf_pipeline_runs
WHERE start_time >= DATEADD(day, -30, GETDATE())
GROUP BY pipeline_name
ORDER BY total_runs DESC
```

### **Get Recent Failed Activities:**
```sql
SELECT 
    TOP 20
    activity_name,
    pipeline_name,
    start_time,
    error_message,
    activity_type
FROM adf_activity_runs
WHERE status = 'FAILED'
AND start_time >= DATEADD(day, -7, GETDATE())
ORDER BY start_time DESC
```

### **Get Long-Running Activities:**
```sql
SELECT 
    TOP 30
    activity_name,
    pipeline_name,
    DATEDIFF(minute, start_time, end_time) as duration_minutes,
    start_time
FROM adf_activity_runs
WHERE status = 'SUCCESS'
AND DATEDIFF(minute, start_time, end_time) > 60
ORDER BY duration_minutes DESC
```

---

## ✨ Next Steps

1. ✅ Install ODBC Driver 17 for SQL Server (if not already installed)
2. ✅ Gather ADF connection details from your admin
3. ✅ Create ADF DSN using ODBC Administrator
4. ✅ Test DSN connection
5. ✅ Create Django models for ADF data
6. ✅ Build service layer for ADF queries
7. ✅ Add ADF jobs section to dashboard
8. ✅ Set up periodic sync of ADF data

---

## 📞 Common Configuration Examples

### **Azure SQL Database (Cloud):**
```
Server: servername.database.windows.net
Port: 1433
Username: admin@servername
Password: [your_secure_password]
Database: adf_metadata
Encryption: Yes (Required)
Trust Cert: No
```

### **SQL Server On-Premises:**
```
Server: 192.168.1.100  OR  myserver.domain.local
Port: 1433
Username: domain\username  OR  sa
Password: [password]
Database: adf_metadata
Encryption: Optional
Authentication: Windows / SQL Auth
```

### **Databricks:**
```
Host: dbc-xxxx.cloud.databricks.com
Port: 443
HTTP Path: /sql/1.0/warehouses/xxxxx
Username: token
Password: [Personal Access Token]
Encryption: Yes
```

---

**Need more help?** Check with your ADF/Database administration team for:
- ✅ Server hostname
- ✅ Database name
- ✅ User credentials
- ✅ Firewall rules for your IP
- ✅ SSL/TLS requirements

Good luck! 🎯
