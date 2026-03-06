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
print("TESTING get_erp_last_8_runs() - WITH MODULE RELOAD")
print("=" * 80)
last_8 = get_erp_last_8_runs()
print(f"\nNumber of runs returned: {len(last_8)}\n")

if last_8:
    print("Run Labels (should show 4-hour windows like '06-MAR-2026 08:00'):")
    for i, run in enumerate(last_8[:8], 1):
        print(f"  {i}. {run.get('run_label')} - {run.get('total_jobs')} jobs - {run.get('success_rate')}% success")
else:
    print("NO DATA RETURNED!")

print("\n" + "=" * 80)
print("TESTING get_erp_current_run_details() - WITH MODULE RELOAD")
print("=" * 80)
current = get_erp_current_run_details()
print(f"\nNumber of jobs in current run: {len(current)}")
if current:
    print(f"Current run time (sample): {current[0].get('start_time_pst')}")
    print(f"Current run status counts:")
    statuses = {}
    for job in current:
        status = job.get('status')
        statuses[status] = statuses.get(status, 0) + 1
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")
else:
    print("NO CURRENT RUN DATA!")
