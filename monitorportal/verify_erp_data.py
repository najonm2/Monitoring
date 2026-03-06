"""
Verify ERP data against IDMC actual data
Compare what our queries return vs what IDMC shows
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_last_8_runs, get_erp_current_run_details

print("\n" + "="*80)
print("VERIFYING ERP DATA AGAINST IDMC")
print("="*80)

# IDMC Data (from user) - as reference
idmc_runs = [
    {"instance": "1214588239747346432", "start": "Mar 6, 7:00 AM PST", "tasks": 9, "status": "Running", "end": None},
    {"instance": "1214527836644302848", "start": "Mar 6, 3:00 AM PST", "tasks": 13, "status": "Success", "end": "Mar 6, 7:19 AM"},
    {"instance": "1214467438016585729", "start": "Mar 5, 11:00 PM PST", "tasks": 13, "status": "Success", "end": "Mar 6, 3:25 AM"},
    {"instance": "1214407045617410050", "start": "Mar 5, 7:00 PM PST", "tasks": 13, "status": "Success", "end": "Mar 6, 1:06 AM"},
    {"instance": "1214346642690535424", "start": "Mar 5, 3:00 PM PST", "tasks": 8, "status": "Failed", "end": "Mar 5, 3:10 PM"},
    {"instance": "1214286246306770945", "start": "Mar 5, 11:00 AM PST", "tasks": 11, "status": "Failed", "end": "Mar 5, 6:18 PM"},
    {"instance": "1214281994427551744", "start": "Mar 5, 10:43 AM PST", "tasks": 8, "status": "Failed", "end": "Mar 5, 11:11 AM"},
    {"instance": "1214225849260306432", "start": "Mar 5, 7:00 AM PST", "tasks": 8, "status": "Failed", "end": "Mar 5, 7:32 AM"},
]

print("\nIDMC Reference Data (Last 8 Runs):")
print("-" * 80)
for i, run in enumerate(idmc_runs, 1):
    print(f"{i}. {run['start']} | Tasks: {run['tasks']:2d} | Status: {run['status']:8s} | ID: {run['instance']}")

print("\n" + "="*80)
print("PORTAL QUERY RESULTS")
print("="*80)

# Get portal data
print("\n⏳ Fetching last 8 runs from database...")
last_8_runs = get_erp_last_8_runs()

print(f"\n✅ Found {len(last_8_runs)} runs\n")

if last_8_runs:
    print("Portal Last 8 Runs:")
    print("-" * 80)
    for i, run in enumerate(last_8_runs, 1):
        taskflow_id = str(run.get('taskflow_run_id', 'N/A'))
        run_label = run.get('run_label', 'N/A')
        total_jobs = run.get('total_jobs', 0)
        status = run.get('run_status', 'UNKNOWN')
        succeeded = run.get('succeeded', 0)
        running = run.get('running', 0)
        failed = run.get('failed', 0)
        suspended = run.get('suspended', 0)
        
        print(f"{i}. {run_label:25s} | Jobs: {total_jobs:2d} | Status: {status:10s} | ID: {taskflow_id}")
        print(f"   ✅:{succeeded:2d} ⏱️:{running:2d} ❌:{failed:2d} ⏸️:{suspended:2d}")

print("\n" + "="*80)
print("COMPARISON ANALYSIS")
print("="*80)

# Compare
if len(last_8_runs) >= 1:
    portal_first = last_8_runs[0]
    idmc_first = idmc_runs[0]
    
    portal_id = str(portal_first.get('taskflow_run_id', ''))
    idmc_id = idmc_first['instance']
    
    print(f"\n🔍 Latest Run Comparison:")
    print(f"  IDMC ID:   {idmc_id}")
    print(f"  Portal ID: {portal_id}")
    print(f"  Match: {'✅ YES' if portal_id == idmc_id else '❌ NO'}")
    print(f"\n  IDMC Tasks:   {idmc_first['tasks']}")
    print(f"  Portal Jobs:  {portal_first.get('total_jobs', 0)}")
    print(f"  Match: {'✅ YES' if portal_first.get('total_jobs') == idmc_first['tasks'] else '❌ NO - COUNT MISMATCH!'}")
    print(f"\n  IDMC Status:   {idmc_first['status']}")
    print(f"  Portal Status: {portal_first.get('run_status', 'N/A')}")
    print(f"  Match: {'✅ YES' if portal_first.get('run_status', '').upper() == idmc_first['status'].upper() else '❌ NO - STATUS MISMATCH!'}")

# Check current run details
print("\n" + "="*80)
print("CURRENT RUN DETAILS")
print("="*80)

print("\n⏳ Fetching current run job details...")
current_jobs = get_erp_current_run_details()

print(f"\n✅ Found {len(current_jobs)} jobs in current run\n")

if current_jobs:
    print(f"Expected from IDMC: {idmc_runs[0]['tasks']} tasks")
    print(f"Portal returns:     {len(current_jobs)} jobs")
    
    if len(current_jobs) != idmc_runs[0]['tasks']:
        print("\n⚠️  JOB COUNT MISMATCH!")
        print("\nPossible issues:")
        print("  1. Query filtering out some jobs")
        print("  2. Master workflow counted as a job")
        print("  3. Location filters too restrictive")
        print("  4. TAX filter removing jobs")
    
    print("\nSample jobs (first 5):")
    for i, job in enumerate(current_jobs[:5], 1):
        asset = job.get('asset_name', 'N/A')
        status = job.get('status', 'N/A')
        location = job.get('location', 'N/A')
        print(f"  {i}. {asset:50s} | {status:10s} | {location}")
    
    # Count unique asset names
    unique_assets = set(job.get('asset_name') for job in current_jobs)
    print(f"\n📊 Unique asset names: {len(unique_assets)}")
    if len(unique_assets) < len(current_jobs):
        print(f"⚠️  Warning: {len(current_jobs)} jobs but only {len(unique_assets)} unique assets (duplicates present)")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"""
Expected (from IDMC):
  - Latest run: {idmc_runs[0]['instance']}
  - Task count: {idmc_runs[0]['tasks']} tasks
  - Status: {idmc_runs[0]['status']}

Portal returns:
  - Latest run: {last_8_runs[0].get('taskflow_run_id') if last_8_runs else 'N/A'}
  - Job count: {last_8_runs[0].get('total_jobs') if last_8_runs else 0} jobs
  - Status: {last_8_runs[0].get('run_status') if last_8_runs else 'N/A'}

Issues to investigate:
  {'✅ Data matches!' if (last_8_runs and str(last_8_runs[0].get('taskflow_run_id')) == idmc_runs[0]['instance'] and last_8_runs[0].get('total_jobs') == idmc_runs[0]['tasks']) else '❌ Data does NOT match - need to fix query'}
""")
