#!/usr/bin/env python
"""
Explore MAPDQPRD schema to find tables that might track run recoveries or audit logs
"""
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("=" * 100)
print("EXPLORING MAPDQPRD SCHEMA FOR IICS TABLES")
print("=" * 100)
print()

# First, find all tables owned by MAPDQPRD
query1 = """
SELECT table_name, num_rows, last_analyzed
FROM user_tables
WHERE table_name LIKE '%IICS%' OR table_name LIKE '%CDI%' OR table_name LIKE '%AUDIT%' OR table_name LIKE '%LOG%'
ORDER BY table_name
"""

print("Step 1: Finding IICS-related tables...")
print("-" * 100)

try:
    tables = fetch_all_mapdqprd(query1)
    
    if tables:
        print(f"\nFound {len(tables)} tables:\n")
        for t in tables:
            rows = t.get('num_rows', 'Unknown')
            analyzed = t.get('last_analyzed', 'Never')
            print(f"  📋 {t['table_name']:<50} Rows: {rows or 'Unknown':<15}")
    else:
        print("❌ No tables found")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 100)
print("Step 2: Check IICS_CDI_RUN_INFO table structure...")
print("-" * 100)

query2 = """
SELECT column_name, data_type, nullable
FROM user_tab_columns
WHERE table_name = 'IICS_CDI_RUN_INFO'
ORDER BY column_id
"""

try:
    columns = fetch_all_mapdqprd(query2)
    
    if columns:
        print(f"\nIICS_CDI_RUN_INFO has {len(columns)} columns:\n")
        for col in columns:
            nullable = "NULL" if col['nullable'] == 'Y' else "NOT NULL"
            print(f"  - {col['column_name']:<30} {col['data_type']:<20} {nullable}")
    else:
        print("❌ Could not read table structure")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 100)
print("Step 3: Check for audit/activity tracking tables...")
print("-" * 100)

query3 = """
SELECT table_name
FROM user_tables
WHERE table_name LIKE '%ACTIVITY%' 
   OR table_name LIKE '%HISTORY%'
   OR table_name LIKE '%EVENT%'
   OR table_name LIKE '%TRACKING%'
ORDER BY table_name
"""

try:
    audit_tables = fetch_all_mapdqprd(query3)
    
    if audit_tables:
        print(f"\nFound {len(audit_tables)} potential audit tables:\n")
        for t in audit_tables:
            print(f"  📋 {t['table_name']}")
    else:
        print("❌ No audit tables found")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 100)
print("Step 4: Sample data from one suspended run...")
print("-" * 100)

query4 = """
SELECT *
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = '1215720696580263936'
AND ROWNUM <= 5
"""

try:
    sample = fetch_all_mapdqprd(query4)
    
    if sample:
        print(f"\nSample record from 12:00 PM run (user says completed):\n")
        for key, value in sample[0].items():
            print(f"  {key:<30} = {value}")
    else:
        print("❌ No data found")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 100)
print("\nCONCLUSIONS:")
print("=" * 100)
print("""
Based on available tables, we can:

Option A: Use existing IICS_CDI_RUN_INFO table
  - Shows raw IICS execution history
  - Does NOT track manual recoveries
  - Immutable historical record
  
Option B: Create custom recovery tracking table
  - Store manual recovery actions (user, timestamp, notes)
  - Link to TASKFLOW_RUN_ID
  - Overlay on dashboard to show "Manually Recovered" status
  
Option C: Query IICS REST API for activity logs
  - Requires IICS API credentials
  - May have audit logs for manual actions
  - More complex integration

RECOMMENDATION: Option B - Custom recovery tracking
  - Simple to implement
  - Full control over data
  - No dependency on IICS API
""")
