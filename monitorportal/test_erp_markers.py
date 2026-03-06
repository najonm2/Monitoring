import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd
import json

print("=" * 80)
print("INVESTIGATE: Do Start/End Markers Exist?")
print("=" * 80)

# Check for marker sessions
query_markers = """
SELECT 
    ASSET_NAME,
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS start_time_raw,
    TO_CHAR(END_TIME, 'YYYY-MM-DD HH24:MI:SS') AS end_time_raw,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE (ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_START' 
       OR ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END')
AND START_TIME >= SYSDATE - 3
ORDER BY START_TIME DESC
FETCH FIRST 20 ROWS ONLY
"""

markers = fetch_all_mapdqprd(query_markers)
print(f"\nFound {len(markers)} marker sessions:")
print(json.dumps(markers, indent=2, default=str))

# Check for master workflow
print("\n" + "=" * 80)
print("Check: wkf_ERP_DAILY_REFRESH_MASTER")
print("=" * 80)

query_master = """
SELECT 
    ASSET_NAME,
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS start_time_raw,
    TO_CHAR(END_TIME, 'YYYY-MM-DD HH24:MI:SS') AS end_time_raw,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 3
ORDER BY START_TIME DESC
FETCH FIRST 10 ROWS ONLY
"""

master = fetch_all_mapdqprd(query_master)
print(f"\nFound {len(master)} master workflow runs:")
print(json.dumps(master, indent=2, default=str))

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
if markers:
    print(f"+ Start/End markers exist: {len(markers)} found")
    if markers[0].get('taskflow_run_id'):
        print(f"   Sample TASKFLOW_RUN_ID: {markers[0]['taskflow_run_id']}")
    else:
        print("   WARNING: Markers have NO TASKFLOW_RUN_ID!")
else:
    print("- NO start/end markers found in last 3 days!")

if master:
    print(f"+ Master workflow exists: {len(master)} runs found")
    if master[0].get('taskflow_run_id'):
        print(f"   Sample TASKFLOW_RUN_ID: {master[0]['taskflow_run_id']}")
    else:
        print("   WARNING: Master workflow has NO TASKFLOW_RUN_ID!")
else:
    print("- NO master workflow runs found!")
