#!/usr/bin/env python
"""Test ERP data freshness - check latest run times"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portal'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("=" * 80)
print("ERP DATA FRESHNESS CHECK")
print("=" * 80)
print()

# Check current database time
db_time_query = """
SELECT 
    TO_CHAR(SYSDATE, 'DD-MON-YYYY HH12:MI:SS AM') AS oracle_time,
    SYSDATE - 3 AS three_days_ago
FROM DUAL
"""

print("1. Database Time Check:")
print("-" * 80)
db_time = fetch_all_mapdqprd(db_time_query)
if db_time:
    print(f"   Oracle SYSDATE: {db_time[0]['oracle_time']}")
print()

# Check latest ERP master run
latest_run_query = """
SELECT 
    ASSET_NAME,
    TO_CHAR(START_TIME, 'DD-MON-YYYY HH12:MI:SS AM') AS start_time,
    TO_CHAR(END_TIME, 'DD-MON-YYYY HH12:MI:SS AM') AS end_time,
    STATUS,
    ROUND((SYSDATE - START_TIME) * 24, 2) AS hours_ago
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
ORDER BY START_TIME DESC
FETCH FIRST 5 ROWS ONLY
"""

print("2. Latest 5 ERP Master Runs:")
print("-" * 80)
latest_runs = fetch_all_mapdqprd(latest_run_query)
if latest_runs:
    for idx, run in enumerate(latest_runs, 1):
        print(f"   {idx}. Start: {run['start_time']}")
        print(f"      Status: {run['status']}, {run['hours_ago']} hours ago")
        print()
else:
    print("   ❌ NO RUNS FOUND!")
print()

# Check if data exists within last 3 days
recent_count_query = """
SELECT 
    COUNT(DISTINCT TASKFLOW_RUN_ID) as run_count,
    MIN(START_TIME) as earliest,
    MAX(START_TIME) as latest
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 3
"""

print("3. Runs in Last 3 Days (Current Filter):")
print("-" * 80)
recent_counts = fetch_all_mapdqprd(recent_count_query)
if recent_counts:
    rc = recent_counts[0]
    print(f"   Total Runs: {rc['run_count']}")
    if rc['earliest']:
        print(f"   Earliest: {rc['earliest']}")
        print(f"   Latest: {rc['latest']}")
else:
    print("   ❌ NO DATA IN LAST 3 DAYS!")
print()

# Check all data regardless of date
all_count_query = """
SELECT 
    COUNT(DISTINCT TASKFLOW_RUN_ID) as run_count,
    MIN(START_TIME) as earliest,
    MAX(START_TIME) as latest,
    ROUND((SYSDATE - MAX(START_TIME)) * 24, 2) AS hours_since_latest
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
"""

print("4. ALL Runs (No Date Filter):")
print("-" * 80)
all_counts = fetch_all_mapdqprd(all_count_query)
if all_counts:
    ac = all_counts[0]
    print(f"   Total Runs Ever: {ac['run_count']}")
    if ac['latest']:
        print(f"   Latest Run: {ac['latest']}")
        print(f"   Hours Since Latest: {ac['hours_since_latest']}")
else:
    print("   ❌ NO DATA AT ALL!")

print()
print("=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

if all_counts and all_counts[0]['hours_since_latest']:
    hours = all_counts[0]['hours_since_latest']
    if hours > 72:
        print(f"❌ ISSUE: Latest run was {hours:.1f} hours ago (>3 days)")
        print(f"   The query filters to SYSDATE - 3, so no data appears!")
        print(f"   SOLUTION: Increase filter from 3 to 7+ days")
    elif hours > 24:
        print(f"⚠️  Latest run was {hours:.1f} hours ago")
        print(f"   Data should still be visible (within 3 day filter)")
    else:
        print(f"✅ Latest run was {hours:.1f} hours ago - recent!")

print("=" * 80)
