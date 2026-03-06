"""
Quick test to verify run statuses match IDMC
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_last_8_runs

print("Getting last 8 runs to verify status...")
runs = get_erp_last_8_runs()

print(f"\nFound {len(runs)} runs\n")
print("STATUS VERIFICATION:")
print("-" * 100)
print(f"{'#':<3} {'RUN TIME':<25} {'STATUS':<12} {'JOBS':<6} {'OK':<4} {'RUN':<4} {'ERR':<4} {'SUS':<4}")
print("-" * 100)

for i, run in enumerate(runs, 1):
    run_label = run.get('run_label', 'N/A')
    status = run.get('run_status', 'UNKNOWN')
    total = run.get('total_jobs', 0)
    succeeded = run.get('succeeded', 0)
    running = run.get('running', 0)
    failed = run.get('failed', 0)
    suspended = run.get('suspended', 0)
    
    # Status indicator
    if status == 'SUCCESS':
        icon = '+'
    elif status == 'FAILED':
        icon = 'X'
    elif status == 'RUNNING':
        icon = '~'
    elif status == 'SUSPENDED':
        icon = '||'
    else:
        icon = '?'
    
    print(f"{i:<3} {run_label:<25} {icon} {status:<10} {total:<6} {succeeded:<4} {running:<4} {failed:<4} {suspended:<4}")

print("\n" + "="*100)
print("EXPECTED (from IDMC):")
print("="*100)
print("1. Mar 6, 7:00 AM   - Running   (9 tasks)")
print("2. Mar 6, 3:00 AM   - Success   (13 tasks)")
print("3. Mar 5, 11:00 PM  - Success   (13 tasks)")
print("4. Mar 5, 7:00 PM   - Success   (13 tasks)")
print("5. Mar 5, 3:00 PM   - Failed    (8 tasks)")
print("6. Mar 5, 11:00 AM  - Failed    (11 tasks)")
print("7. Mar 5, 10:43 AM  - Failed    (8 tasks)")
print("8. Mar 5, 7:00 AM   - Failed    (8 tasks)")

print("\n" + "="*100)
print("TEMPLATE FIX:")
print("="*100)
print("OLD: Used calculated logic (failed > 0, running > 0, success_rate >= 95%)")
print("     Result: Showed 'PARTIAL' for most runs")
print("\nNEW: Uses run.run_status directly from master workflow")
print("     Result: Shows actual status (SUCCESS, FAILED, RUNNING, SUSPENDED)")
