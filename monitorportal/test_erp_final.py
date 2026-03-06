import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd
import json

print("=" * 80)
print("FINAL ERP TRACKING DESIGN")
print("=" * 80)

# Query 1: Get last 8 distinct run IDs
print("\n1. Last 8 ERP Runs (by TASKFLOW_RUN_ID):")
query_last_8 = """
WITH run_summary AS (
    SELECT 
        r.TASKFLOW_RUN_ID,
        MIN(r.START_TIME) AS run_start_time,
        MAX(CASE 
            WHEN r.ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_START' 
            THEN r.START_TIME 
        END) AS marker_start_time,
        MAX(CASE 
            WHEN r.ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END' AND r.STATUS = 'SUCCESS'
            THEN r.END_TIME 
        END) AS marker_end_time,
        COUNT(*) AS total_jobs,
        SUM(CASE WHEN  r.STATUS = 'SUCCESS' THEN 1 ELSE 0 END) AS succeeded,
        SUM(CASE WHEN r.STATUS = 'RUNNING' THEN 1 ELSE 0 END) AS running,
        SUM(CASE WHEN r.STATUS = 'FAILED' THEN 1 ELSE 0 END) AS failed,
        SUM(CASE WHEN r.STATUS IN ('SUSPENDED', 'CHILD_SUSPENDED') THEN 1 ELSE 0 END) AS suspended
    FROM MAPDQPRD.IICS_CDI_RUN_INFO r
    WHERE r.LOCATION IN (
        'CDW_DSL_ERP\\Workflows',
        'CDW_DSL_ERP\\Sessions',
        'CDW_ASL_SAPS4\\Workflows',
        'ASL_ERP_DATAHUB\\Workflows'
    )
    AND r.ASSET_NAME NOT LIKE '%TAX%'
    AND r.START_TIME >= SYSDATE - 3
    GROUP BY r.TASKFLOW_RUN_ID
)
SELECT 
    TASKFLOW_RUN_ID,
    TO_CHAR(
        FROM_TZ(CAST(run_start_time AS TIMESTAMP), 'UTC')
        AT TIME ZONE 'America/Los_Angeles',
        'DD-MON-YYYY HH12:MI AM'
    ) AS run_label,
    TO_CHAR(
        FROM_TZ(CAST(marker_start_time AS TIMESTAMP), 'UTC')
        AT TIME ZONE 'America/Los_Angeles',
        'DD-MON-YYYY HH12:MI:SS AM'
    ) AS start_time_pst,
    TO_CHAR(
        FROM_TZ(CAST(marker_end_time AS TIMESTAMP), 'UTC')
        AT TIME ZONE 'America/Los_Angeles',
        'DD-MON-YYYY HH12:MI:SS AM'
    ) AS end_time_pst,
    total_jobs,
    succeeded,
    running,
    failed,
    suspended,
    ROUND(succeeded * 100.0 / total_jobs, 1) AS success_rate,
    CASE 
        WHEN marker_end_time IS NOT NULL THEN 'SUCCESS'
        WHEN running > 0 THEN 'RUNNING'
        WHEN failed > 0 THEN 'FAILED'
        WHEN suspended > 0 THEN 'SUSPENDED'
        ELSE 'UNKNOWN'
    END AS run_status
FROM run_summary
ORDER BY run_start_time DESC
FETCH FIRST 8 ROWS ONLY
"""

last_8_runs = fetch_all_mapdqprd(query_last_8)
print(f"Found {len(last_8_runs)} runs")
print(json.dumps(last_8_runs, indent=2, default=str))

# Query 2: Get current run details
if last_8_runs:
    latest_run_id = last_8_runs[0]['taskflow_run_id']
    print(f"\n2. Current Run Details (TASKFLOW_RUN_ID={latest_run_id}):")
    
    query_current = f"""
    SELECT 
        ASSET_NAME AS asset_name,
        SUBTASK_ASSET_NAME AS subtask_asset_name,
        LOCATION AS location,
        TO_CHAR(
            FROM_TZ(CAST(START_TIME AS TIMESTAMP), 'UTC')
            AT TIME ZONE 'America/Los_Angeles',
            'DD-MON-YYYY HH12:MI:SS AM'
        ) AS start_time_pst,
        TO_CHAR(
            FROM_TZ(CAST(END_TIME AS TIMESTAMP), 'UTC')
            AT TIME ZONE 'America/Los_Angeles',
            'DD-MON-YYYY HH12:MI:SS AM'
        ) AS end_time_pst,
        STATUS AS status
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = '{latest_run_id}'
    AND LOCATION IN (
        'CDW_DSL_ERP\\Workflows',
        'CDW_DSL_ERP\\Sessions',
        'CDW_ASL_SAPS4\\Workflows',
        'ASL_ERP_DATAHUB\\Workflows'
    )
    AND ASSET_NAME NOT LIKE '%TAX%'
    ORDER BY
        CASE
            WHEN STATUS = 'FAILED' THEN 0
            WHEN STATUS IN ('SUSPENDED', 'CHILD_SUSPENDED') THEN 1
            WHEN STATUS = 'RUNNING' THEN 2
            WHEN STATUS = 'SUCCESS' THEN 3
            ELSE 4
        END,
        START_TIME DESC
    """
    
    current_jobs = fetch_all_mapdqprd(query_current)
    print(f"Found {len(current_jobs)} jobs in current run")
    
    # Group by status
    status_groups = {}
    for job in current_jobs:
        status = job['status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(job)
    
    print(f"\nStatus breakdown:")
    for status, jobs in status_groups.items():
        print(f"  {status}: {len(jobs)} jobs")
        if len(jobs) <= 3:
            for job in jobs:
                print(f"    - {job['asset_name']}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print("✓ Using TASKFLOW_RUN_ID to group jobs by run")
print("✓ Start time from: s_m_Load_ERP_MASTER_ICSM_ENTRY_START")
print("✓ End time from: s_m_Load_ERP_MASTER_ICSM_ENTRY_END (when SUCCESS)")
print("✓ Current run: End time is NULL (still running)")
print("✓ All times converted to PST")
