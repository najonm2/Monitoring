"""
CRITICAL: Check if timezone difference is causing the count mismatch
SSRS might be using GMT while portal uses MST (Mountain Standard Time)
MST = GMT-7 hours (or GMT-6 during daylight saving)
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
print("  TIMEZONE INVESTIGATION - MST vs GMT Issue")
print("=" * 80)

# 1. Check Oracle's current timezone settings
print("\n1. ORACLE TIMEZONE SETTINGS:")
print("-" * 80)
timezone_query = """
    SELECT 
        SYSDATE,
        CURRENT_TIMESTAMP,
        SYSTIMESTAMP,
        DBTIMEZONE,
        SESSIONTIMEZONE
    FROM DUAL
"""
timezone_info = fetch_all(timezone_query)
for row in timezone_info:
    print(f"   Oracle SYSDATE:        {row.get('sysdate')}")
    print(f"   Oracle CURRENT_TIMESTAMP: {row.get('current_timestamp')}")
    print(f"   Oracle SYSTIMESTAMP:   {row.get('systimestamp')}")
    print(f"   Database Timezone:     {row.get('dbtimezone')}")
    print(f"   Session Timezone:      {row.get('sessiontimezone')}")

print(f"\n   Python datetime.now(): {datetime.now()}")
print(f"   Python Date: {datetime.now().strftime('%Y-%m-%d')}")

# 2. Check failed jobs count using SYSDATE (current database time)
print("\n2. FAILED JOBS USING SYSDATE (Database Time):")
print("-" * 80)
sysdate_query = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS CNT,
           TO_CHAR(TRUNC(SYSDATE), 'YYYY-MM-DD') AS QUERY_DATE
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
"""
sysdate_result = fetch_all(sysdate_query)
for row in sysdate_result:
    print(f"   Query Date: {row.get('query_date')}")
    print(f"   Failed Jobs Count: {row.get('cnt')}")

# 3. Check failed jobs for specific dates (March 5 and March 6, 2026 in GMT)
print("\n3. FAILED JOBS BY SPECIFIC DATES:")
print("-" * 80)
specific_dates_query = """
    SELECT 
        TO_CHAR(TRUNC(START_TIME), 'YYYY-MM-DD') AS JOB_DATE,
        COUNT(DISTINCT INSTANCE_NAME) AS FAILED_COUNT
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) BETWEEN TO_DATE('2026-03-04', 'YYYY-MM-DD') 
                              AND TO_DATE('2026-03-07', 'YYYY-MM-DD')
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    GROUP BY TRUNC(START_TIME)
    ORDER BY TRUNC(START_TIME) DESC
"""
date_results = fetch_all(specific_dates_query)
for row in date_results:
    print(f"   {row.get('job_date')}: {row.get('failed_count')} failed jobs")

# 4. Check if converting to MST timezone affects the count
print("\n4. TIMEZONE CONVERSION TEST (GMT to MST = -7 hours):")
print("-" * 80)
print("   If Oracle stores in GMT, March 6 00:00 GMT = March 5 17:00 MST")
print("   SSRS might be filtering by MST date, portal by GMT date")

# Query using timezone-adjusted date
mst_adjusted_query = """
    SELECT 
        TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS START_TIME_STR,
        TO_CHAR(START_TIME - INTERVAL '7' HOUR, 'YYYY-MM-DD HH24:MI:SS') AS MST_TIME,
        INSTANCE_NAME
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    AND ROWNUM <= 5
"""
print("\n   Sample jobs from TODAY (showing GMT and MST conversions):")
mst_samples = fetch_all(mst_adjusted_query)
for row in mst_samples:
    print(f"   GMT: {row.get('start_time_str')} -> MST: {row.get('mst_time')} | {row.get('instance_name')}")

# 5. Check what date range SSRS might be using based on MST
print("\n5. CRITICAL TEST: Jobs that would match SSRS query (March 5 MST):")
print("-" * 80)
print("   If SSRS filters by 'March 5, 2026 MST', it converts to:")
print("   Start: March 5 00:00 MST = March 5 07:00 GMT")
print("   End:   March 6 00:00 MST = March 6 07:00 GMT")

ssrs_match_query = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS SSRS_COUNT
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
    AND START_TIME >= TO_DATE('2026-03-05 07:00:00', 'YYYY-MM-DD HH24:MI:SS')
    AND START_TIME < TO_DATE('2026-03-06 07:00:00', 'YYYY-MM-DD HH24:MI:SS')
"""
ssrs_result = fetch_all(ssrs_match_query)
for row in ssrs_result:
    print(f"\n   Jobs in range March 5 07:00 GMT to March 6 07:00 GMT: {row.get('ssrs_count')}")
    print(f"   (This is March 5 00:00 MST to March 6 00:00 MST)")

# 6. Alternative: Check if using current MST date
print("\n6. USING CURRENT DATE IN MST (subtract 7 hours from SYSDATE):")
print("-" * 80)
mst_today_query = """
    SELECT COUNT(DISTINCT INSTANCE_NAME) AS MST_COUNT,
           TO_CHAR(TRUNC(SYSDATE - INTERVAL '7' HOUR), 'YYYY-MM-DD') AS MST_DATE
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME - INTERVAL '7' HOUR) = TRUNC(SYSDATE - INTERVAL '7' HOUR)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
"""
mst_today_result = fetch_all(mst_today_query)
for row in mst_today_result:
    print(f"   MST Date: {row.get('mst_date')}")
    print(f"   Failed Jobs (MST-adjusted): {row.get('mst_count')}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
print("If SSRS shows ~77 jobs and uses MST timezone:")
print("  - Portal query should use: TRUNC(START_TIME - INTERVAL '7' HOUR)")
print("  - Or convert SYSDATE to MST before comparison")
print("\nIf counts match when using MST adjustment, we found the root cause!")
print("=" * 80 + "\n")
