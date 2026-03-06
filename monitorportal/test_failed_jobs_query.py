import time
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all

print("=" * 60)
print("TESTING FAILED JOBS QUERIES")
print("=" * 60)

# Test 1: Simple total count
print("\n1. Testing TOTAL FAILED JOBS count...")
start = time.time()
result = fetch_all("""
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS total_count
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
""")
elapsed = time.time() - start
total = result[0].get('total_count', 0) if result else 0
print(f"   Time: {elapsed:.2f}s")
print(f"   Count: {total}")

# Test 2: Get actual session names
print("\n2. Getting failed session names...")
start = time.time()
result = fetch_all("""
    SELECT DISTINCT INSTANCE_NAME
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    ORDER BY INSTANCE_NAME
""")
elapsed = time.time() - start
print(f"   Time: {elapsed:.2f}s")
print(f"   Count: {len(result)}")
if result and len(result) <= 10:
    print("   Sample sessions:")
    for row in result[:5]:
        print(f"     - {row.get('instance_name')}")

# Test 3: Complex main query (with timeout)
print("\n3. Testing MAIN COMPLEX QUERY...")
print("   (This is the slow one - testing first 10 rows)...")
start = time.time()
try:
    result = fetch_all("""
        SELECT DISTINCT 
            TIR.SERVER_NAME AS grid_name,
            TIR.SUBJECT_AREA AS subject_area,
            TIR.WORKFLOW_NAME AS workflow_name,
            TIR.INSTANCE_NAME AS session_name,
            TIR.START_TIME AS start_time,
            TIR.END_TIME AS end_time,
            DECODE(TIR.RUN_STATUS_CODE, 
                   3, 'Failed', 
                   4, 'Stopped', 
                   5, 'Aborted', 
                   15, 'Terminated') AS status
        FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
        WHERE TIR.TASK_TYPE_NAME = 'Session'
        AND TRUNC(TIR.START_TIME) = TRUNC(SYSDATE)
        AND TIR.RUN_STATUS_CODE IN (3, 4, 5, 15)
        AND ROWNUM <= 10
    """)
    elapsed = time.time() - start
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Rows: {len(result)}")
    if result:
        print(f"   Sample: {result[0].get('session_name')}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("EXPECTED: Total should be 77 (from SSRS)")
print("=" * 60)
