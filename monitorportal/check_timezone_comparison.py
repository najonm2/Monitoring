#!/usr/bin/env python
"""
Show all ERP master runs with both UTC and MST times to understand timezone conversion
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

# Get all recent master runs with timezone conversion
query = """
WITH master_runs AS (
    SELECT DISTINCT
        TASKFLOW_RUN_ID,
        START_TIME,
        STATUS,
        END_TIME
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 7
),
subtask_counts AS (
    SELECT 
        TASKFLOW_RUN_ID,
        COUNT(*) as total_subtasks,
        SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN STATUS = 'CHILD_SUSPENDED' THEN 1 ELSE 0 END) as suspended_count
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID IN (SELECT TASKFLOW_RUN_ID FROM master_runs)
    AND SUBTASK_ASSET_NAME IS NOT NULL
    GROUP BY TASKFLOW_RUN_ID
)
SELECT 
    m.TASKFLOW_RUN_ID,
    TO_CHAR(m.START_TIME, 'DD-MON-YYYY HH24:MI:SS') as utc_time,
    TO_CHAR(
        FROM_TZ(CAST(m.START_TIME AS TIMESTAMP), 'UTC')
        AT TIME ZONE 'America/Denver',
        'DD-MON-YYYY HH12:MI AM'
    ) AS mst_time,
    m.STATUS,
    CASE WHEN m.END_TIME IS NULL THEN 'NO' ELSE 'YES' END as completed,
    COALESCE(s.success_count, 0) as success_count,
    COALESCE(s.suspended_count, 0) as suspended_count,
    COALESCE(s.total_subtasks, 0) as total_subtasks
FROM master_runs m
LEFT JOIN subtask_counts s ON m.TASKFLOW_RUN_ID = s.TASKFLOW_RUN_ID
ORDER BY m.START_TIME DESC
"""

print("=" * 120)
print("ERP MASTER RUNS - UTC vs MST TIME COMPARISON")
print("=" * 120)
print()

results = fetch_all_mapdqprd(query)

if not results:
    print("❌ No results found")
    sys.exit(1)

print(f"{'#':<3} {'MST Time':<25} {'UTC Time':<22} {'Status':<12} {'Subtasks':<15} {'Overall Status':<15}")
print("=" * 120)

for i, row in enumerate(results, 1):
    mst = row['mst_time']
    utc = row['utc_time']
    status = row['status']
    success = row['success_count']
    suspended = row['suspended_count']
    total = row['total_subtasks']
    
    # Determine overall status
    if success == total and total > 0:
        overall = "✅ SUCCESS"
    elif suspended > 0:
        overall = "⏸ SUSPENDED"
    elif success > 0:
        overall = "🔄 PARTIAL"
    else:
        overall = "❓ UNKNOWN"
    
    subtask_str = f"✓{success} ⏸{suspended}/{total}"
    
    print(f"{i:<3} {mst:<25} {utc:<22} {status:<12} {subtask_str:<15} {overall:<15}")

print("=" * 120)
print()
print("KEY FINDINGS:")
print("  - MST Time = What users see in the dashboard")
print("  - UTC Time = What's stored in the database")  
print("  - MST is typically UTC-7 (Mountain Standard Time)")
print()
print("If the dashboard shows times that don't match IICS Monitor:")
print("  1. Check if IICS Monitor is using UTC or local time")
print("  2. Verify timezone configuration in IICS")
print("  3. Confirm database START_TIME timezone")
print()
