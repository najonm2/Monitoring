#!/usr/bin/env python
"""
Check if any jobs have multiple records (indicating recovery behavior)
"""
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# Look for jobs with multiple records in the same TASKFLOW_RUN_ID
query = """
WITH job_counts AS (
    SELECT 
        TASKFLOW_RUN_ID,
        COALESCE(SUBTASK_ASSET_NAME, ASSET_NAME) as job_name,
        COUNT(*) as record_count,
        LISTAGG(STATUS, ' → ') WITHIN GROUP (ORDER BY START_TIME) as status_progression,
        MIN(TO_CHAR(START_TIME, 'DD-MON HH24:MI:SS')) as first_start,
        MAX(TO_CHAR(END_TIME, 'DD-MON HH24:MI:SS')) as last_end
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 7
    GROUP BY TASKFLOW_RUN_ID, COALESCE(SUBTASK_ASSET_NAME, ASSET_NAME)
    HAVING COUNT(*) > 1
)
SELECT *
FROM job_counts
ORDER BY record_count DESC, TASKFLOW_RUN_ID DESC
FETCH FIRST 20 ROWS ONLY
"""

print("=" * 100)
print("CHECKING FOR JOBS WITH MULTIPLE RECORDS (Recovery Pattern)")
print("=" * 100)
print()

results = fetch_all_mapdqprd(query)

if not results:
    print("❌ No jobs found with multiple records")
    print("   This means recovery likely UPDATES the existing record rather than creating a new one")
    print()
else:
    print(f"✅ Found {len(results)} jobs with multiple records")
    print()
    for row in results:
        print(f"📋 Job: {row['job_name'][:60]}")
        print(f"   Run ID: {row['taskflow_run_id']}")
        print(f"   Records: {row['record_count']}")
        print(f"   Status Progression: {row['status_progression']}")
        print(f"   First Start: {row['first_start']}")
        print(f"   Last End: {row['last_end']}")
        
        # Check if this shows recovery
        if 'SUSPENDED' in row['status_progression'] and 'SUCCESS' in row['status_progression']:
            print(f"   ✅ RECOVERY PATTERN DETECTED!")
        
        print()

print("=" * 100)
