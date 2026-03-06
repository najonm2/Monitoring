"""
Compare Portal query results with what SSRS would show
Check if there are any filtering differences
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all
from datetime import datetime

print("\n" + "=" * 80)
print("  COMPARING PORTAL QUERY WITH SSRS REQUIREMENTS")
print("=" * 80)

# 1. Check what SYSDATE is right now
print("\n1. CURRENT DATABASE TIME:")
print("-" * 80)
time_check = fetch_all("SELECT SYSDATE, TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') AS current_time FROM DUAL")
for row in time_check:
    print(f"   SYSDATE: {row.get('current_time')}")

# 2. Our current portal query (simplified version)
print("\n2. PORTAL QUERY - Current Implementation:")
print("-" * 80)
portal_query = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS cnt
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
"""
portal_result = fetch_all(portal_query)
portal_count = portal_result[0].get('cnt', 0) if portal_result else 0
print(f"   Count: {portal_count} failed sessions")

# 3. Check if SSRS might be using different date filtering
print("\n3. ALTERNATIVE QUERY APPROACHES:")
print("-" * 80)

# A. Using >= instead of TRUNC
query_a = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS cnt
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND START_TIME >= TRUNC(SYSDATE)
    AND START_TIME < TRUNC(SYSDATE) + 1
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
"""
result_a = fetch_all(query_a)
count_a = result_a[0].get('cnt', 0) if result_a else 0
print(f"   A. Using >= and < (date range): {count_a} sessions")

# B. Check if excluding a specific job matters
query_b = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS cnt
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    AND INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
"""
result_b = fetch_all(query_b)
count_b = result_b[0].get('cnt', 0) if result_b else 0
print(f"   B. Excluding specific job: {count_b} sessions")

# C. Get ALL failed sessions (without limiting to latest per instance)
query_c = """
    SELECT COUNT(*) AS cnt
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
"""
result_c = fetch_all(query_c)
count_c = result_c[0].get('cnt', 0) if result_c else 0
print(f"   C. ALL failed runs (no MAX filter): {count_c} total failures")

# D. Get distinct sessions that failed (ignoring restarts)
query_d = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS cnt
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
"""
result_d = fetch_all(query_d)
count_d = result_d[0].get('cnt', 0) if result_d else 0
print(f"   D. DISTINCT sessions that failed (any time today): {count_d} sessions")

# 4. Check what SSRS screenshot showed (77 jobs)
print("\n4. SSRS COMPARISON:")
print("-" * 80)
print(f"   SSRS Screenshot: ~77 failed jobs (March 5, 2026)")
print(f"   Portal Current:  {portal_count} failed jobs")
print(f"   Difference:      {77 - portal_count}")

# 5. Check if SSRS is including jobs that have SUCCEEDED after failure
print("\n5. SESSIONS THAT FAILED BUT LATER SUCCEEDED:")
print("-" * 80)
query_e = """
    SELECT COUNT(DISTINCT session_name) AS cnt
    FROM (
        SELECT 
            TIR.INSTANCE_NAME AS session_name,
            MIN(CASE WHEN RUN_STATUS_CODE IN (3,4,5,15) THEN 1 ELSE 0 END) AS had_failure,
            MAX(CASE WHEN RUN_STATUS_CODE = 1 THEN 1 ELSE 0 END) AS had_success
        FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
        WHERE TASK_TYPE_NAME = 'Session'
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        GROUP BY TIR.INSTANCE_NAME
        HAVING MIN(CASE WHEN RUN_STATUS_CODE IN (3,4,5,15) THEN 1 ELSE 0 END) = 1
    )
"""
result_e = fetch_all(query_e)
count_e = result_e[0].get('cnt', 0) if result_e else 0
print(f"   Sessions that experienced failure today: {count_e}")

# 6. Get sample of failed job names to compare with SSRS
print("\n6. SAMPLE FAILED JOB NAMES (First 10):")
print("-" * 80)
sample_query = """
    SELECT INSTANCE_NAME, START_TIME, 
           DECODE(RUN_STATUS_CODE, 3, 'Failed', 4, 'Stopped', 5, 'Aborted', 15, 'Terminated') AS status
    FROM (
        SELECT INSTANCE_NAME, START_TIME, RUN_STATUS_CODE
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE TASK_TYPE_NAME = 'Session'
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        AND RUN_STATUS_CODE IN (3, 4, 5, 15)
        ORDER BY START_TIME DESC
    )
    WHERE ROWNUM <= 10
"""
samples = fetch_all(sample_query)
for i, row in enumerate(samples, 1):
    print(f"   {i}. {row.get('instance_name')} - {row.get('status')} at {row.get('start_time')}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
print("Compare these results:")
print(f"  - If portal shows {portal_count} and SSRS shows 77:")
print(f"    → Check if SSRS is counting ALL failures (approach C: {count_c})")
print(f"    → Check if SSRS includes failed-then-succeeded (approach E: {count_e})")
print(f"    → Check if there's a date/time difference issue")
print("\nNext Steps:")
print("  1. Compare the sample job names with what you see in SSRS")
print("  2. Check which counting method SSRS uses")
print("  3. Verify the date filter matches SSRS configuration")
print("=" * 80 + "\n")
