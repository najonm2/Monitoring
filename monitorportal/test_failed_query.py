#!/usr/bin/env python
"""Test the actual failed jobs query that's timing out"""
import sys
import os
import time

# Add portal to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portal'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.services.level3_service import get_level3_failed_with_error

print("=" * 60)
print("Testing Failed Jobs Query (Level 3)")
print("=" * 60)
print()

try:
    print("⏳ Running query (60 second timeout)...")
    start = time.time()
    
    result = get_level3_failed_with_error()
    
    elapsed = time.time() - start
    
    print()
    print("=" * 60)
    print(f"✅ QUERY SUCCESSFUL!")
    print("=" * 60)
    print(f"Time: {elapsed:.2f} seconds")
    print(f"Rows returned: {len(result)}")
    
    if result:
        print()
        print("Sample row (first record):")
        print(f"  Session: {result[0].get('session_name', 'N/A')[:50]}")
        print(f"  Status: {result[0].get('status', 'N/A')}")
        print(f"  Error: {result[0].get('error_message', 'N/A')[:100]}")
    
    print("=" * 60)
    
except Exception as e:
    elapsed = time.time() - start
    print()
    print("=" * 60)
    print(f"❌ QUERY FAILED after {elapsed:.2f}s")
    print("=" * 60)
    print(f"Error: {str(e)}")
    print()
    
    import traceback
    traceback.print_exc()
    
    sys.exit(1)
