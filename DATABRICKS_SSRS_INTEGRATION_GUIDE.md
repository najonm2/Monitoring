# Configure Django to Use SSRS Databricks DSN
# ═════════════════════════════════════════════════════════════════

## 🎯 Your SSRS Configuration

```
Data Source Name: ADF_DATASOURCE
Type: ODBC
Connection String: dsn=DataBricks_For_DBX_APP_64B_PRD
Credentials: Without any credentials
Description: DBX Connection
Status: Connected successfully ✅
```

---

## 🚀 Configure in Django (3 Simple Steps)

### Step 1: Add to settings.py

```python
# settings.py

# Databricks ODBC DSN (same as SSRS)
DATABRICKS_DSN = 'DataBricks_For_DBX_APP_64B_PRD'

# Optional: ADF Database name (if storing ADF metadata in Databricks)
ADF_DATABRICKS_DATABASE = 'adf_monitoring'  # Change as needed
```

### Step 2: Test Connection in Django Shell

```bash
python manage.py shell
```

```python
from portal.services.databricks_odbc_service import get_databricks_service

# Test connection
service = get_databricks_service()
success, message = service.test_connection()
print(message)
# Output: ✅ Connected successfully to DataBricks_For_DBX_APP_64B_PRD
```

### Step 3: Use in Your Views

```python
# views.py
from portal.services.databricks_odbc_service import get_adf_databricks_service

def dashboard_view(request):
    # Get service
    service = get_adf_databricks_service()
    
    # Query ADF data
    recent_runs = service.get_recent_pipeline_runs(days=7)
    statistics = service.get_pipeline_statistics(days=30)
    
    context = {
        'pipeline_runs': recent_runs,
        'statistics': statistics,
    }
    
    return render(request, 'dashboard.html', context)
```

---

## 📊 Common Queries to Run

### Get Recent Pipeline Runs

```python
from portal.services.databricks_odbc_service import get_databricks_service

service = get_databricks_service()

# Get recent ADF runs
query = """
SELECT 
    run_id,
    pipeline_name,
    start_time,
    end_time,
    status
FROM pipeline_runs
WHERE start_time >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY start_time DESC
LIMIT 100
"""

results = service.execute_query_dict(query)
for run in results:
    print(f"{run['pipeline_name']}: {run['status']}")
```

### Get Failed Pipelines

```python
service = get_databricks_service()

query = """
SELECT 
    pipeline_name,
    COUNT(*) as failure_count,
    MAX(start_time) as last_failure
FROM pipeline_runs
WHERE status = 'FAILED'
AND start_time >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY pipeline_name
ORDER BY failure_count DESC
"""

failures = service.execute_query_dict(query)
```

### Get Pipeline Performance

```python
service = get_databricks_service()

query = """
SELECT 
    pipeline_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
    AVG(CAST(duration_minutes as FLOAT)) as avg_duration_minutes
FROM pipeline_runs
WHERE start_time >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY pipeline_name
ORDER BY total_runs DESC
"""

stats = service.execute_query_dict(query)
```

---

## 🧪 Test Script

Create `test_databricks_ssrs_connection.py`:

```python
"""
Test Databricks ODBC connection (SSRS configuration)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.databricks_odbc_service import (
    get_databricks_service,
    get_adf_databricks_service
)

print("╔════════════════════════════════════════════════════╗")
print("║ Databricks ODBC Connection Test (SSRS Config)      ║")
print("╚════════════════════════════════════════════════════╝")
print()

# Test 1: Basic connection
print("Test 1: Basic Connection")
print("─" * 50)
service = get_databricks_service()
success, message = service.test_connection()
print(message)
print()

# Test 2: List tables
print("Test 2: List Available Tables")
print("─" * 50)
try:
    tables = service.get_tables()
    print(f"✅ Found {len(tables)} tables:")
    for table in tables[:10]:  # Show first 10
        print(f"   • {table}")
    if len(tables) > 10:
        print(f"   ... and {len(tables) - 10} more")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 3: Get sample data
print("Test 3: Sample Data")
print("─" * 50)
try:
    adf_service = get_adf_databricks_service()
    runs = adf_service.get_recent_pipeline_runs(days=7, limit=5)
    print(f"✅ Found {len(runs)} recent pipeline runs:")
    for run in runs:
        print(f"   • {run.get('pipeline_name')}: {run.get('status')}")
except Exception as e:
    print(f"⚠️  Error (table might not exist yet): {e}")
print()

# Test 4: Connection info
print("Test 4: Configuration Info")
print("─" * 50)
print(f"DSN: {service.dsn}")
print(f"Connection String: {service.connection_string}")
print(f"Timeout: {service.timeout}s")
print()

print("╔════════════════════════════════════════════════════╗")
print("║ ✅ All tests completed!                           ║")
print("╚════════════════════════════════════════════════════╝")
```

