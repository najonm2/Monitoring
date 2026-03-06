import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd
import json

print("=" * 80)
print("TESTING ERP MASTER WORKFLOW TRACKING WITH TASKFLOW_RUN_ID")
print("=" * 80)

# Test 1: Find last 8 distinct run IDs
print("\n1. Last 8 Distinct TASKFLOW_RUN_ID values:")
query1 = """
SELECT DISTINCT
    TASKFLOW_RUN_ID
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE LOCATION IN (
    'CDW_DSL_ERP\\Workflows',
    'CDW_DSL_ERP\\Sessions',
    'CDW_ASL_SAPS4\\Workflows',
    'ASL_ERP_DATAHUB\\Workflows'
)
AND ASSET_NAME NOT LIKE '%TAX%'
AND START_TIME >= SYSDATE - 3
ORDER BY TASKFLOW_RUN_ID DESC
FETCH FIRST 10 ROWS ONLY
"""
run_ids = fetch_all_mapdqprd(query1)
print(f"Found {len(run_ids)} distinct run IDs")
print(json.dumps(run_ids, indent=2, default=str))

# Test 2: Get master workflow for each run ID
if run_ids:
    latest_run_id = run_ids[0]['taskflow_run_id']
    print(f"\n2. Master Workflow for latest run (TASKFLOW_RUN_ID={latest_run_id}):")
    query2 = """
    SELECT 
        TASKFLOW_RUN_ID,
        ASSET_NAME,
        INSTANCE_NAME,
        TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') as start_time_raw,
        TO_CHAR(END_TIME, 'YYYY-MM-DD HH24:MI:SS') as end_time_raw,
        STATUS
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
    AND TASKFLOW_RUN_ID = :run_id
    """
    master_runs = fetch_all_mapdqprd(query2, {'run_id': latest_run_id})
    print(json.dumps(master_runs, indent=2, default=str))

    # Test 3: Get start/end markers for latest run
    print(f"\n3. Start/End Markers for latest run (TASKFLOW_RUN_ID={latest_run_id}):")
    query3 = """
    SELECT 
        ASSET_NAME,
        TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') as start_time_raw,
        TO_CHAR(END_TIME, 'YYYY-MM-DD HH24:MI:SS') as end_time_raw,
        STATUS
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE (ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_START' 
           OR ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END')
    AND TASKFLOW_RUN_ID = :run_id
    ORDER BY START_TIME
    """
    markers = fetch_all_mapdqprd(query3, {'run_id': latest_run_id})
    print(json.dumps(markers, indent=2, default=str))

    # Test 4: Count all jobs in latest run
    print(f"\n4. All Jobs in latest run (TASKFLOW_RUN_ID={latest_run_id}):")
    query4 = """
    SELECT 
        COUNT(*) as total_jobs,
        SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as succeeded,
        SUM(CASE WHEN STATUS = 'RUNNING' THEN 1 ELSE 0 END) as running,
        SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as failed,
        SUM(CASE WHEN STATUS IN ('SUSPENDED', 'CHILD_SUSPENDED') THEN 1 ELSE 0 END) as suspended
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = :run_id
    AND LOCATION IN (
        'CDW_DSL_ERP\\Workflows',
        'CDW_DSL_ERP\\Sessions',
        'CDW_ASL_SAPS4\\Workflows',
        'ASL_ERP_DATAHUB\\Workflows'
    )
    AND ASSET_NAME NOT LIKE '%TAX%'
    """
    job_counts = fetch_all_mapdqprd(query4, {'run_id': latest_run_id})
    print(json.dumps(job_counts, indent=2, default=str))

    # Test 5: Sample jobs from latest run
    print(f"\n5. Sample Jobs (first 5):")
    query5 = """
    SELECT 
        ASSET_NAME,
        LOCATION,
        TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') as start_time_raw,
        STATUS
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE TASKFLOW_RUN_ID = :run_id
    AND LOCATION IN (
        'CDW_DSL_ERP\\Workflows',
        'CDW_DSL_ERP\\Sessions',
        'CDW_ASL_SAPS4\\Workflows',
        'ASL_ERP_DATAHUB\\Workflows'
    )
    AND ASSET_NAME NOT LIKE '%TAX%'
    ORDER BY START_TIME DESC
    FETCH FIRST 5 ROWS ONLY
    """
    sample_jobs = fetch_all_mapdqprd(query5, {'run_id': latest_run_id})
    print(json.dumps(sample_jobs, indent=2, default=str))

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
if run_ids:
    print(f"✓ Found {len(run_ids)} distinct run IDs")
    print(f"  Latest TASKFLOW_RUN_ID: {run_ids[0]['taskflow_run_id']}")
else:
    print("✗ No run IDs found")

# Test 2: Find start/end marker sessions
if master_runs:
    latest_instance = master_runs[0]['instance_name']
    print(f"\n2. Start/End Markers for latest run (Instance: {latest_instance}):")
    
    query2 = """
    SELECT 
        ASSET_NAME,
        INSTANCE_NAME,
        TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') as start_time_raw,
        TO_CHAR(END_TIME, 'YYYY-MM-DD HH24:MI:SS') as end_time_raw,
        STATUS
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE (ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_START' 
           OR ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END')
    AND START_TIME >= SYSDATE - 3
    ORDER BY START_TIME DESC
    FETCH FIRST 20 ROWS ONLY
    """
    markers = fetch_all_mapdqprd(query2)
    print(json.dumps(markers, indent=2, default=str))

# Test 3: Find all jobs related to latest master run
print("\n3. All Jobs in Latest Master Run (child jobs/sessions):")
query3 = """
SELECT 
    ASSET_NAME,
    LOCATION,
    TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') as start_time_raw,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE LOCATION IN (
    'CDW_DSL_ERP\\Workflows',
    'CDW_DSL_ERP\\Sessions',
    'CDW_ASL_SAPS4\\Workflows',
    'ASL_ERP_DATAHUB\\Workflows'
)
AND ASSET_NAME NOT LIKE '%TAX%'
AND START_TIME >= SYSDATE - 0.5
ORDER BY START_TIME DESC
FETCH FIRST 20 ROWS ONLY
"""
latest_jobs = fetch_all_mapdqprd(query3)
print(f"Found {len(latest_jobs)} jobs in last 12 hours")
if latest_jobs:
    print(f"Sample (first 5):")
    print(json.dumps(latest_jobs[:5], indent=2, default=str))

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
if master_runs:
    print(f"✓ Found {len(master_runs)} master workflow runs")
    print(f"  Latest run: {master_runs[0]['start_time_raw']} - {master_runs[0]['status']}")
else:
    print("✗ No master workflow runs found")

if markers:
    start_markers = [m for m in markers if 'START' in m['asset_name']]
    end_markers = [m for m in markers if 'END' in m['asset_name']]
    print(f"✓ Found {len(start_markers)} START markers, {len(end_markers)} END markers")
else:
    print("✗ No start/end markers found")
