"""
Check the structure - are there any records where SUBTASK_ASSET_NAME IS NULL?
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# Check if there are ANY records with NULL SUBTASK_ASSET_NAME
query = """
SELECT 
    COUNT(*) as total_count,
    SUM(CASE WHEN SUBTASK_ASSET_NAME IS NULL THEN 1 ELSE 0 END) as null_subtask_count,
    SUM(CASE WHEN SUBTASK_ASSET_NAME IS NOT NULL THEN 1 ELSE 0 END) as not_null_subtask_count
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 2
"""

rows = fetch_all_mapdqprd(query)

print("=" * 80)
print("CHECKING SUBTASK_ASSET_NAME COLUMN")
print("=" * 80)

if rows:
    r = rows[0]
    print(f"Total records: {r.get('total_count')}")
    print(f"SUBTASK_ASSET_NAME IS NULL: {r.get('null_subtask_count')}")
    print(f"SUBTASK_ASSET_NAME IS NOT NULL: {r.get('not_null_subtask_count')}")
    print()
    
    if r.get('null_subtask_count') == 0:
        print("⚠️  ALL records have SUBTASK_ASSET_NAME populated!")
        print("This means there are NO separate 'master' records.")
        print("The master workflow status must be inferred from subtask statuses.")
    else:
        print("✅ Some records have NULL SUBTASK_ASSET_NAME (master records exist)")

# Let's check sample records to understand the structure
sample_query = """
SELECT 
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'MM/DD HH24:MI') as START_TIME,
    ASSET_NAME,
    SUBTASK_ASSET_NAME,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 1
ORDER BY START_TIME DESC
FETCH FIRST 5 ROWS ONLY
"""

sample_rows = fetch_all_mapdqprd(sample_query)
print()
print("=" * 80)
print("SAMPLE RECORDS:")
print("=" * 80)
for r in sample_rows:
    print(f"TASKFLOW_RUN_ID: {r.get('taskflow_run_id')}")
    print(f"  ASSET_NAME: {r.get('asset_name')}")
    print(f"  SUBTASK_ASSET_NAME: {r.get('subtask_asset_name') or 'NULL'}")
    print(f"  STATUS: {r.get('status')}")
    print()
