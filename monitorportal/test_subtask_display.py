"""
Quick test to see if get_erp_current_run_details returns subtask names
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_current_run_details

print("Getting current run details...")
jobs = get_erp_current_run_details()

print(f"\nFound {len(jobs)} jobs\n")

print("Job details (showing both asset_name and subtask_asset_name):")
print("-" * 100)
for i, job in enumerate(jobs, 1):
    asset = job.get('asset_name', 'N/A')
    subtask = job.get('subtask_asset_name', 'N/A')
    status = job.get('status', 'N/A')
    print(f"{i:2d}. Asset: {asset[:35].ljust(35)} | Subtask: {subtask[:45].ljust(45)} | {status}")

print("\nTemplate will display: {{ job.subtask_asset_name|default:job.asset_name }}")
print("\nThis means users will see the SUBTASK names (wkf_Load_DEFERRED_REV_TABLES, etc.)")
