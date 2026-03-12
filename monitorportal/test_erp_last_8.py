#!/usr/bin/env python
"""Test the actual last 8 runs query"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portal'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.services.level3_service import get_erp_last_8_runs

print("=" * 80)
print("TESTING: get_erp_last_8_runs()")
print("=" * 80)
print()

try:
    runs = get_erp_last_8_runs()
    
    if runs:
        print(f"✅ Found {len(runs)} runs")
        print()
        for idx, run in enumerate(runs, 1):
            print(f"Run {idx}:")
            print(f"   Label: {run.get('run_label')}")
            print(f"   Start (MST): {run.get('start_time_mst')}")
            print(f"   Status: {run.get('run_status')}")
            print(f"   Jobs: {run.get('total_jobs')} (✓{run.get('succeeded')} ✗{run.get('failed')} ▶{run.get('running')})")
            print()
    else:
        print("❌ NO RUNS RETURNED!")
        print()
        print("This means the query is filtering out all runs.")
        print("Possible causes:")
        print("   1. All runs are marked as 'abandoned' (all CHILD_SUSPENDED)")
        print("   2. No matching TASKFLOW_RUN_IDs found")
        print("   3. Date filter too restrictive")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)
