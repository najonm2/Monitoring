"""
Debug ERP Current Run Query
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("\n" + "="*60)
print("  DEBUG: ERP Current Run Query")
print("="*60)

# Step 1: Check latest master workflow run
print("\n📌 STEP 1: Check latest master workflow runs")
query1 = """
SELECT 
    TASKFLOW_RUN_ID,
    TO_CHAR(START_TIME, 'DD-MON-YYYY HH12:MI:SS AM') AS START_TIME,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
AND START_TIME >= SYSDATE - 1
ORDER BY START_TIME DESC
FETCH FIRST 3 ROWS ONLY
"""
try:
    master_runs = fetch_all_mapdqprd(query1)
    print(f"Found {len(master_runs)} master runs in last 24 hours:")
    for i, run in enumerate(master_runs, 1):
        print(f"  {i}. TASKFLOW_RUN_ID: {run.get('taskflow_run_id')}")
        print(f"     Start: {run.get('start_time')}")
        print(f"     Status: {run.get('status')}\n")
    
    if master_runs:
        latest_run_id = master_runs[0].get('taskflow_run_id')
        print(f"✅ Latest TASKFLOW_RUN_ID: {latest_run_id}")
        
        # Step 2: Count jobs with this run ID
        print(f"\n📌 STEP 2: Count jobs for TASKFLOW_RUN_ID = {latest_run_id}")
        query2 = f"""
        SELECT COUNT(*) AS job_count
        FROM MAPDQPRD.IICS_CDI_RUN_INFO
        WHERE TASKFLOW_RUN_ID = '{latest_run_id}'
        AND LOCATION IN (
            'CDW_DSL_ERP\\Workflows',
            'CDW_DSL_ERP\\Sessions',
            'CDW_ASL_SAPS4\\Workflows',
            'ASL_ERP_DATAHUB\\Workflows'
        )
        """
        count_result = fetch_all_mapdqprd(query2)
        job_count = count_result[0].get('job_count', 0) if count_result else 0
        print(f"  Total jobs with this TASKFLOW_RUN_ID: {job_count}")
        
        # Step 3: Show sample jobs
        if job_count > 0:
            print(f"\n📌 STEP 3: Show first 5 jobs for this run")
            query3 = f"""
            SELECT 
                ASSET_NAME,
                SUBTASK_ASSET_NAME,
                STATUS,
                TO_CHAR(START_TIME, 'HH12:MI:SS AM') AS START_TIME
            FROM MAPDQPRD.IICS_CDI_RUN_INFO
            WHERE TASKFLOW_RUN_ID = '{latest_run_id}'
            AND LOCATION IN (
                'CDW_DSL_ERP\\Workflows',
                'CDW_DSL_ERP\\Sessions',
                'CDW_ASL_SAPS4\\Workflows',
                'ASL_ERP_DATAHUB\\Workflows'
            )
            AND ROWNUM <= 5
            ORDER BY START_TIME DESC
            """
            sample_jobs = fetch_all_mapdqprd(query3)
            for i, job in enumerate(sample_jobs, 1):
                print(f"  {i}. {job.get('asset_name')}")
                print(f"     Status: {job.get('status')} | Start: {job.get('start_time')}")
        else:
            print("  ⚠️  No jobs found with this TASKFLOW_RUN_ID!")
            print("\n📌 STEP 4: Try user's query approach (latest per asset)")
            query4 = """
            SELECT
                ASSET_NAME,
                STATUS,
                TO_CHAR(START_TIME, 'HH12:MI:SS AM') AS START_TIME
            FROM (
                SELECT
                    ASSET_NAME,
                    STATUS,
                    START_TIME,
                    ROW_NUMBER() OVER (
                        PARTITION BY ASSET_NAME
                        ORDER BY START_TIME DESC
                    ) AS RN
                FROM MAPDQPRD.IICS_CDI_RUN_INFO
                WHERE LOCATION IN (
                    'CDW_DSL_ERP\\Workflows',
                    'CDW_DSL_ERP\\Sessions',
                    'CDW_ASL_SAPS4\\Workflows',
                    'ASL_ERP_DATAHUB\\Workflows'
                )
                AND ASSET_NAME NOT LIKE '%TAX%'
            )
            WHERE RN = 1
            AND ROWNUM <= 10
            ORDER BY
                CASE
                    WHEN STATUS = 'RUNNING' THEN 1
                    WHEN STATUS = 'FAILED' THEN 2
                    ELSE 3
                END,
                START_TIME DESC
            """
            latest_jobs = fetch_all_mapdqprd(query4)
            print(f"\n  Found {len(latest_jobs)} jobs using latest-per-asset approach:")
            for i, job in enumerate(latest_jobs, 1):
                status_icon = "⏱️" if job.get('status') == 'RUNNING' else "✅" if job.get('status') == 'SUCCESS' else "❌"
                print(f"    {i}. {status_icon} {job.get('asset_name')}")
                print(f"       Status: {job.get('status')} | Start: {job.get('start_time')}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
