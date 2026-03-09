import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'

import django
django.setup()

from portal.services.level3_service import get_level3_folders_with_metrics

print("\n" + "="*80)
print("  TESTING: get_level3_folders_with_metrics()")
print("="*80)

folders = get_level3_folders_with_metrics()

print(f"\nFound {len(folders)} folders")
print("\nFirst 5 folders:")
print("-"*80)

for i, folder in enumerate(folders[:5], 1):
    print(f"\n#{i}:")
    print(f"  Keys: {list(folder.keys())}")
    print(f"  subject_area: {folder.get('subject_area', 'MISSING!')}")
    print(f"  job_count: {folder.get('job_count', 0)}")
    print(f"  failed_count: {folder.get('failed_count', 0)}")
    print(f"  success_count: {folder.get('success_count', 0)}")
    print(f"  running_count: {folder.get('running_count', 0)}")
    
    # Check if subject_area looks like a date
    sa = str(folder.get('subject_area', ''))
    if '-' in sa or '/' in sa:
        print(f"  ⚠️  WARNING: subject_area looks like a date: {sa}")

print("\n" + "="*80)
print("✅ Test Complete")
print("="*80)