**Run test:**
```bash
python test_databricks_ssrs_connection.py
```

---

## 🔗 Relationship to SSRS

| Aspect | SSRS | Django |
|--------|------|--------|
| **Data Source Name** | ADF_DATASOURCE | (configured in view) |
| **Connection Type** | ODBC | pyodbc |
| **DSN** | DataBricks_For_DBX_APP_64B_PRD | DATABRICKS_DSN setting |
| **Credentials** | None (DSN handles) | None (DSN handles) |
| **Query Type** | SQL | SQL via pyodbc |
| **Result Format** | Native/XML | Tuples/Dicts |

---

## 📊 Example: Create ADF Dashboard Widget

```python
# views.py
from django.shortcuts import render
from portal.services.databricks_odbc_service import get_adf_databricks_service

def adf_dashboard(request):
    """ADF Dashboard using SSRS Databricks DSN"""
    
    try:
        service = get_adf_databricks_service()
        
        # Get data using same DSN as SSRS
        recent_runs = service.get_recent_pipeline_runs(days=7, limit=50)
        failed_runs = service.get_failed_pipelines(days=7)
        statistics = service.get_pipeline_statistics(days=30)
        
        context = {
            'recent_runs': recent_runs,
            'failed_runs': failed_runs,
            'statistics': statistics,
            'dsn': service.dsn,
            'data_source': 'ADF_DATASOURCE (Databricks via ODBC)',
        }
        
        return render(request, 'adf_dashboard.html', context)
    
    except Exception as e:
        context = {
            'error': f'Failed to load ADF data: {str(e)}',
            'dsn': getattr(settings, 'DATABRICKS_DSN', 'Not configured'),
        }
        
        return render(request, 'adf_dashboard_error.html', context)
```

**Template (adf_dashboard.html):**
```html
<div class="dashboard">
    <h1>ADF Pipeline Monitor</h1>
    <p class="subtitle">Data Source: {{ data_source }} | DSN: {{ dsn }}</p>
    
    <div class="stats-grid">
        {% for stat in statistics %}
        <div class="stat-card">
            <h3>{{ stat.pipeline_name }}</h3>
            <p class="success">✅ {{ stat.successful }} successful</p>
            <p class="failed">❌ {{ stat.failed }} failed</p>
            <p class="rate">Success Rate: {{ stat.success_rate }}%</p>
        </div>
        {% endfor %}
    </div>
    
    <table class="runs-table">
        <thead>
            <tr>
                <th>Pipeline</th>
                <th>Status</th>
                <th>Start Time</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
            {% for run in recent_runs %}
            <tr>
                <td>{{ run.pipeline_name }}</td>
                <td>
                    {% if run.status == 'SUCCESS' %}
                        <span class="badge success">✅ {{ run.status }}</span>
                    {% elif run.status == 'FAILED' %}
                        <span class="badge failed">❌ {{ run.status }}</span>
                    {% else %}
                        <span class="badge">{{ run.status }}</span>
                    {% endif %}
                </td>
                <td>{{ run.start_time }}</td>
                <td>{{ run.duration_minutes }}m</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

---

## ✅ Checklist

- [ ] DSN `DataBricks_For_DBX_APP_64B_PRD` is configured in Windows ODBC
- [ ] Added `DATABRICKS_DSN` to `settings.py`
- [ ] Added `databricks_odbc_service.py` to `portal/services/`
- [ ] Ran `python manage.py shell` and tested `service.test_connection()`
- [ ] Ran `test_databricks_ssrs_connection.py` successfully
- [ ] Can query Databricks data from Django views
- [ ] Integrated ADF dashboard into main portal

---

## 🚨 Troubleshooting

| Error | Solution |
|-------|----------|
| `DSN not found` | Verify DSN exists: Run `odbcad32.exe` and check System DSN tab |
| `Connection timeout` | Check Databricks is accessible, verify network/firewall |
| `Table not found` | Verify table exists in Databricks, use correct database name |
| `Authentication failed` | DSN credentials issue, reconfigure in ODBC admin |

---

## 📞 Summary

You're now using the **same Databricks DSN connection in Django** as your SSRS configuration:

✅ Same DSN: `DataBricks_For_DBX_APP_64B_PRD`  
✅ Same credentials: None (DSN handles it)  
✅ Same connection type: ODBC  
✅ Can query same data as SSRS reports  

The Django service layer provides Python-friendly access to all Databricks data that your SSRS reports use.
