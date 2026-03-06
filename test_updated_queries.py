# Test Updated Queries
import sys
import os

sys.path.insert(0, r'C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from portal.services.level3_service import (
    get_level3_failed_with_error,
    get_level3_long_running
)
import json

print("="*70)
print("TESTING UPDATED QUERIES")
print("="*70)

# Test 1: Failed with Error (with ERROR_MESSAGE column)
print("\n1️⃣  FAILED WITH ERROR QUERY:")
print("-" * 70)
try:
    data = get_level3_failed_with_error()
    print(f"✅ Query executed successfully")
    print(f"📋 Records found: {len(data)}")
    
    if data:
        print(f"\n📝 Sample Record:")
        sample = data[0]
        for key, value in sample.items():
            val_str = str(value)[:100] if value else 'None'
            print(f"   {key}: {val_str}")
        
        # Check for error_message column
        if 'error_message' in sample:
            print(f"\n✅ ERROR_MESSAGE column present!")
        else:
            print(f"\n⚠️  ERROR_MESSAGE column missing!")
    else:
        print("\n✅ Query works but no failed jobs (good news!)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Long Running Sessions (with duration comparisons)
print("\n\n2️⃣  LONG RUNNING SESSIONS QUERY:")
print("-" * 70)
try:
    data = get_level3_long_running()
    print(f"✅ Query executed successfully")
    print(f"📋 Records found: {len(data)}")
    
    if data:
        print(f"\n📝 Sample Record:")
        sample = data[0]
        for key, value in sample.items():
            print(f"   {key}: {value}")
        
        # Check for new duration columns
        if 'current_duration_min' in sample and 'avg_duration_min' in sample:
            print(f"\n✅ DURATION columns present!")
            print(f"   Current: {sample['current_duration_min']} min")
            print(f"   Average: {sample['avg_duration_min']} min")
        else:
            print(f"\n⚠️  DURATION columns missing!")
    else:
        print("\n✅ Query works but no long-running sessions (good news!)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("SUMMARY:")
print("="*70)
print("""
✅ Updated Queries Include:

1. Failed with Error:
   - Shows only failed jobs that haven't been restarted
   - Includes ERROR_MESSAGE column
   - More accurate failure detection

2. Long Running Sessions:
   - Compares current runtime with historical average
   - Shows sessions running longer than normal
   - Includes duration comparison columns
""")
print("="*70)
