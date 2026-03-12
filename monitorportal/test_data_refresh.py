"""Test MDM and Level3 data refresh"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

import time

print("=" * 60)
print("TESTING DATA REFRESH - MDM & Level3")
print("=" * 60)

# Test 1: MDM Job Status
print("\n[1] MDM Job Status")
print("-" * 40)
try:
    start = time.time()
    from portal.services.level3_service import get_mdm_job_status
    jobs = get_mdm_job_status()
    elapsed = time.time() - start
    print(f"  Returned {len(jobs)} MDM jobs in {elapsed:.2f}s")
    for j in jobs:
        status = j.get('status', 'UNKNOWN')
        name = j.get('asset_name', 'UNKNOWN')
        start_t = j.get('start_time', 'None')
        end_t = j.get('end_time', 'None')
        print(f"  {name}: {status} | Start: {start_t} | End: {end_t}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Level3 Today Stats
print("\n[2] Level3 Today Stats")
print("-" * 40)
try:
    start = time.time()
    from portal.services.level3_service import get_level3_jobs_today_only
    stats = get_level3_jobs_today_only()
    elapsed = time.time() - start
    print(f"  Fetched in {elapsed:.2f}s")
    print(f"  Total: {stats.get('total', 0)}")
    print(f"  Succeeded: {stats.get('succeeded', 0)}")
    print(f"  Failed: {stats.get('failed', 0)}")
    print(f"  Running: {stats.get('running', 0)}")
    print(f"  Stopped: {stats.get('stopped', 0)}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Level3 Failed Jobs Status
print("\n[3] Level3 Failed Jobs Status")
print("-" * 40)
try:
    start = time.time()
    from portal.services.level3_service import get_level3_failed_jobs_status
    summary, failed_jobs = get_level3_failed_jobs_status()
    elapsed = time.time() - start
    print(f"  Fetched in {elapsed:.2f}s")
    print(f"  Summary: {summary}")
    print(f"  Failed jobs count: {len(failed_jobs)}")
    if failed_jobs:
        for j in failed_jobs[:3]:
            print(f"    {j.get('workflow_name', 'N/A')}: {j.get('status', 'N/A')}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check Django cache
print("\n[4] Django Cache Status")
print("-" * 40)
try:
    from django.core.cache import cache
    mdm_cached = cache.get('mdm_job_status_data')
    level3_cached = cache.get('level3_bi_report_data')
    print(f"  MDM cache: {'HIT (cached data exists)' if mdm_cached else 'MISS (no cached data)'}")
    print(f"  Level3 BI cache: {'HIT (cached data exists)' if level3_cached else 'MISS (no cached data)'}")
    
    # Clear caches
    cache.delete('mdm_job_status_data')
    cache.delete('level3_bi_report_data')
    print("  -> Caches cleared!")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
