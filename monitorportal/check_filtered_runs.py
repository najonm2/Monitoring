#!/usr/bin/env python
"""Check the recent runs that are being filtered out"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portal'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("=" * 80)
print("CHECKING FILTERED RUNS (Last 24 hours)")
print("=" * 80)
print()

query = """
WITH all_recent_runs AS (
    SELECT DISTINCT 
        TASKFLOW_RUN_ID,
        MIN(START_TIME) as first_start
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 1
    GROUP BY TASKFLOW_RUN_ID
    ORDER BY MIN(START_TIME) DESC
    FETCH FIRST 10 ROWS ONLY
),
run_details AS (
    SELECT 
        r.TASKFLOW_RUN_ID,
        r.first_start,
        TO_CHAR(r.first_start, 'DD-MON HH12:MI AM') as start_label,
        COUNT(*) as total_records,
        SUM(CASE WHEN i.STATUS = 'CHILD_SUSPENDED' THEN 1 ELSE 0 END) as suspended_count,
        SUM(CASE WHEN i.STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN i.STATUS = 'FAILED' THEN 1 ELSE 0 END) as failed_count,
        SUM(CASE WHEN i.STATUS = 'RUNNING' THEN 1 ELSE 0 END) as running_count,
        COUNT(DISTINCT i.SUBTASK_ASSET_NAME) as subtask_count
    FROM all_recent_runs r
    LEFT JOIN MAPDQPRD.IICS_CDI_RUN_INFO i 
        ON r.TASKFLOW_RUN_ID = i.TASKFLOW_RUN_ID
    GROUP BY r.TASKFLOW_RUN_ID, r.first_start
)
SELECT 
    start_label,
    TASKFLOW_RUN_ID,
    CASE 
        WHEN suspended_count = total_records THEN 'ABANDONED (all CHILD_SUSPENDED)'
        WHEN success_count > 0 OR failed_count > 0 THEN 'VALID RUN'
        ELSE 'UNKNOWN'
    END as run_type,
    total_records,
    subtask_count,
    suspended_count,
    success_count,
    failed_count,
    running_count
FROM run_details
ORDER BY first_start DESC
"""

runs = fetch_all_mapdqprd(query)

if runs:
    for run in runs:
        print(f"Run: {run['start_label']}")
        print(f"   Type: {run['run_type']}")
        print(f"   Total Records: {run['total_records']}, Subtasks: {run['subtask_count']}")
        print(f"   Status Breakdown: ✓{run['success_count']} ✗{run['failed_count']} " 
              f"▶{run['running_count']} ⏸{run['suspended_count']}")
        print()

print("=" * 80)
print("EXPLANATION:")
print("=" * 80)
print("The current query filters out runs where ALL records are CHILD_SUSPENDED")
print("(marked as 'abandoned'). This is removing recent valid runs from display!")
print()
print("SOLUTION: Remove the 'abandoned' filter OR check actual job executions.")
print("=" * 80)
