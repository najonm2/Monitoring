#!/usr/bin/env python
import sys
print("=" * 80)
print("DEPENDENCY DIAGNOSTIC")
print("=" * 80)

# Test 1: Check oracledb
print("\n1?? Testing oracledb import...")
try:
    import oracledb
    print(f"? oracledb installed: {oracledb.__version__}")
except ImportError as e:
    print(f"? oracledb NOT installed: {e}")
    print("   FIX: pip install oracledb")
    sys.exit(1)

# Test 2: Check oracle_client
print("\n2?? Testing oracle_client import...")
try:
    from portal.db.oracle_client import get_conn, fetch_all, oracle_cursor
    print("? oracle_client imports successfully")
except Exception as e:
    print(f"? oracle_client import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check level3_queries
print("\n3?? Testing level3_queries import...")
try:
    from portal.sql.level3_queries import MAIN_QUERY, clean_sql
    print("? level3_queries imports successfully")
    print(f"   MAIN_QUERY length: {len(MAIN_QUERY)} chars")
except Exception as e:
    print(f"? level3_queries import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check level3_service
print("\n4?? Testing level3_service import...")
try:
    from portal.services.level3_service import (
        get_level3_failed_jobs,
        get_level3_failed_with_error,
        get_level3_long_running,
    )
    print("? level3_service imports successfully!")
    print(f"   - get_level3_failed_jobs: {get_level3_failed_jobs.__name__}")
    print(f"   - get_level3_failed_with_error: {get_level3_failed_with_error.__name__}")
    print(f"   - get_level3_long_running: {get_level3_long_running.__name__}")
except Exception as e:
    print(f"? level3_service import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test Oracle connection
print("\n5?? Testing Oracle connection...")
try:
    conn = get_conn()
    print("? Oracle connection successful!")
    conn.close()
except Exception as e:
    print(f"?? Oracle connection failed (may be DB issue, not Python issue): {e}")
    print("   This is OK - check Oracle credentials in oracle_client.py")

print("\n" + "=" * 80)
print("? ALL PYTHON DEPENDENCIES OK!")
print("=" * 80)