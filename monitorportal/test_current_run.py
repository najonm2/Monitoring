"""
Test ERP Current Run Query
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.level3_service import get_erp_current_run_details

print("\n" + "="*60)
print("  TESTING: ERP Current Run Details Query")
print("="*60)

try:
    jobs = get_erp_current_run_details()
    
    if jobs:
        print(f"\n✅ Success! Retrieved {len(jobs)} jobs from current run\n")
        
        # Show first 3 jobs with details
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{'='*50}")
            print(f"Job #{i}: {job.get('asset_name', 'N/A')}")
            print(f"{'='*50}")
            print(f"  Subtasks: {job.get('subtask_count', 0)}")
            print(f"  Start: {job.get('start_time_mst', 'N/A')}")
            print(f"  End: {job.get('end_time_mst', 'N/A')}")
            print(f"  Duration: {job.get('duration_minutes', 0):.1f} minutes")
            print(f"  Status: {job.get('status', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            
            status = job.get('status', '').upper()
            if status == 'RUNNING':
                print(f"  ⏱️  RUNNING - Duration so far: {job.get('duration_minutes', 0):.1f} mins")
            elif status == 'SUCCESS':
                print(f"  ✅ SUCCESS")
            elif status == 'FAILED':
                print(f"  ❌ FAILED")
        
        # Count by status
        running = sum(1 for j in jobs if j.get('status', '').upper() == 'RUNNING')
        success = sum(1 for j in jobs if j.get('status', '').upper() == 'SUCCESS')
        failed = sum(1 for j in jobs if j.get('status', '').upper() == 'FAILED')
        suspended = sum(1 for j in jobs if j.get('status', '').upper() in ['SUSPENDED', 'CHILD_SUSPENDED'])
        
        print(f"\n{'='*50}")
        print("STATUS SUMMARY:")
        print(f"{'='*50}")
        print(f"  Total Jobs: {len(jobs)}")
        print(f"  🟢 SUCCESS: {success}")
        print(f"  🟡 RUNNING: {running}")
        print(f"  🔴 FAILED: {failed}")
        print(f"  ⏸️  SUSPENDED: {suspended}")
        
    else:
        print("\n⚠️  No jobs found in current run")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
