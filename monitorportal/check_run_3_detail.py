"""
Check specific run details to understand status discrepancy
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# Check run #3 (12:00 AM) which IDMC shows as SUCCESS but we show as SUSPENDED
print("Checking Run #3: 06-MAR-2026 12:00 AM (IDMC: Success, Portal: Suspended)")
print("="*100)

query = """
SELECT 
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'DD-MON-YYYY HH12:MI AM') as start_time,
    STATUS,
    END_TIME
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= TO_DATE('2026-03-05 23:00:00', 'YYYY-MM-DD HH24:MI:SS')
AND START_TIME < TO_DATE('2026-03-06 01:00:00', 'YYYY-MM-DD HH24:MI:SS')
ORDER BY START_TIME DESC
"""

results = fetch_all_mapdqprd(query)

print(f"\nFound {len(results)} master workflow entries around 12:00 AM:")
for row in results:
    taskflow_id = row['taskflow_run_id']
    start = row['start_time']
    status = row['status']
    end_time = row.get('end_time', 'NULL')
    print(f"\n  TASKFLOW_RUN_ID: {taskflow_id}")
    print(f"  START_TIME: {start}")
    print(f"  STATUS: {status}")
    print(f"  END_TIME: {end_time}")
    
    # Get all jobs for this run
    query2 = f"""
    SELECT 
        SUBTASK_ASSET_NAME,
        STATUS,
        TO_CHAR(START_TIME, 'HH24:MI:SS') as start_time,
        TO_CHAR(END_TIME, 'HH24:MI:SS') as end_time
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = '{taskflow_id}'
    AND ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    ORDER BY START_TIME
    """
    
    jobs = fetch_all_mapdqprd(query2)
    print(f"\n  Child jobs ({len(jobs)}):")
    
    status_counts = {}
    for job in jobs:
        subtask = job['subtask_asset_name'][:45]
        status = job['status']
        start_t = job.get('start_time', 'N/A')
        end_t = job.get('end_time', 'N/A')
        
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
        
        print(f"    - {subtask.ljust(45)} | {status.ljust(10)} | {start_t} - {end_t}")
    
    print(f"\n  Status Summary: {status_counts}")

print("\n" + "="*100)
print("ANALYSIS:")
print("="*100)
print("If all jobs show SUSPENDED but IDMC shows SUCCESS:")
print("  → Database status is outdated/not updated after completion")
print("  → Need to check END_TIME to determine if run completed")
print("  → If END_TIME exists, use that to determine final status")
