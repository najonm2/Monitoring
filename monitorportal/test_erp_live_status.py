"""
Test ERP status query against live IDMC data
IDMC shows at 8:37 AM PST (9:37 AM MST):
- 10 jobs completed (Success)
- 2 jobs still running
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_last_8_runs

print("\n" + "="*60)
print("  🔍 TESTING ERP STATUS - LIVE COMPARISON")
print("="*60)

print("\n📊 IDMC Data (8:37 AM PST / 9:37 AM MST):")
print("   ✅ Success: 10 jobs")
print("   ⏱️ Running: 2 jobs")
print("   📝 Total: 12 jobs in 08:00 AM run")

print("\n🔍 Querying Portal Database...")
try:
    runs = get_erp_last_8_runs()
    
    if runs and len(runs) > 0:
        latest_run = runs[0]  # First run is the latest
        
        print("\n" + "="*60)
        print("  📈 LATEST RUN - PORTAL DATA")
        print("="*60)
        
        print(f"\n🕐 Run Time: {latest_run.get('run_label', 'Unknown')}")
        print(f"   Start: {latest_run.get('start_time_mst', 'N/A')}")
        print(f"   End: {latest_run.get('end_time_mst', 'N/A')}")
        
        total = latest_run.get('total_jobs', 0)
        succeeded = latest_run.get('succeeded', 0)
        running = latest_run.get('running', 0)
        failed = latest_run.get('failed', 0)
        suspended = latest_run.get('suspended', 0)
        status = latest_run.get('run_status', 'UNKNOWN')
        
        print(f"\n📊 Job Counts:")
        print(f"   Total Jobs: {total}")
        print(f"   ✅ Succeeded: {succeeded}")
        print(f"   ⏱️ Running: {running}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏸️ Suspended: {suspended}")
        print(f"\n🎯 Run Status: {status}")
        
        print("\n" + "="*60)
        print("  🔍 COMPARISON")
        print("="*60)
        
        print("\n📋 IDMC vs Portal:")
        print(f"   Total Jobs:")
        print(f"      IDMC: 12 jobs")
        print(f"      Portal: {total} jobs")
        if total == 12:
            print(f"      ✅ MATCH")
        else:
            print(f"      ❌ MISMATCH - Portal count incorrect")
        
        print(f"\n   Success Count:")
        print(f"      IDMC: 10 jobs")
        print(f"      Portal: {succeeded} jobs")
        if succeeded == 10:
            print(f"      ✅ MATCH")
        else:
            print(f"      ⚠️ DIFFERENCE - Portal shows {succeeded}, IDMC shows 10")
        
        print(f"\n   Running Count:")
        print(f"      IDMC: 2 jobs")
        print(f"      Portal: {running} jobs")
        if running == 2:
            print(f"      ✅ MATCH")
        else:
            print(f"      ⚠️ DIFFERENCE - Portal shows {running}, IDMC shows 2")
        
        print(f"\n   Overall Status:")
        print(f"      Portal: {status}")
        if running > 0:
            expected_status = "RUNNING"
        elif failed > 0:
            expected_status = "FAILED"
        elif suspended > 0:
            expected_status = "SUSPENDED"
        else:
            expected_status = "SUCCESS"
        
        print(f"      Expected: {expected_status} (because {running} jobs running)")
        if status == expected_status:
            print(f"      ✅ CORRECT")
        else:
            print(f"      ❌ INCORRECT - Should be {expected_status}")
        
        print("\n" + "="*60)
        print("  🔎 ROOT CAUSE ANALYSIS")
        print("="*60)
        
        if total != 12:
            print("\n❌ Issue 1: Total job count mismatch")
            print("   Possible causes:")
            print("   - Query not capturing all jobs in this run")
            print("   - TASKFLOW_RUN_ID grouping issue")
            print("   - Time range filter too narrow")
        
        if succeeded != 10 or running != 2:
            print("\n❌ Issue 2: Job status counts don't match IDMC")
            print("   Possible causes:")
            print("   - Cache showing old data (2-minute TTL)")
            print("   - Query not getting latest job status")
            print("   - Status mapping incorrect")
            print("\n💡 RECOMMENDATION:")
            print("   Clear cache and verify query is getting LATEST status per job")
        
        if status != expected_status:
            print("\n❌ Issue 3: Overall run status incorrect")
            print("   Status calculation logic may need review")
        
    else:
        print("\n❌ No data returned from query!")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("  ✅ TEST COMPLETE")
print("="*60)
print()
