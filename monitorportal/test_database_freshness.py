"""
Check raw data to compare database vs IDMC
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("\n" + "="*70)
print("  🔍 CHECKING DATABASE UPDATE TIMING")
print("="*70)

query = """
SELECT 
    ASSET_NAME,
    STATUS,
    LOCATION,
    START_TIME,
    END_TIME,
    UPDATE_TIME,
    TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') AS current_time
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = (
    SELECT TASKFLOW_RUN_ID
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 1
    ORDER BY START_TIME DESC
    FETCH FIRST 1 ROWS ONLY
)
AND LOCATION IN (
    'CDW_DSL_ERP\\Workflows',
    'CDW_DSL_ERP\\Sessions',
    'CDW_ASL_SAPS4\\Workflows',
    'ASL_ERP_DATAHUB\\Workflows'
)
AND ASSET_NAME NOT LIKE '%TAX%'
ORDER BY UPDATE_TIME DESC
"""

try:
    jobs = fetch_all_mapdqprd(query)
    
    print(f"\n📊 Found {len(jobs)} job records")
    
    if jobs and len(jobs) > 0:
        current_time = jobs[0].get('current_time', 'Unknown')
        print(f"\n🕐 Database Time: {current_time}")
        print(f"🕐 IDMC Update Time: 8:37:54 AM PST (16:37:54 UTC)")
        
        print("\n" + "="*70)
        print("  📋 JOB STATUS IN DATABASE")
        print("="*70)
        
        status_counts = {}
        for job in jobs[:15]:  # Show first 15
            asset = job.get('asset_name', 'Unknown')
            status = job.get('status', 'Unknown')
            location = job.get('location', 'Unknown')
            end_time = job.get('end_time', 'None')
            update_time = job.get('update_time', 'Unknown')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            
            status_icon = {
                'SUCCESS': '✅',
                'RUNNING': '⏱️',
                'FAILED': '❌',
                'SUSPENDED': '⏸️'
            }.get(status, '❓')
            
            print(f"\n{status_icon} {asset[:50]}")
            print(f"   Status: {status:10}  End: {end_time}")
            print(f"   Location: {location}")
            print(f"   Last Update: {update_time}")
        
        print("\n" + "="*70)
        print("  📊 SUMMARY")
        print("="*70)
        
        print(f"\n🗄️ Database (Portal):")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        print(f"\n🌐 IDMC (Live):")
        print(f"   SUCCESS: 10")
        print(f"   RUNNING: 2")
        
        print("\n" + "="*70)
        print("  💡 ANALYSIS")
        print("="*70)
        
        db_success = status_counts.get('SUCCESS', 0)
        db_running = status_counts.get('RUNNING', 0)
        
        if db_success == 10 and db_running == 2:
            print("\n✅ Database is UP TO DATE with IDMC!")
            print("   Query logic needs review.")
        else:
            print("\n⚠️ DATABASE IS STALE!")
            print(f"\n   Database shows: {db_success} Success, {db_running} Running")
            print(f"   IDMC shows: 10 Success, 2 Running")
            print(f"\n   💡 The IICS_CDI_RUN_INFO table hasn't been updated yet.")
            print(f"      Jobs that completed aren't reflected in the database.")
            print(f"\n   📌 This is a data refresh issue, not a query issue.")
            print(f"      Wait for the table to sync with IDMC or check ETL process.")
            
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
