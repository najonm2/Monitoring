#!/usr/bin/env python
"""Test Oracle connection with current credentials"""
import sys
import os
import time

# Add portal to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portal'))

from db.oracle_client import get_conn

print("=" * 60)
print("Testing Oracle Connection...")
print("=" * 60)
print(f"Host: azeus2loraipcp2.corp.intranet:1521")
print(f"Service: infr01p_app")
print(f"User: icsm_appl")
print(f"Password: Infprd3_appl (length: {len('Infprd3_appl')} chars)")
print("=" * 60)
print()

try:
    print("⏳ Attempting connection (30 second timeout)...")
    start = time.time()
    
    conn = get_conn()
    elapsed = time.time() - start
    
    print(f"✅ CONNECTION SUCCESSFUL in {elapsed:.2f}s")
    print()
    
    # Test a simple query
    print("Testing simple query...")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM DUAL")
    result = cursor.fetchone()
    
    print(f"✅ QUERY SUCCESSFUL: {result}")
    print()
    
    cursor.close()
    conn.close()
    
    print("=" * 60)
    print("✅ Oracle connection is working correctly!")
    print("=" * 60)
    
except Exception as e:
    elapsed = time.time() - start
    print()
    print("=" * 60)
    print(f"❌ CONNECTION FAILED after {elapsed:.2f}s")
    print("=" * 60)
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print()
    print("DIAGNOSIS:")
    
    error_msg = str(e).lower()
    
    if "invalid username/password" in error_msg or "ora-01017" in error_msg:
        print("❌ INCORRECT PASSWORD - The password 'Infprd3_appl' is WRONG")
        print("   Action: Get the correct new password and update oracle_client.py")
    elif "listener" in error_msg or "ora-12541" in error_msg:
        print("❌ LISTENER ERROR - Cannot reach Oracle server")
    elif "timeout" in error_msg or "timed out" in error_msg:
        print("❌ CONNECTION TIMEOUT - Network or firewall issue")
    elif "ora-28000" in error_msg:
        print("❌ ACCOUNT LOCKED - The icsm_appl account is locked")
    else:
        print(f"❌ UNKNOWN ERROR - Check Oracle DBA")
    
    print("=" * 60)
    
    import traceback
    print()
    print("Full traceback:")
    traceback.print_exc()
    
    sys.exit(1)
