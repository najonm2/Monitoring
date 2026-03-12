"""
Check if there are multiple master workflow entries per TASKFLOW_RUN_ID
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# Check TASKFLOW_RUN_ID 1215479110705471488 which shows as SUSPENDED but should be SUCCESS
query = """
SELECT 
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'MM/DD HH24:MI:SS') as START_TIME,
    TO_CHAR(END_TIME, 'MM/DD HH24:MI:SS') as END_TIME,
    ASSET_NAME,
    SUBTASK_ASSET_NAME,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = '1215479110705471488'
ORDER BY START_TIME, SUBTASK_ASSET_NAME NULLS FIRST
"""

rows = fetch_all_mapdqprd(query)

print("=" * 120)
print(f"TASKFLOW_RUN_ID: 1215479110705471488 (Should be SUCCESS according to IDMC)")
print("=" * 120)
print(f"Total records: {len(rows)}")
print()

# Separate master and subtask records
master_records = [r for r in rows if not r.get('subtask_asset_name')]
subtask_records = [r for r in rows if r.get('subtask_asset_name')]

print(f"Master workflow records: {len(master_records)}")
print(f"Subtask records: {len(subtask_records)}")
print()

if master_records:
    print("MASTER WORKFLOW ENTRIES:")
    print(f"{'START_TIME':<20} {'END_TIME':<20} {'STATUS':<15}")
    print("-" * 60)
    for r in master_records:
        print(f"{r.get('start_time'):<20} {r.get('end_time') or 'N/A':<20} {r.get('status'):<15}")
    print()

# Count subtasks by status
from collections import Counter
subtask_status_counts = Counter([r.get('status') for r in subtask_records])

print("SUBTASK STATUS SUMMARY:")
for status, count in subtask_status_counts.items():
    print(f"  {status}: {count}")
print()

# Show first 15 subtasks
print("FIRST 15 SUBTASKS:")
print(f"{'START_TIME':<20} {'END_TIME':<20} {'SUBTASK_NAME':<40} {'STATUS':<15}")
print("-" * 120)
for r in subtask_records[:15]:
    subtask_name = r.get('subtask_asset_name', 'N/A')[:38]
    print(f"{r.get('start_time'):<20} {r.get('end_time') or 'N/A':<20} {subtask_name:<40} {r.get('status'):<15}")
