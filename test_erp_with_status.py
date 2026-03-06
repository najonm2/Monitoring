import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'

import django
django.setup()

from portal.erp_mdm_insights import get_erp_run_history

print("\n" + "="*80)
print("  ERP RUN HISTORY - COMPLETE DATA TEST (WITH run_status)")
print("="*80)

data = get_erp_run_history()

if data.get('success'):
    runs = data.get('last_8_runs', [])
    print(f"\n✅ Success! Retrieved {len(runs)} runs")
    
    print("\n" + "-"*80)
    print("LAST 8 RUNS - STATUS VERIFICATION:")
    print("-"*80)
    
    for i, run in enumerate(runs, 1):
        status = run.get('run_status', 'MISSING!')
        status_icon = {
            'RUNNING': '🟡',
            'SUCCESS': '✅',
            'SUSPENDED': '⏸️',
            'FAILED': '❌',
            'UNKNOWN': '❓'
        }.get(status, '❓')
        
        print(f"\n#{i}: {run.get('run_label', 'N/A')}")
        print(f"    Total Jobs: {run.get('total_jobs', 0)}")
        print(f"    Succeeded: {run.get('succeeded', 0)}")
        print(f"    Running: {run.get('running', 0)}")
        print(f"    Failed: {run.get('failed', 0)}")
        print(f"    Suspended: {run.get('suspended', 0)}")
        print(f"    Success Rate: {run.get('success_rate', 0)}%")
        print(f"    >>> STATUS: {status_icon} {status} <<<")
        
        if status == 'MISSING!':
            print("    ⚠️  ERROR: run_status field is MISSING!")
    
    print("\n" + "="*80)
    print("✅ TEST RESULT:")
    
    has_status_field = all(run.get('run_status') is not None for run in runs)
    if has_status_field:
        print("   ✅ All runs have run_status field!")
        print("   ✅ Template will display statuses correctly!")
    else:
        print("   ❌ Some runs are missing run_status field!")
        print("   ❌ Template will NOT display statuses!")
    
    print("="*80)
else:
    print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
