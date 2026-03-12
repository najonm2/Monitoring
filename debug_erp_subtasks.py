"""
Debug ERP Subtasks - Check what's in the database for a SUSPENDED run
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

def debug_suspended_run():
    """Check a specific TASKFLOW_RUN_ID that's showing as SUSPENDED"""
    
    # Get one of the SUSPENDED runs - let's use 08-MAR-2026 12:00 PM (noon)
    # This is showing as SUSPENDED in our dashboard
    query = """
    SELECT 
        TASKFLOW_RUN_ID,
        TO_CHAR(START_TIME, 'MM/DD HH24:MI') as START_TIME,
        ASSET_NAME,
        SUBTASK_ASSET_NAME,
        STATUS,
        TO_CHAR(END_TIME, 'MM/DD HH24:MI') as END_TIME
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 2  -- Last 2 days
    ORDER BY START_TIME DESC, TASKFLOW_RUN_ID, SUBTASK_ASSET_NAME NULLS FIRST
    """
    
    rows = fetch_all_mapdqprd(query)
    
    print("=" * 120)
    print("CHECKING ALL ERP MASTER RUNS (Last 2 Days)")
    print("=" * 120)
    print()
    
    if not rows:
        print("❌ No data found!")
        return
    
    print(f"Found {len(rows)} records")
    print()
    
    # Group by TASKFLOW_RUN_ID
    current_run_id = None
    subtask_count = 0
    master_count = 0
    
    print(f"{'TASKFLOW_RUN_ID':<25} {'START':<12} {'ASSET_NAME':<35} {'SUBTASK':<35} {'STATUS':<12} {'END':<12}")
    print("-" * 120)
    
    for row in rows[:30]:  # Limit to first 30 for readability
        run_id = row.get('taskflow_run_id')
        start = row.get('start_time')
        asset = row.get('asset_name')
        subtask = row.get('subtask_asset_name')
        status = row.get('status')
        end = row.get('end_time')
        
        if current_run_id != run_id:
            if current_run_id:
                print(f"\n  → Master entries: {master_count}, Subtask entries: {subtask_count}\n")
            current_run_id = run_id
            subtask_count = 0
            master_count = 0
            print(f"\n{'='*120}")
            print(f"TASKFLOW_RUN_ID: {run_id}")
            print(f"{'='*120}")
        
        asset_short = asset[:33] if asset else "N/A"
        subtask_short = subtask[:33] if subtask else "---"
        end_short = end if end else "N/A"
        
        if subtask:
            subtask_count += 1
        else:
            master_count += 1
        
        run_id_short = str(run_id)[:23] if run_id else "N/A"
        print(f"{run_id_short:<25} {start:<12} {asset_short:<35} {subtask_short:<35} {status:<12} {end_short:<12}")
    
    print(f"\n  → Master entries: {master_count}, Subtask entries: {subtask_count}")
    
    print()
    print("=" * 120)
    print("KEY INSIGHT:")
    print("=" * 120)
    print("Check if there are multiple entries per subtask (recovery attempts)")
    print("The query should pick the LATEST entry per subtask (ORDER BY START_TIME DESC)")

if __name__ == '__main__':
    debug_suspended_run()
