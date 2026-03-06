"""
Investigate how jobs are stored in IICS_CDI_RUN_INFO
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("\n" + "="*70)
print("  🔍 INVESTIGATING JOB RECORDS IN IICS_CDI_RUN_INFO")
print("="*70)

# Get the latest TASKFLOW_RUN_ID for the 08:00 AM run
query1 = """
SELECT TASKFLOW_RUN_ID
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 1
ORDER BY START_TIME DESC
FETCH FIRST 1 ROWS ONLY
"""

try:
    result = fetch_all_mapdqprd(query1)
    if result and len(result) > 0:
        taskflow_run_id = result[0].get('taskflow_run_id')
        print(f"\n📌 Latest TASKFLOW_RUN_ID: {taskflow_run_id}")
        
        # Now get all records for this run
        query2 = f"""
        SELECT 
            ASSET_NAME,
            ASSET_TYPE,
            STATUS,
            START_TIME,
            END_TIME,
            LOCATION,
            IICS_CDI_RUN_INFO_KEY_ID
        FROM MAPDQPRD.IICS_CDI_RUN_INFO
        WHERE TASKFLOW_RUN_ID = '{taskflow_run_id}'
        AND LOCATION IN (
            'CDW_DSL_ERP\\Workflows',
            'CDW_DSL_ERP\\Sessions',
            'CDW_ASL_SAPS4\\Workflows',
            'ASL_ERP_DATAHUB\\Workflows'
        )
        AND ASSET_NAME NOT LIKE '%TAX%'
        ORDER BY START_TIME DESC, ASSET_NAME
        """
        
        jobs = fetch_all_mapdqprd(query2)
        
        print(f"\n📊 Found {len(jobs)} records for this run:")
        print("\n" + "="*70)
        
        # Group by ASSET_NAME to see if there are duplicates
        from collections import defaultdict
        by_asset = defaultdict(list)
        
        for job in jobs:
            asset = job.get('asset_name', 'Unknown')
            by_asset[asset].append(job)
        
        print(f"\n📋 Unique Assets: {len(by_asset)}")
        print(f"📋 Total Records: {len(jobs)}")
        
        print("\n🔍 Checking for duplicate ASSET_NAMEs (multiple status updates):")
        duplicates_found = False
        for asset, records in by_asset.items():
            if len(records) > 1:
                duplicates_found = True
                print(f"\n   📌 {asset} - {len(records)} records:")
                for i, rec in enumerate(records, 1):
                    status = rec.get('status', 'Unknown')
                    start = rec.get('start_time', 'N/A')
                    end = rec.get('end_time', 'N/A')
                    key = rec.get('iics_cdi_run_info_key_id', 'N/A')
                    print(f"      {i}. Status: {status:10} Start: {start} End: {end} Key: {key}")
        
        if not duplicates_found:
            print("\n   ℹ️ No duplicate ASSET_NAMEs found - each job has only 1 record")
            print("\n   This means status doesn't update in place - it's always the latest")
        
        print("\n" + "="*70)
        print("  📊 STATUS BREAKDOWN")
        print("="*70)
        
        status_counts = {}
        for job in jobs:
            status = job.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   {status:15}: {count} jobs")
        
        print("\n📌 Expected from IDMC: 10 Success, 2 Running")
        print(f"📊 Portal Query Result: {status_counts.get('SUCCESS', 0)} Success, {status_counts.get('RUNNING', 0)} Running")
                
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
