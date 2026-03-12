#!/usr/bin/env python
"""
Helper script to mark ERP runs as manually recovered

Usage:
    python mark_run_recovered.py <TASKFLOW_RUN_ID> <recovered_by> <notes>

Example:
    python mark_run_recovered.py 1215720696580263936 "john.doe@example.com" "Manually resumed all tasks"

Completion time is automatically fetched from database (latest subtask completion time)
"""
import sys
import os
from datetime import datetime

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.models import ERPRunRecovery
from portal.db.oracle_client import fetch_all_mapdqprd


def mark_run_as_recovered(taskflow_run_id, recovered_by, notes, final_status='SUCCESS'):
    """
    Mark a run as manually recovered
    
    Args:
        taskflow_run_id: IICS TASKFLOW_RUN_ID
        recovered_by: Email or name of person who recovered
        notes: Recovery notes
        final_status: Final status (default: SUCCESS)
    
    Completion time is automatically fetched from database (latest subtask completion)
    """
    # First, check if run exists and get start time + completion time from IICS data
    query = f"""
    SELECT 
        TASKFLOW_RUN_ID,
        TO_CHAR(
            FROM_TZ(CAST(START_TIME AS TIMESTAMP), 'UTC')
            AT TIME ZONE 'America/Denver',
            'YYYY-MM-DD HH24:MI:SS'
        ) AS run_start_time_mst,
        STATUS,
        TO_CHAR(
            FROM_TZ(CAST(MAX(UPDATE_TIME) AS TIMESTAMP), 'UTC')
            AT TIME ZONE 'America/Denver',
            'YYYY-MM-DD HH24:MI:SS'
        ) AS completion_time_mst
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = '{taskflow_run_id}'
    AND ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    GROUP BY TASKFLOW_RUN_ID, START_TIME, STATUS
    """
    
    runs = fetch_all_mapdqprd(query)
    
    if not runs:
        print(f"❌ Run {taskflow_run_id} not found in IICS_CDI_RUN_INFO")
        return False
    
    run_data = runs[0]
    original_status = run_data['status']
    run_start_time = datetime.strptime(run_data['run_start_time_mst'], '%Y-%m-%d %H:%M:%S')
    
    # Get completion time from database (latest subtask update time)
    completion_datetime = None
    if run_data.get('completion_time_mst'):
        try:
            completion_datetime = datetime.strptime(run_data['completion_time_mst'], '%Y-%m-%d %H:%M:%S')
            print(f"📅 Completion time from database: {completion_datetime.strftime('%Y-%m-%d %I:%M %p MST')}")
        except (ValueError, TypeError):
            print(f"⚠️  Could not parse completion time from database")
    
    # Check if recovery already exists
    existing = ERPRunRecovery.objects.filter(taskflow_run_id=taskflow_run_id).first()
    
    if existing:
        print(f"⚠️  Recovery record already exists for run {taskflow_run_id}")
        print(f"   Current status: {existing.original_status} → {existing.final_status}")
        print(f"   Recovered by: {existing.recovered_by}")
        
        update = input("\nUpdate existing record? (y/n): ")
        if update.lower() != 'y':
            print("Cancelled.")
            return False
        
        existing.recovered_by = recovered_by
        existing.recovery_notes = notes
        existing.final_status = final_status
        if completion_datetime:
            existing.completion_time = completion_datetime
        existing.save()
        
        print(f"✅ Updated recovery record for run {taskflow_run_id}")
        return True
    
    # Create new recovery record
    recovery = ERPRunRecovery.objects.create(
        taskflow_run_id=taskflow_run_id,
        run_start_time=run_start_time,
        completion_time=completion_datetime,
        original_status=original_status,
        recovered_by=recovered_by,
        recovery_notes=notes,
        final_status=final_status,
        is_active=True
    )
    
    print(f"✅ Created recovery record:")
    print(f"   Run ID: {taskflow_run_id}")
    print(f"   Start Time: {run_start_time.strftime('%Y-%m-%d %I:%M %p')}")
    if completion_datetime:
        print(f"   Completion Time: {completion_datetime.strftime('%Y-%m-%d %I:%M %p')}")
    else:
        print(f"   Completion Time: Not available (still running or no subtasks completed)")
    print(f"   Status: {original_status} → {final_status}")
    print(f"   Recovered by: {recovered_by}")
    print(f"   Notes: {notes}")
    
    return True


def list_suspended_runs():
    """
    List recent suspended runs that might need recovery marking
    """
    query = """
    SELECT 
        TASKFLOW_RUN_ID,
        TO_CHAR(
            FROM_TZ(CAST(START_TIME AS TIMESTAMP), 'UTC')
            AT TIME ZONE 'America/Denver',
            'DD-MON-YYYY HH12:MI AM'
        ) AS run_time_mst,
        STATUS,
        (SELECT COUNT(*) 
         FROM MAPDQPRD.IICS_CDI_RUN_INFO sub
         WHERE sub.TASKFLOW_RUN_ID = main.TASKFLOW_RUN_ID
         AND sub.SUBTASK_ASSET_NAME IS NOT NULL
         AND sub.STATUS = 'CHILD_SUSPENDED') as suspended_count
    FROM MAPDQPRD.IICS_CDI_RUN_INFO main
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND START_TIME >= SYSDATE - 7
    AND STATUS IN ('CHILD_SUSPENDED', 'SUSPENDED', 'FAILED')
    ORDER BY START_TIME DESC
    """
    
    runs = fetch_all_mapdqprd(query)
    
    if not runs:
        print("No suspended/failed runs found in the last 7 days")
        return
    
    print("\n" + "=" * 100)
    print("SUSPENDED/FAILED RUNS (Last 7 Days)")
    print("=" * 100)
    print(f"\n{'Run Time':<25} {'Status':<20} {'TASKFLOW_RUN_ID':<30} {'Suspended Jobs':<15}")
    print("-" * 100)
    
    for run in runs:
        print(f"{run['run_time_mst']:<25} {run['status']:<20} {run['taskflow_run_id']:<30} {run['suspended_count']:<15}")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - list suspended runs
        print("ERP Run Recovery Marker")
        print("=" * 100)
        list_suspended_runs()
        print("\nTo mark a run as recovered, use:")
        print("  python mark_run_recovered.py <TASKFLOW_RUN_ID> <your_email> <notes>")
        print("\nExample:")
        print('  python mark_run_recovered.py 1215720696580263936 "john@example.com" "Manually resumed all tasks"')
        print("\nNote: Completion time is automatically fetched from database")
        
    elif len(sys.argv) < 4:
        print("Usage: python mark_run_recovered.py <TASKFLOW_RUN_ID> <recovered_by> <notes> [final_status]")
        print("\nExample:")
        print('  python mark_run_recovered.py 1215720696580263936 "john@example.com" "Manually resumed" SUCCESS')
        print('\nNote: Completion time is automatically fetched from database (latest subtask completion)')
        sys.exit(1)
    
    else:
        taskflow_run_id = sys.argv[1]
        recovered_by = sys.argv[2]
        notes = sys.argv[3]
        final_status = sys.argv[4] if len(sys.argv) > 4 else 'SUCCESS'
        
        success = mark_run_as_recovered(taskflow_run_id, recovered_by, notes, final_status)
        
        if success:
            print("\n✅ Recovery marked successfully!")
            print("   Refresh the ERP dashboard to see the updated status.")
        else:
            print("\n❌ Failed to mark recovery")
            sys.exit(1)
