#!/usr/bin/env python
"""
Check if the 3 PM ERP run has recovery records (status changes from SUSPENDED to SUCCESS)
"""
import sys
import os
import datetime

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

def print_job_analysis(job_name, records):
    """Print analysis of job records"""
    if len(records) == 1:
        r = records[0]
        status_icon = "✓" if r['status'] == 'SUCCESS' else "✗" if r['status'] == 'FAILED' else "⏸" if 'SUSPENDED' in r['status'] else "▶"
        print(f"\n  📋 {job_name}")
        print(f"     {status_icon} Status: {r['status']}")
        print(f"     ⏰ Start: {r['start_time']}, End: {r['end_time'] or 'RUNNING'}")
    else:
        print(f"\n  📋 {job_name} 🔄 MULTIPLE RECORDS ({len(records)})")
        for i, r in enumerate(records, 1):
            status_icon = "✓" if r['status'] == 'SUCCESS' else "✗" if r['status'] == 'FAILED' else "⏸" if 'SUSPENDED' in r['status'] else "▶"
            print(f"     Record #{i}: {status_icon} {r['status']} | Start: {r['start_time']}, End: {r['end_time'] or 'RUNNING'}")
        
        # Check if recovered
        statuses = [r['status'] for r in records]
        if 'SUCCESS' in statuses and 'CHILD_SUSPENDED' in statuses:
            print(f"     ✅ RECOVERY DETECTED: Went from SUSPENDED → SUCCESS")
        elif 'SUCCESS' in statuses and 'FAILED' in statuses:
            print(f"     ✅ RECOVERY DETECTED: Went from FAILED → SUCCESS")

# Get the 3 PM run details (TASKFLOW_RUN_ID from test output)
query = """
SELECT 
    TASKFLOW_RUN_ID,
    COALESCE(SUBTASK_ASSET_NAME, ASSET_NAME) as job_name,
    STATUS,
    TO_CHAR(START_TIME, 'DD-MON HH24:MI:SS') as start_time,
    TO_CHAR(END_TIME, 'DD-MON HH24:MI:SS') as end_time,
    CASE WHEN END_TIME IS NULL THEN 'No' ELSE 'Yes' END as completed
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID IN (
    SELECT DISTINCT TASKFLOW_RUN_ID
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 1
    AND START_TIME < SYSDATE
    ORDER BY START_TIME DESC
    FETCH FIRST 2 ROWS ONLY
)
AND COALESCE(SUBTASK_ASSET_NAME, ASSET_NAME) NOT LIKE '%TAX%'
ORDER BY TASKFLOW_RUN_ID DESC, job_name, START_TIME DESC
"""

print("=" * 80)
print("CHECKING RECOVERY STATUS FOR RECENT RUNS")
print("=" * 80)
print()

results = fetch_all_mapdqprd(query)

if not results:
    print("❌ No results found")
    sys.exit(1)

# Group by TASKFLOW_RUN_ID and job_name
current_run = None
current_job = None
job_records = []

for row in results:
    run_id = row['taskflow_run_id']
    job = row['job_name']
    
    if current_run != run_id:
        # New run - print previous job records if any
        if job_records:
            print_job_analysis(current_job, job_records)
        
        current_run = run_id
        current_job = job
        job_records = [row]
        print(f"\n{'='*80}")
        print(f"RUN: {run_id}")
        print(f"{'='*80}")
    elif current_job != job:
        # New job within same run
        if job_records:
            print_job_analysis(current_job, job_records)
        current_job = job
        job_records = [row]
    else:
        # Same job - additional record
        job_records.append(row)

# Print last job
if job_records:
    print_job_analysis(current_job, job_records)

print("\n" + "=" * 80)
