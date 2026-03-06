import time
import django
import os
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all

print("=" * 70)
print("INVESTIGATING COUNT MISMATCH: Portal=9 vs SSRS=77")
print("=" * 70)

# Check current database date
print("\n1. What is SYSDATE in the database?")
result = fetch_all("SELECT SYSDATE AS current_date, TRUNC(SYSDATE) AS trunc_date FROM DUAL")
if result:
    print(f"   SYSDATE: {result[0].get('current_date')}")
    print(f"   TRUNC(SYSDATE): {result[0].get('trunc_date')}")

# Check failed jobs by date (last 7 days)
print("\n2. Failed jobs count by date (last 7 days):")
result = fetch_all("""
    SELECT TRUNC(START_TIME) as job_date, 
           COUNT(DISTINCT INSTANCE_NAME) as job_count
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    AND TRUNC(START_TIME) >= TRUNC(SYSDATE) - 7
    GROUP BY TRUNC(START_TIME)
    ORDER BY TRUNC(START_TIME) DESC
""")
if result:
    for row in result:
        print(f"   {row.get('job_date')}: {row.get('job_count')} jobs")

# Test the exact SSRS DataSet2 query
print("\n3. Testing EXACT SSRS DataSet2 query (TOTAL_FAILED_JOBS):")
start = time.time()
result = fetch_all("""
    SELECT Count(DISTINCT SESSION_NAME) AS total_count
    FROM (
        SELECT 
            TIR.SERVER_NAME AS GRID_NAME,
            TIR.SUBJECT_AREA,
            TIR.WORKFLOW_NAME,
            TIR.INSTANCE_NAME AS SESSION_NAME,
            TIR.START_TIME,
            TIR.END_TIME,
            DECODE(RUN_STATUS_CODE,
                1, 'Succeeded',
                2, 'Disabled',
                3, 'Failed',
                4, 'Stopped',
                5, 'Aborted',
                6, 'Running',
                7, 'Suspending',
                8, 'Suspended',
                9, 'Stopping',
                10, 'Aborting',
                11, 'Waiting',
                12, 'Scheduled',
                13, 'Unscheduled',
                14, 'Unknown',
                15, 'Terminated') AS STATUS
        FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
        WHERE TASK_TYPE_NAME = 'Session'
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    )
""")
elapsed = time.time() - start
print(f"   Time: {elapsed:.2f}s")
print(f"   Count: {result[0].get('total_count') if result else 0}")

# Test without LATEST filter
print("\n4. All failed sessions today (no filters):")
result = fetch_all("""
    SELECT COUNT(*) as total_rows
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
""")
print(f"   Total rows: {result[0].get('total_rows') if result else 0}")

# Check if there's data on different date (maybe SSRS ran on different day)
print("\n5. Checking if there are 77 failed jobs on ANY recent date:")
result = fetch_all("""
    SELECT TRUNC(START_TIME) as job_date, 
           COUNT(DISTINCT INSTANCE_NAME) as job_count
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    AND TRUNC(START_TIME) >= TRUNC(SYSDATE) - 30
    GROUP BY TRUNC(START_TIME)
    HAVING COUNT(DISTINCT INSTANCE_NAME) >= 70
    ORDER BY TRUNC(START_TIME) DESC
""")
if result:
    print(f"   Found {len(result)} dates with 70+ failures:")
    for row in result:
        print(f"   {row.get('job_date')}: {row.get('job_count')} jobs")
else:
    print("   No dates found with 70+ failures in last 30 days")

print("\n" + "=" * 70)
print("CONCLUSION: Need to check SSRS report execution date/parameters")
print("=" * 70)
