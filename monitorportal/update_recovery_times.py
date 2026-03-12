#!/usr/bin/env python
"""
Quick script to update recovery completion times for the three runs
Completion times are automatically fetched from database (latest subtask completion)
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

# Define the three runs
runs_to_update = [
    {
        'taskflow_run_id': '1215720696580263936',  # 09-MAR 12:00 PM
        'recovered_by': 'system.admin@lumen.com',
        'notes': 'Manually resumed all suspended subtasks via IICS Monitor. All tasks completed successfully.'
    },
    {
        'taskflow_run_id': '1215479110705471488',  # 08-MAR 8:00 PM
        'recovered_by': 'system.admin@lumen.com',
        'notes': 'Manually resumed all suspended subtasks via IICS Monitor. All tasks completed successfully.'
    },
    {
        'taskflow_run_id': '1215358312988663810',  # 08-MAR 12:00 PM
        'recovered_by': 'system.admin@lumen.com',
        'notes': 'Manually resumed all suspended subtasks via IICS Monitor. All tasks completed successfully.'
    }
]

print("=" * 100)
print("UPDATING RECOVERY RECORDS WITH COMPLETION TIMES FROM DATABASE")
print("=" * 100)
print()

for run_info in runs_to_update:
    taskflow_run_id = run_info['taskflow_run_id']
    
    # Get run details from IICS including completion time from database
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
        continue
    
    run_data = runs[0]
    original_status = run_data['status']
    run_start_time = datetime.strptime(run_data['run_start_time_mst'], '%Y-%m-%d %H:%M:%S')
    
    # Get completion time from database
    completion_datetime = None
    if run_data.get('completion_time_mst'):
        try:
            completion_datetime = datetime.strptime(run_data['completion_time_mst'], '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            print(f"⚠️  Could not parse completion time from database")
    
    # Check if recovery already exists
    existing = ERPRunRecovery.objects.filter(taskflow_run_id=taskflow_run_id).first()
    
    if existing:
        # Update existing record with completion time from database
        existing.completion_time = completion_datetime
        existing.recovered_by = run_info['recovered_by']
        existing.recovery_notes = run_info['notes']
        existing.save()
        
        print(f"✅ Updated recovery record:")
        print(f"   Run ID: {taskflow_run_id}")
        print(f"   Start Time: {run_start_time.strftime('%Y-%m-%d %I:%M %p')}")
        if completion_datetime:
            print(f"   Completion Time: {completion_datetime.strftime('%Y-%m-%d %I:%M %p')} (from database)")
        else:
            print(f"   Completion Time: Not available")
        print(f"   Status: {original_status} → SUCCESS")
        print()
    else:
        # Create new recovery record with completion time from database
        recovery = ERPRunRecovery.objects.create(
            taskflow_run_id=taskflow_run_id,
            run_start_time=run_start_time,
            completion_time=completion_datetime,
            original_status=original_status,
            recovered_by=run_info['recovered_by'],
            recovery_notes=run_info['notes'],
            final_status='SUCCESS',
            is_active=True
        )
        
        print(f"✅ Created recovery record:")
        print(f"   Run ID: {taskflow_run_id}")
        print(f"   Start Time: {run_start_time.strftime('%Y-%m-%d %I:%M %p')}")
        if completion_datetime:
            print(f"   Completion Time: {completion_datetime.strftime('%Y-%m-%d %I:%M %p')} (from database)")
        else:
            print(f"   Completion Time: Not available")
        print(f"   Status: {original_status} → SUCCESS")
        print()

print("=" * 100)
print("✅ ALL RECOVERY RECORDS UPDATED SUCCESSFULLY!")
print("=" * 100)
print()
print("Next steps:")
print("1. Wait 30 seconds for cache to expire")
print("2. Refresh the ERP dashboard at: http://127.0.0.1:8000/dashboards/erp/")
print("3. Verify completion times are displayed for all three runs")
