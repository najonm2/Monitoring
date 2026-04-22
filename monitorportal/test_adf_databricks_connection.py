"""
Test Databricks Connection and ADF Queries
Test the Databricks_Conn DSN and verify ADF data queries
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.databricks_odbc_service import get_adf_databricks_service
from django.conf import settings

print("=" * 70)
print("DATABRICKS ADF CONNECTION TEST")
print("=" * 70)
print()

# Test 1: Check DSN Configuration
print("Test 1: DSN Configuration")
print("-" * 70)
dsn = getattr(settings, 'DATABRICKS_DSN', 'Not configured')
adf_table = getattr(settings, 'DATABRICKS_ADF_TABLE', 'Not configured')
print(f"   DSN Name: {dsn}")
print(f"   ADF Table: {adf_table}")
print()

# Test 2: Test Basic Connection
print("Test 2: Test Basic Connection")
print("-" * 70)
try:
    service = get_adf_databricks_service()
    success, message = service.test_connection()
    
    if success:
        print(f"   ✅ {message}")
    else:
        print(f"   ❌ {message}")
        print()
        print("   Troubleshooting:")
        print("   1. Open ODBC Data Sources (64-bit)")
        print("   2. Check if 'Databricks_Conn' exists in User DSN tab")
        print("   3. Test the connection in ODBC Manager")
        print("   4. Ensure Databricks credentials are correct")
        exit(1)
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    exit(1)

print()

# Test 3: Test ADF Status Query
print("Test 3: Test ADF Status Query (Today)")
print("-" * 70)
try:
    adf_jobs = service.get_adf_status_today()
    
    if adf_jobs:
        print(f"   ✅ Found {len(adf_jobs)} ADF jobs for today")
        print()
        print("   Sample Jobs:")
        for job in adf_jobs[:5]:
            status = job.get('Run_Status', 'Unknown')
            job_name = job.get('job_name', 'Unknown')
            print(f"      • {job_name}: {status}")
    else:
        print("   ⚠️  No ADF jobs found for today")
        print("   This may be normal if no jobs have run today yet")
except Exception as e:
    print(f"   ❌ Query failed: {e}")
    print()
    print("   Possible issues:")
    print("   1. Table 'asl.metadata_framework.ingestion_log' may not exist")
    print("   2. No permissions to access the table")
    print("   3. Query syntax error")

print()

# Test 4: Test Failed Jobs Query
print("Test 4: Test Failed Jobs Query (Today)")
print("-" * 70)
try:
    failed_jobs = service.get_failed_jobs_today()
    
    if failed_jobs:
        print(f"   ✅ Found {len(failed_jobs)} failed jobs for today")
        print()
        print("   Failed Jobs:")
        for job in failed_jobs[:5]:
            job_name = job.get('job_name', 'Unknown')
            resource_type = job.get('resource_type', 'Unknown')
            error = job.get('error_message', 'No error message')[:100]
            print(f"      • [{resource_type}] {job_name}")
            print(f"        Error: {error}...")
    else:
        print("   ✅ No failed jobs found for today (Good news!)")
except Exception as e:
    print(f"   ❌ Query failed: {e}")

print()

# Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()
print("✅ Next Steps:")
print("   1. Navigate to http://127.0.0.1:8000/dashboards/adf/")
print("   2. Click 'VIEW' on 'ADF Status' report")
print("   3. Click 'VIEW' on 'Databricks & ADF Failed Jobs' report")
print("   4. Data will be fetched from Databricks in real-time")
print()
print("💡 Tips:")
print("   • Data is cached for 2 minutes to improve performance")
print("   • Queries fetch only today's data for fast response")
print("   • Failed jobs are highlighted in red for easy identification")
print()
print("=" * 70)
