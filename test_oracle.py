# Test Oracle Connection and Data
import sys
import os

# Add project to path
sys.path.insert(0, r'C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from portal.services.level3_service import get_level3_failed_jobs
import json

print("="*60)
print("TESTING ORACLE DATABASE CONNECTION")
print("="*60)

try:
    print("\n🔄 Fetching data from Oracle...")    
    summary, data = get_level3_failed_jobs()
    
    print(f"\n✅ SUCCESS!")
    print(f"📊 Summary: {summary}")
    print(f"📋 Total Records: {len(data)}")
    
    if data:
        print(f"\n📝 First Record:")
        first_record = data[0]
        for key, value in first_record.items():
            print(f"   {key}: {value}")
    else:
        print("\n⚠️  No records returned from Oracle")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
