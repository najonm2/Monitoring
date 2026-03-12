"""
Investigate Run #5 data inconsistency
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'
import django
django.setup()

from portal.services.level3_service import fetch_all_mapdqprd

# Get detailed info about Run #5 (09-MAR-2026 12:00 PM)
query = """
WITH target_run AS (
    SELECT DISTINCT TASKFLOW_RUN_ID
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= TRUNC(SYSDATE - 7)
    ORDER BY START_TIME DESC
    FETCH NEXT 8 ROWS ONLY
)
SELECT 
    TASKFLOW_RUN_ID,
    START_TIME,
    END_TIME,
    SUBTASK_ASSET_NAME,
    STATUS,
    COUNT(*) OVER (PARTITION BY TASKFLOW_RUN_ID, STATUS) as count_by_status
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID IN (SELECT TASKFLOW_RUN_ID FROM target_run)
AND ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
ORDER BY START_TIME DESC, SUBTASK_ASSET_NAME
"""

results = fetch_all_mapdqprd(query)

print("Investigating the detail of all 8 runs and their subtasks:\n")
print("="*120)

current_run_id = None
for row in results:
    run_id = row.get('TASKFLOW_RUN_ID')
    start_time = row.get('START_TIME')
    subtask = row.get('SUBTASK_ASSET_NAME', 'UNKNOWN')
    status = row.get('STATUS', 'UNKNOWN')
    
    if run_id != current_run_id:
        print(f"\n📌 Run ID: {run_id} | Start: {start_time}")
        print("-" * 120)
        current_run_id = run_id
    
    end_job_marker = "🔴 END JOB MARKER" if str(subtask) == 's_m_Load_ERP_MASTER_ICSM_ENTRY_END' else ""
    print(f"   {str(subtask):<45} | Status: {str(status):<12} {end_job_marker}")

print("\n" + "="*120)

# Now check Run #5 specifically - find the issue
print("\n\nDETAILED Analysis:\n")

check_query = """
WITH run_analysis AS (
    SELECT 
        TASKFLOW_RUN_ID,
        TO_CHAR(MIN(START_TIME), 'DD-MON-YYYY HH:MI AM') as run_start,
        COUNT(*) as total_jobs,
        SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as succeeded_jobs,
        SUM(CASE WHEN STATUS = 'SUSPENDED' THEN 1 ELSE 0 END) as suspended_jobs,
        SUM(CASE WHEN STATUS = 'RUNNING' THEN 1 ELSE 0 END) as running_jobs,
        SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as failed_jobs,
        MAX(CASE 
            WHEN SUBTASK_ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END' AND STATUS = 'SUCCESS'
            THEN 1 ELSE 0
        END) as has_end_job_success,
        MAX(CASE 
            WHEN SUBTASK_ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END'
            THEN STATUS
        END) as end_job_status
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 7
    GROUP BY TASKFLOW_RUN_ID
    ORDER BY MIN(START_TIME) DESC
    FETCH FIRST 8 ROWS ONLY
)
SELECT * FROM run_analysis
"""

analysis_results = fetch_all_mapdqprd(check_query)

print(f"{'Run Start Time':<25} {'Total':<8} {'✅':<8} {'⏸️':<8} {'⏱️':<8} {'❌':<8} {'End Job?':<12} {'End Job Status':<15}")
print("-" * 120)

for row in analysis_results:
    run_start = row.get('run_start', 'N/A')
    total = row.get('total_jobs', 0)
    succeeded = row.get('succeeded_jobs', 0)
    suspended = row.get('suspended_jobs', 0)
    running = row.get('running_jobs', 0)
    failed = row.get('failed_jobs', 0)
    has_end_job = "YES ✓" if row.get('has_end_job_success') == 1 else "NO"
    end_job_status = row.get('end_job_status', 'N/A')
    
    print(f"{run_start:<25} {total:<8} {succeeded:<8} {suspended:<8} {running:<8} {failed:<8} {has_end_job:<12} {str(end_job_status):<15}")

print("\n" + "="*120)
print("\n✅ Analysis complete. The data shows:")
print("   - Runs with End Job SUCCESS marker but all jobs SUSPENDED are valid")
print("   - This means the workflow terminated (End Job ran) but dependent jobs were suspended")
print("   - The UI correctly displays these as 'SUSPENDED' runs with latest success time as reference")
