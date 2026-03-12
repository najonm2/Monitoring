"""
Test ERP Last 8 Runs Query - Fixed Version
Tests the updated query that handles recovery scenarios
"""

import sys
import os

# Add the monitorportal directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.services.level3_service import get_erp_last_8_runs

def test_erp_runs():
    """Test the fixed ERP runs query"""
    print("=" * 80)
    print("TESTING ERP LAST 8 RUNS - FIXED VERSION")
    print("=" * 80)
    print()
    
    runs = get_erp_last_8_runs()
    
    if not runs:
        print("❌ No runs found!")
        return
    
    print(f"✅ Found {len(runs)} runs\n")
    
    # Print header
    print(f"{'#':<3} {'RUN TIME':<20} {'END TIME':<20} {'TOTAL':<7} {'✅ SUCC':<7} {'⏱️ RUN':<7} {'❌ FAIL':<7} {'⏸️ SUSP':<7} {'RATE':<8} {'STATUS':<12}")
    print("-" * 120)
    
    # Print each run
    for idx, run in enumerate(runs, 1):
        run_label = run.get('run_label', 'N/A')[:18]
        end_time = run.get('end_time_mst', 'N/A')[:18] if run.get('end_time_mst') else 'N/A'
        total = run.get('total_jobs', 'None')
        succeeded = run.get('succeeded', 'None')
        running = run.get('running', 'None')
        failed = run.get('failed', 'None')
        suspended = run.get('suspended', 'None')
        rate = f"{run.get('success_rate', 0)}%" if run.get('success_rate') is not None else 'N/A'
        status = run.get('run_status', 'UNKNOWN')
        
        # Color code based on status
        status_display = status
        if status == 'SUCCESS':
            status_display = f"✅ {status}"
        elif status == 'FAILED':
            status_display = f"❌ {status}"
        elif status == 'RUNNING':
            status_display = f"⏱️ {status}"
        elif status == 'SUSPENDED':
            status_display = f"⏸️ {status}"
        
        badge = "LATEST" if idx == 1 else str(idx)
        
        print(f"{badge:<3} {run_label:<20} {end_time:<20} {total!s:<7} {succeeded!s:<7} {running!s:<7} {failed!s:<7} {suspended!s:<7} {rate:<8} {status_display:<12}")
    
    print()
    print("=" * 80)
    print("VALIDATION CHECKS:")
    print("=" * 80)
    
    # Check for issues
    issues_found = False
    
    # Check if old runs showing as RUNNING
    completed_runs = [r for r in runs if r.get('end_time_mst') and r.get('end_time_mst') != 'N/A']
    running_with_end = [r for r in completed_runs if r.get('run_status') == 'RUNNING']
    if running_with_end:
        issues_found = True
        print(f"❌ Found {len(running_with_end)} completed runs showing as RUNNING (should be SUCCESS/FAILED)")
        for r in running_with_end:
            print(f"   - {r.get('run_label')}: End time={r.get('end_time_mst')}, Status={r.get('run_status')}")
    
    # Check for None job counts
    none_counts = [r for r in runs if r.get('total_jobs') is None]
    if none_counts:
        issues_found = True
        print(f"❌ Found {len(none_counts)} runs with None job counts")
        for r in none_counts:
            print(f"   - {r.get('run_label')}: Status={r.get('run_status')}")
    
    # Check for successful runs with proper counts
    success_runs = [r for r in runs if r.get('run_status') == 'SUCCESS']
    if success_runs:
        print(f"\n✅ Found {len(success_runs)} SUCCESS runs:")
        for r in success_runs:
            total = r.get('total_jobs', 0)
            succeeded = r.get('succeeded', 0)
            print(f"   - {r.get('run_label')}: {succeeded}/{total} jobs succeeded ({r.get('success_rate')}%)")
    
    if not issues_found:
        print("\n✅ All validation checks passed!")
    else:
        print("\n❌ Issues found - query needs further adjustment")

if __name__ == '__main__':
    test_erp_runs()
