import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'

import django
django.setup()

from portal.services.level3_service import get_erp_last_8_runs

print("\n" + "="*60)
print("  ERP LAST 8 RUNS - STATUS DEBUG")
print("="*60)

runs = get_erp_last_8_runs()

if runs:
    print(f"\nTotal runs returned: {len(runs)}")
    print("\nDetailed Analysis:")
    print("-" * 120)
    
    for i, run in enumerate(runs, 1):
        print(f"\nRun #{i}: {run.get('run_label', 'N/A')}")
        print(f"  TASKFLOW_RUN_ID: {run.get('taskflow_run_id', 'N/A')}")
        print(f"  Total Jobs: {run.get('total_jobs', 'N/A')}")
        print(f"  Succeeded: {run.get('succeeded', 'N/A')}")
        print(f"  Running: {run.get('running', 'N/A')}")
        print(f"  Failed: {run.get('failed', 'N/A')}")
        print(f"  Suspended: {run.get('suspended', 'N/A')}")
        print(f"  Success Rate: {run.get('success_rate', 'N/A')}%")
        print(f"  >>> STATUS: {run.get('run_status', 'N/A')} <<<")
        
        # Debug: Check for None/NULL values
        if run.get('total_jobs') is None:
            print(f"  ⚠️  WARNING: total_jobs is None!")
        if run.get('succeeded') is None:
            print(f"  ⚠️  WARNING: succeeded is None!")
        if run.get('running') is None:
            print(f"  ⚠️  WARNING: running is None!")
        if run.get('failed') is None:
            print(f"  ⚠️  WARNING: failed is None!")
        if run.get('suspended') is None:
            print(f"  ⚠️  WARNING: suspended is None!")
else:
    print("\n❌ No runs returned!")

print("\n" + "="*60)
