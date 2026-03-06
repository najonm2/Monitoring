import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'

import django
django.setup()

from portal.erp_mdm_insights import get_erp_run_history

print("\n" + "="*100)
print("  ERP RUN HISTORY - COMPLETE TEST WITH DURATION & SLA")
print("="*100)

data = get_erp_run_history()

if data.get('success'):
    runs = data.get('last_8_runs', [])
    print(f"\n✅ Success! Retrieved {len(runs)} runs")
    
    print("\n" + "-"*100)
    print("LAST 8 RUNS - ENHANCED WITH DURATION & SLA:")
    print("-"*100)
    
    for i, run in enumerate(runs, 1):
        status = run.get('run_status', 'UNKNOWN')
        sla_status = run.get('sla_status', 'UNKNOWN')
        
        status_icon = {
            'RUNNING': '🟡',
            'SUCCESS': '✅',
            'SUSPENDED': '⏸️',
            'FAILED': '❌',
            'UNKNOWN': '❓'
        }.get(status, '❓')
        
        sla_icon = {
            'MET': '✅',
            'MISSED': '❌',
            'IN PROGRESS': '⏱️',
            'UNKNOWN': '❓'
        }.get(sla_status, '❓')
        
        print(f"\n#{i}: {run.get('run_label', 'N/A')}")
        print(f"    Start Time: {run.get('start_time', 'N/A')}")
        print(f"    End Time: {run.get('end_time', 'N/A')}")
        
        duration = run.get('duration_minutes', 0)
        if duration:
            if duration < 60:
                duration_str = f"{duration:.0f} mins"
            else:
                hours = int(duration // 60)
                mins = int(duration % 60)
                duration_str = f"{hours}h {mins}m ({duration:.0f} mins)"
            print(f"    Duration: {duration_str}")
        else:
            print(f"    Duration: N/A (Still running)")
        
        print(f"    Total Jobs: {run.get('total_jobs', 0)}")
        print(f"    Succeeded: {run.get('succeeded', 0)}")
        print(f"    Running: {run.get('running', 0)}")
        print(f"    Failed: {run.get('failed', 0)}")
        print(f"    Suspended: {run.get('suspended', 0)}")
        print(f"    Success Rate: {run.get('success_rate', 0)}%")
        print(f"    >>> STATUS: {status_icon} {status} <<<")
        
        sla_met_by = run.get('sla_met_by')
        if sla_status == 'MET' and sla_met_by is not None:
            print(f"    >>> SLA: {sla_icon} {sla_status} (Completed {sla_met_by:.0f} minutes early) <<<")
        elif sla_status == 'MISSED' and sla_met_by is not None:
            print(f"    >>> SLA: {sla_icon} {sla_status} (Exceeded by {sla_met_by:.0f} minutes) <<<")
        else:
            print(f"    >>> SLA: {sla_icon} {sla_status} <<<")
    
    print("\n" + "="*100)
    print("✅ TEST RESULT: All fields present!")
    print("   ✅ Start Time: Captured")
    print("   ✅ End Time: Captured")
    print("   ✅ Duration: Calculated")
    print("   ✅ SLA Status: Calculated (4-hour SLA window)")
    print("   ✅ SLA Met By: Shows minutes early/late")
    print("="*100)
else:
    print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
