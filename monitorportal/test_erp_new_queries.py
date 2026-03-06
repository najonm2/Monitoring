import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

# Force reload the module
import importlib
from portal.services import level3_service
importlib.reload(level3_service)

from portal.services.level3_service import get_erp_last_8_runs, get_erp_current_run_details
import json

print("=" * 80)
print("TESTING NEW ERP QUERIES WITH wkf_ERP_DAILY_REFRESH_MASTER")
print("=" * 80)

print("\n1. Last 8 Runs:")
print("-" * 80)
last_8 = get_erp_last_8_runs()
print(f"Found {len(last_8)} runs\n")

if last_8:
    for i, run in enumerate(last_8, 1):
        status_icon = "+" if run.get('run_status') == 'SUCCESS' else ("~" if run.get('run_status') == 'RUNNING' else "!")
        end_time = run.get('end_time_pst') or "Still running..."
        print(f"{status_icon} {i}. {run.get('run_label')}")
        print(f"      Start: {run.get('start_time_pst')}")
        print(f"      End:   {end_time}")
        print(f"      Jobs: {run.get('total_jobs')} total | {run.get('succeeded')} succeeded | {run.get('running')} running | {run.get('failed')} failed")
        print(f"      Success Rate: {run.get('success_rate')}% | Status: {run.get('run_status')}")
        print()

print("\n2. Current Run Details:")
print("-" * 80)
current = get_erp_current_run_details()
print(f"Found {len(current)} jobs in current run\n")

if current:
    # Group by status
    status_counts = {}
    for job in current:
        status = job.get('status')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("Status Breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count} jobs")
    
    print("\nSample Jobs (first 5):")
    for i, job in enumerate(current[:5], 1):
        print(f"  {i}. {job.get('asset_name')} - {job.get('status')}")

print("\n" + "=" * 80)
print("VERIFICATION:")
print("=" * 80)
if last_8 and current:
    latest_run_id = last_8[0].get('taskflow_run_id')
    latest_label = last_8[0].get('run_label')
    latest_status = last_8[0].get('run_status')
    latest_end = last_8[0].get('end_time_pst')
    
    print(f"+ Latest run: {latest_label}")
    print(f"  TASKFLOW_RUN_ID: {latest_run_id}")
    print(f"  Status: {latest_status}")
    print(f"  End time: {latest_end if latest_end else 'NULL (still running)'}")
    print(f"  Current run jobs: {len(current)}")
    print(f"  Expected jobs in last_8: {last_8[0].get('total_jobs')}")
    
    if len(current) == last_8[0].get('total_jobs'):
        print("  > MATCH! Job counts align correctly")
    else:
        print(f"  > MISMATCH: {len(current)} current jobs != {last_8[0].get('total_jobs')} expected")
else:
    print("- No data returned")

print("=" * 80)
