"""
Verify LAST 8 RUNS STATUS - AI INSIGHTS data
Cross-check to ensure all data is showing correctly
"""
import os
import sys
import json

# Setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'
import django
django.setup()

from portal.erp_mdm_insights import get_erp_run_history
from portal.services.level3_service import get_erp_last_8_runs, get_erp_current_run_details

def check_last_8_runs():
    """Check raw data from get_erp_last_8_runs"""
    print("\n" + "="*80)
    print("1. CHECKING RAW LAST 8 RUNS DATA")
    print("="*80)
    
    runs = get_erp_last_8_runs()
    
    if not runs:
        print("❌ ERROR: No runs returned from get_erp_last_8_runs()")
        return
    
    print(f"\n✅ Total runs fetched: {len(runs)}")
    
    for idx, run in enumerate(runs, 1):
        print(f"\n--- Run #{idx} ---")
        print(f"Run Label:        {run.get('run_label', 'N/A')}")
        print(f"Taskflow Run ID:  {run.get('taskflow_run_id', 'N/A')}")
        print(f"Start Time (MST): {run.get('start_time_mst', 'N/A')}")
        print(f"End Time (MST):   {run.get('end_time_mst', 'N/A')}")
        print(f"Duration (mins):  {run.get('duration_minutes', 'N/A')}")
        print(f"Total Jobs:       {run.get('total_jobs', 0)}")
        print(f"  ✅ Succeeded:   {run.get('succeeded', 0)}")
        print(f"  ⏱️  Running:    {run.get('running', 0)}")
        print(f"  ❌ Failed:     {run.get('failed', 0)}")
        print(f"  ⏸️  Suspended:  {run.get('suspended', 0)}")
        print(f"Success Rate:     {run.get('success_rate', 0)}%")
        print(f"Run Status:       {run.get('run_status', 'UNKNOWN')}")
        print(f"SLA Minutes:      {run.get('sla_minutes', 240)}")
        print(f"Latest Success:   {run.get('latest_success_end_time', 'N/A')}")

def verify_job_counts():
    """Verify that job counts add up correctly"""
    print("\n" + "="*80)
    print("2. VERIFYING JOB COUNT TOTALS")
    print("="*80)
    
    runs = get_erp_last_8_runs()
    
    errors = []
    for idx, run in enumerate(runs, 1):
        total = run.get('total_jobs', 0)
        succeeded = run.get('succeeded', 0)
        running = run.get('running', 0)
        failed = run.get('failed', 0)
        suspended = run.get('suspended', 0)
        
        counted = succeeded + running + failed + suspended
        
        print(f"\nRun #{idx}: {run.get('run_label', 'N/A')}")
        print(f"  Total Jobs:  {total}")
        print(f"  Counted:     {counted} (✅{succeeded} + ⏱️{running} + ❌{failed} + ⏸️{suspended})")
        
        if total != counted:
            print(f"  ❌ MISMATCH: Expected {total}, but counted {counted}")
            errors.append(f"Run #{idx}: Total {total} != Counted {counted}")
        else:
            print(f"  ✅ MATCH: All jobs accounted for")
    
    if errors:
        print("\n❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ All job counts verified correctly!")

def check_current_run():
    """Check current run details"""
    print("\n" + "="*80)
    print("3. CHECKING CURRENT RUN DETAILS")
    print("="*80)
    
    jobs = get_erp_current_run_details()
    
    if not jobs:
        print("⚠️  No current run jobs found")
        return
    
    print(f"\n✅ Current run jobs fetched: {len(jobs)}")
    
    success_count = 0
    failed_count = 0
    running_count = 0
    suspended_count = 0
    
    for job in jobs:
        status = str(job.get('status', 'UNKNOWN')).upper()
        if status == 'SUCCESS':
            success_count += 1
        elif status == 'FAILED':
            failed_count += 1
        elif status == 'RUNNING':
            running_count += 1
        elif status in ['SUSPENDED', 'CHILD_SUSPENDED']:
            suspended_count += 1
    
    print(f"\nCurrent Run Summary:")
    print(f"  ✅ Succeeded:   {success_count}")
    print(f"  ⏱️  Running:    {running_count}")
    print(f"  ❌ Failed:     {failed_count}")
    print(f"  ⏸️  Suspended:  {suspended_count}")
    print(f"  Total:         {len(jobs)}")
    
    if failed_count > 0:
        print(f"\n⚠️  Failed Jobs Detected ({failed_count}):")
        for job in jobs:
            if str(job.get('status', '')).upper() == 'FAILED':
                print(f"  - {job.get('asset_name', 'N/A')}")

def check_full_insights():
    """Check the complete AI insights"""
    print("\n" + "="*80)
    print("4. CHECKING FULL AI INSIGHTS DATA")
    print("="*80)
    
    data = get_erp_run_history()
    
    if not data.get('success'):
        print(f"❌ ERROR: {data.get('message', 'Unknown error')}")
        return
    
    print("\n✅ AI Insights Data Successfully Retrieved")
    
    # Check last 8 runs
    last_8 = data.get('last_8_runs', [])
    print(f"\nLast 8 Runs: {len(last_8)} runs")
    
    for idx, run in enumerate(last_8[:3], 1):  # Show first 3
        print(f"\n  Run #{idx}: {run.get('run_label', 'N/A')}")
        print(f"    Status:       {run.get('run_status', 'UNKNOWN')}")
        print(f"    Recovered:    {'Yes' if run.get('is_recovered') else 'No'}")
        print(f"    SLA Status:   {run.get('sla_status', 'UNKNOWN')}")
        if run.get('sla_met_by') is not None:
            print(f"    SLA Met By:   {run.get('sla_met_by')} mins")
    
    # Check current run
    current = data.get('current_run', {})
    print(f"\n\nCurrent Run Details:")
    print(f"  Total Jobs:     {current.get('total_jobs', 0)}")
    print(f"  Completed:      {current.get('completed', 0)}")
    print(f"  Running:        {current.get('running', 0)}")
    print(f"  Failed:         {current.get('failed', 0)}")
    print(f"  Suspended:      {current.get('suspended', 0)}")
    print(f"  Success Rate:   {current.get('success_rate', 0)}%")
    
    # Check long running sessions
    long_running = data.get('long_running_sessions', [])
    print(f"\n\nLong Running Sessions: {len(long_running)}")
    if long_running:
        for idx, session in enumerate(long_running[:3], 1):
            print(f"  {idx}. {session.get('asset_name', 'N/A')} - {session.get('duration_minutes', 'N/A')} mins")

def main():
    print("\n" + "="*80)
    print("VERIFYING LAST 8 RUNS STATUS - AI INSIGHTS")
    print("="*80)
    print(f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        check_last_8_runs()
        verify_job_counts()
        check_current_run()
        check_full_insights()
        
        print("\n" + "="*80)
        print("✅ VERIFICATION COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
