#!/usr/bin/env python
"""
Check the actual database status for specific runs that user says are completed
"""
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

def print_run_summary(run_label, jobs):
    """Print summary of a run"""
    print(f"\n{'='*100}")
    print(f"RUN: {run_label}")
    print(f"{'='*100}")
    
    # Count by status
    status_counts = {}
    for job in jobs:
        status = job['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Summary line
    total = len(jobs)
    succeeded = status_counts.get('SUCCESS', 0)
    failed = status_counts.get('FAILED', 0)
    running = status_counts.get('RUNNING', 0)
    suspended = status_counts.get('CHILD_SUSPENDED', 0) + status_counts.get('SUSPENDED', 0)
    
    print(f"Total Jobs: {total}")
    print(f"Status Breakdown: ✓{succeeded} ✗{failed} ▶{running} ⏸{suspended}")
    print()
    
    # Check END_TIME
    jobs_with_end = sum(1 for j in jobs if j['has_end_time'] == 'YES')
    jobs_without_end = total - jobs_with_end
    
    print(f"Completion Status:")
    print(f"  - Jobs WITH end_time: {jobs_with_end}")
    print(f"  - Jobs WITHOUT end_time: {jobs_without_end} ⚠️")
    print()
    
    # Determine overall status
    if succeeded == total and total > 0:
        print(f"✅ RUN COMPLETED SUCCESSFULLY (all {total} jobs succeeded)")
    elif suspended > 0 and jobs_without_end > 0:
        print(f"⏸️ RUN SUSPENDED (database shows {suspended} suspended, {jobs_without_end} without end_time)")
    elif jobs_without_end > 0:
        print(f"▶️ RUN IN PROGRESS ({jobs_without_end} jobs still running)")
    else:
        print(f"⚠️ MIXED STATUS")
    
    # Sample a few jobs to show detail
    print(f"\nSample Jobs (first 3):")
    for i, job in enumerate(jobs[:3], 1):
        status_icon = "✓" if job['status'] == 'SUCCESS' else "✗" if job['status'] == 'FAILED' else "⏸" if 'SUSPENDED' in job['status'] else "▶"
        print(f"  {i}. {status_icon} {job['job_name'][:50]}")
        print(f"     Status: {job['status']}, End: {job['end_time'] or 'NONE (still running)'}")

# Check the specific runs the user mentioned
query = """
SELECT 
    TO_CHAR(START_TIME, 'DD-MON-YYYY HH12:MI AM') as start_label,
    TASKFLOW_RUN_ID,
    COALESCE(SUBTASK_ASSET_NAME, ASSET_NAME) as job_name,
    STATUS,
    TO_CHAR(START_TIME, 'DD-MON HH24:MI:SS') as start_time,
    TO_CHAR(END_TIME, 'DD-MON HH24:MI:SS') as end_time,
    CASE WHEN END_TIME IS NULL THEN 'NO' ELSE 'YES' END as has_end_time
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= TO_DATE('08-MAR-2026 12:00:00', 'DD-MON-YYYY HH24:MI:SS')
AND START_TIME <= TO_DATE('09-MAR-2026 12:30:00', 'DD-MON-YYYY HH24:MI:SS')
ORDER BY START_TIME DESC, job_name
"""

print("=" * 100)
print("CHECKING DATABASE STATUS FOR USER-REPORTED COMPLETED RUNS")
print("=" * 100)
print()
print("User says these are COMPLETED:")
print("  - 09-MAR-2026 12:00 PM")
print("  - 08-MAR-2026 08:00 PM")
print("  - 08-MAR-2026 12:00 PM")
print()
print("Checking actual database records...")
print("=" * 100)
print()

results = fetch_all_mapdqprd(query)

if not results:
    print("❌ No records found")
    sys.exit(1)

current_run = None
run_jobs = []

for row in results:
    if current_run != row['start_label']:
        # Print previous run summary
        if run_jobs:
            print_run_summary(current_run, run_jobs)
        
        current_run = row['start_label']
        run_jobs = [row]
    else:
        run_jobs.append(row)

# Print last run
if run_jobs:
    print_run_summary(current_run, run_jobs)

print("\n" + "=" * 100)
print("DIAGNOSIS:")
print("=" * 100)
print()
print("If runs show SUSPENDED with no END_TIME but user says they completed:")
print("  1. Check if you're looking at the correct IICS environment")
print("  2. Verify the runs actually completed in IICS Monitor")
print("  3. Check for database replication lag")
print("  4. Confirm TASKFLOW_RUN_ID matches between IICS and database")
print()
