import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_last_8_runs, get_erp_current_run_details
import json

print("=" * 80)
print("TESTING get_erp_last_8_runs()")
print("=" * 80)
last_8 = get_erp_last_8_runs()
print(f"Number of runs returned: {len(last_8)}")
print(json.dumps(last_8, indent=2, default=str))

print("\n" + "=" * 80)
print("TESTING get_erp_current_run_details()")
print("=" * 80)
current = get_erp_current_run_details()
print(f"Number of jobs in current run: {len(current)}")
if current:
    print("First 5 jobs:")
    print(json.dumps(current[:5], indent=2, default=str))
else:
    print("No current run data found!")
