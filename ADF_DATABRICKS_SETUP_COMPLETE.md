# ADF Databricks Integration Setup - Complete ✅

## What Was Configured

### 1. Settings Configuration
**File:** `monitorportal/monitorportal/settings.py`

Added Databricks DSN configuration:
```python
# Databricks ODBC Configuration
DATABRICKS_DSN = 'Databricks_Conn'  # Your User DSN name
DATABRICKS_ADF_TABLE = 'asl.metadata_framework.ingestion_log'  # Your ADF metadata table
```

### 2. Service Layer Enhancement
**File:** `monitorportal/portal/services/databricks_odbc_service.py`

Updated `ADF_DatabricksService` class with two custom methods:

#### `get_adf_status_today()`
- Executes your **ADF Status Query**
- Fetches latest run per job for today
- Returns job details with IST timestamps
- Filters by `resource_type = 'ADF'`

#### `get_failed_jobs_today()`
- Executes your **Failed Jobs Query**
- Fetches failed Databricks & ADF jobs for today
- Returns latest run per job
- Filters by `job_status = 'Failed'`

### 3. View Functions
**File:** `monitorportal/portal/views.py`

Added two new view functions:

#### `adf_status(request)`
- Displays ADF job status dashboard
- Shows statistics: Total, Succeeded, Failed, Running, Success Rate
- Data cached for 2 minutes
- Handles connection errors gracefully

#### `databricks_adf_failed(request)`
- Displays failed jobs dashboard
- Shows statistics by resource type (ADF, Databricks, Other)
- Data cached for 2 minutes
- Highlights failed jobs in red

### 4. View Type Routing
**File:** `monitorportal/portal/views.py` - Updated `report_view()`

Added routing for:
- `view_type="adf_status"` → calls `adf_status()`
- `view_type="databricks_adf_failed"` → calls `databricks_adf_failed()`

### 5. HTML Templates

#### `adf_status.html`
- Modern dashboard with statistics cards
- Color-coded job status (Green=Success, Red=Failed, Orange=Running)
- Responsive table with all job details
- Shows: Job Name, Type, Schedule, Status, Start/End Time (IST), Error Message
- Empty state when no jobs

#### `databricks_adf_failed.html`
- Focused on failed jobs only
- Statistics by resource type
- Red-themed design for critical alerts
- Shows: Job Name, Resource Type, Timestamps, Status, Error Message
- Celebration message when no failures

---

## How to Test

### Step 1: Verify DSN Configuration

Open **ODBC Data Sources (64-bit)** on Windows:
1. Press `Win + R`, type `odbcad32.exe`, press Enter
2. Go to **User DSN** tab
3. Verify `Databricks_Conn` exists
4. Click **Test** to verify connection

### Step 2: Test Connection from Django

Run the test script:
```powershell
cd c:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
python test_adf_databricks_connection.py
```

Expected output:
```
✅ Connected successfully to Databricks_Conn
✅ Found X ADF jobs for today
✅ Found Y failed jobs for today
```

### Step 3: Access ADF Dashboards

1. Start Django development server:
   ```powershell
   python manage.py runserver
   ```

2. Open browser and navigate to:
   ```
   http://127.0.0.1:8000/dashboards/adf/
   ```

3. Click **VIEW** on each report:
   - **ADF Status** → Shows all ADF jobs for today
   - **Databricks & ADF Failed Jobs** → Shows only failed jobs

---

## Query Details

### Query 1: ADF Status (Today)
```sql
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
    FROM asl.metadata_framework.ingestion_log
    WHERE CAST(start_time AS DATE) = CURRENT_DATE
      AND resource_type = 'ADF'
)
SELECT * FROM ranked_jobs WHERE rn = 1
ORDER BY Start_Time_IST
```

### Query 2: Failed Jobs (Today)
```sql
WITH RankedJobs AS (
    SELECT 
        job_name, 
        resource_type, 
        start_time, 
        end_time, 
        job_status, 
        error_message,
        ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY start_time DESC) AS rn
    FROM asl.metadata_framework.ingestion_log
    WHERE DATE(start_time) = CURRENT_DATE()
      AND job_status = 'Failed'
)
SELECT * FROM RankedJobs WHERE rn = 1
ORDER BY job_status DESC
```

---

## Features

### ✅ Real-time Data
- Data fetched directly from Databricks
- Latest run per job (no duplicates)
- IST timezone conversion for timestamps

### ✅ Performance Optimization
- 2-minute caching to reduce database load
- Fast queries with ROW_NUMBER() window function
- Filters applied at database level

### ✅ Error Handling
- Graceful degradation if Databricks connection fails
- Clear error messages for troubleshooting
- Connection status displayed on dashboard

### ✅ Visual Design
- Color-coded statistics cards
- Row highlighting based on status
- Responsive table design
- Modern gradient backgrounds

---

## Troubleshooting

### Issue: Connection Failed

**Error:** `Databricks Connection failed: [ODBC Driver Manager]`

**Solution:**
1. Verify DSN exists in ODBC Data Sources (64-bit)
2. Test connection in ODBC Manager
3. Check Databricks credentials
4. Ensure Simba Spark ODBC Driver is installed

### Issue: No Data Returned

**Error:** Query executes but returns empty results

**Solution:**
1. Verify table name: `asl.metadata_framework.ingestion_log`
2. Check if jobs have run today
3. Verify permissions to access the table
4. Run query directly in Databricks SQL to test

### Issue: Table Does Not Exist

**Error:** `Table or view not found: asl.metadata_framework.ingestion_log`

**Solution:**
1. Check the correct database and table name
2. Update `DATABRICKS_ADF_TABLE` in `settings.py`
3. Verify schema: `<database>.<schema>.<table>`

---

## Next Steps

1. **Customize Queries**: Modify queries in `databricks_odbc_service.py` to add more fields or filters
2. **Add Historical Data**: Create views for last 7 days or 30 days
3. **Add Alerts**: Integrate email notifications for failed jobs
4. **Add Charts**: Use Chart.js to visualize trends
5. **Add Filtering**: Add date range picker for historical analysis

---

## Files Modified

| File | Changes |
|------|---------|
| `settings.py` | Added DATABRICKS_DSN and DATABRICKS_ADF_TABLE |
| `databricks_odbc_service.py` | Added get_adf_status_today() and get_failed_jobs_today() |
| `views.py` | Added adf_status() and databricks_adf_failed() functions |
| `adf_status.html` | Created new template |
| `databricks_adf_failed.html` | Created new template |
| `test_adf_databricks_connection.py` | Created test script |

---

## Summary

✅ **Databricks DSN configured**: `Databricks_Conn`  
✅ **ADF queries integrated**: Both queries from your specification  
✅ **Dashboards created**: 2 new ADF monitoring pages  
✅ **Error handling**: Graceful degradation if connection fails  
✅ **Performance**: 2-minute caching for fast response  
✅ **Visual design**: Modern, color-coded, responsive UI  

**Ready to use!** Navigate to http://127.0.0.1:8000/dashboards/adf/ and click VIEW on any report.
