"""
Investigate actual data structure for latest ERP run
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# Get latest TASKFLOW_RUN_ID
query1 = """
SELECT DISTINCT TASKFLOW_RUN_ID, START_TIME
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 1
ORDER BY START_TIME DESC
FETCH FIRST 1 ROWS ONLY
"""

print("Getting latest TASKFLOW_RUN_ID...")
result = fetch_all_mapdqprd(query1)
if result:
    latest_id = result[0]['taskflow_run_id']
    print(f"\nLatest TASKFLOW_RUN_ID: {latest_id}")
    
    # Now get ALL rows for this ID
    query2 = f"""
    SELECT 
        ASSET_NAME,
        SUBTASK_ASSET_NAME,
        LOCATION,
        STATUS,
        TASKFLOW_RUN_ID,
        START_TIME
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = '{latest_id}'
    ORDER BY START_TIME, ASSET_NAME
    """
    
    print(f"\nQuerying all jobs for TASKFLOW_RUN_ID {latest_id}...")
    all_jobs = fetch_all_mapdqprd(query2)
    
    print(f"\nTotal rows: {len(all_jobs)}")
    print("\nAll rows:")
    print("-" * 120)
    for i, job in enumerate(all_jobs, 1):
        asset = job['asset_name'][:40].ljust(40)
        subtask = str(job.get('subtask_asset_name', ''))[:30].ljust(30)
        location = job['location'][:30].ljust(30)
        status = job['status'].ljust(10)
        print(f"{i:2d}. {asset} | {subtask} | {location} | {status}")
    
    # Count unique assets
    unique_assets = {}
    for job in all_jobs:
        asset = job['asset_name']
        if asset not in unique_assets:
            unique_assets[asset] = 0
        unique_assets[asset] += 1
    
    print(f"\nUnique assets ({len(unique_assets)}):")
    for asset, count in sorted(unique_assets.items()):
        print(f"  {asset}: {count} rows")
    
    # Check locations
    locations = {}
    for job in all_jobs:
        loc = job['location']
        if loc not in locations:
            locations[loc] = 0
        locations[loc] += 1
    
    print(f"\nLocations ({len(locations)}):")
    for loc, count in sorted(locations.items()):
        print(f"  {loc}: {count} rows")
