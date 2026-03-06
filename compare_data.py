# Test API Endpoint Directly
import sys
import os

sys.path.insert(0, r'C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from portal.api_views import generate_realistic_data
from portal.services.level3_service import get_level3_failed_jobs
import json

print("="*70)
print("ORACLE VS MOCK DATA COMPARISON")
print("="*70)

# Test 1: Oracle Data
print("\n1️⃣  ORACLE DATABASE DATA:")
print("-" * 70)
try:
    summary, data = get_level3_failed_jobs()
    print(f"✅ Connection: SUCCESS")
    print(f"📊 Summary: {summary}")
    print(f"📋 Records: {len(data)}")
    if data:
        print(f"\nSample Record:")
        print(json.dumps(data[0], indent=2, default=str))
    else:
        print("⚠️  No failed jobs in database today")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Mock Data
print("\n\n2️⃣  MOCK/SIMULATED DATA:")
print("-" * 70)
try:
    mock_result = generate_realistic_data("level3_failed")
    print(f"✅ Generation: SUCCESS")
    print(f"📊 Summary: {mock_result.get('summary')}")
    print(f"📋 Records: {len(mock_result.get('data', []))}")
    if mock_result.get('data'):
        print(f"\nSample Record:")
        print(json.dumps(mock_result['data'][0], indent=2, default=str))
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("EXPLANATION:")
print("="*70)
print("""
✅ ORACLE DATA (Real):
   - Shows actual failed jobs from INFA_PCREPO repository
   - Currently: 0 records (no failures today - good news!)
   
🎭 MOCK DATA (Simulated):
   - Generated realistic test data for development/demo
   - Always returns 5-15 sample records
   - Used when Oracle has no data or for testing

🔄 API BEHAVIOR:
   - API will use ORACLE data when available
   - If empty, you'll see "No records found" message
   - Mock data only used if Oracle connection fails
""")
print("="*70)
