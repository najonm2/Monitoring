"""
Find the successful run that corresponds to the recovered execution
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# The user's IDMC shows 7:00 PM PDT (Mar 8) = 02:00 UTC (Mar 9) start, 9:45 PM end
# Let's find all master workflow records from that time period
query = """
SELECT 
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'MM/DD HH24:MI:SS') as START_TIME,
    TO_CHAR(END_TIME, 'MM/DD HH24:MI:SS') as END_TIME,
    STATUS,
    ASSET_NAME,
    SUBTASK_ASSET_NAME
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND SUBTASK_ASSET_NAME IS NULL  -- Master records only
AND START_TIME >= TO_DATE('2026-03-09 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
AND START_TIME <= TO_DATE('2026-03-09 06:00:00', 'YYYY-MM-DD HH24:MI:SS')
ORDER BY START_TIME DESC
"""

rows = fetch_all_mapdqprd(query)

print("=" * 120)
print("MASTER WORKFLOW RECORDS (Mar 9 00:00-06:00 UTC)")
print("=" * 120)
print(f"Total master records: {len(rows)}")
print()

print(f"{'TASKFLOW_RUN_ID':<28} {'START_TIME':<20} {'END_TIME':<20} {'STATUS':<15}")
print("-" * 90)
for r in rows:
    run_id = str(r.get('taskflow_run_id'))[:26]
    print(f"{run_id:<28} {r.get('start_time'):<20} {r.get('end_time') or 'N/A':<20} {r.get('status'):<15}")
print()

# Now check which TASKFLOW_RUN_IDs have subtasks
print("=" * 120)
print("CHECKING SUBTASK COUNTS FOR EACH RUN")
print("=" * 120)

for r in rows:
    run_id = r.get('taskflow_run_id')
    
    subtask_query = f"""
    SELECT COUNT(*) as subtask_count,
           SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
           SUM(CASE WHEN STATUS = 'CHILD_SUSPENDED' THEN 1 ELSE 0 END) as suspended_count
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = '{run_id}'
    AND SUBTASK_ASSET_NAME IS NOT NULL
    """
    
    subtask_rows = fetch_all_mapdqprd(subtask_query)
    if subtask_rows:
        counts = subtask_rows[0]
        print(f"Run ID {str(run_id)[:26]}: {counts.get('subtask_count')} subtasks, {counts.get('success_count')} success, {counts.get('suspended_count')} suspended")
