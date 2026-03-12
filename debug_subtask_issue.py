#!/usr/bin/env python
"""
Debug script to check what subtask data is being returned
"""
import os
import sys
import django

# Add the monitorportal directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_current_run_details
from portal.erp_mdm_insights import get_erp_run_history

print("=" * 80)
print("ERP DATA DEBUG")
print("=" * 80)

# Get raw current run data
print("\n1. RAW DATABASE RESULTS:")
print("-" * 80)
raw_results = get_erp_current_run_details()
if raw_results:
    print(f"Total jobs: {len(raw_results)}")
    print(f"\nFirst job keys: {list(raw_results[0].keys())}")
    print(f"\nFirst 3 jobs:")
    for i, job in enumerate(raw_results[:3]):
        print(f"\nJob {i+1}:")
        for key, value in job.items():
            print(f"  {key}: {value}")
else:
    print("No data returned!")

# Get processed ERP run history
print("\n\n2. PROCESSED ERP RUN HISTORY:")
print("-" * 80)
erp_data = get_erp_run_history()

if erp_data.get('success'):
    current_run = erp_data.get('current_run', {})
    jobs_list = current_run.get('jobs', [])
    
    print(f"Success: {erp_data.get('success')}")
    print(f"Current run total jobs: {current_run.get('total_jobs')}")
    print(f"Jobs in current_run['jobs']: {len(jobs_list)}")
    
    if jobs_list:
        print(f"\nFirst job keys: {list(jobs_list[0].keys())}")
        print(f"\nFirst 3 jobs:")
        for i, job in enumerate(jobs_list[:3]):
            print(f"\nJob {i+1}:")
            for key, value in job.items():
                print(f"  {key}: {value}")
else:
    print(f"Error: {erp_data.get('message')}")

print("\n" + "=" * 80)
