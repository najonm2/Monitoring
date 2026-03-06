"""Test the pending-only query to verify it returns 5 rows, not 12"""
import sys
sys.path.insert(0, r'C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from portal.db.oracle_client import fetch_all

# Test query - should return ONLY pending failures (latest status = failed)
test_query = """
SELECT 
    TIR.SERVER_NAME AS grid_name,
    TIR.SUBJECT_AREA AS folder_name,
    TIR.WORKFLOW_NAME AS workflow_name,
    TIR.INSTANCE_NAME AS session_name,
    TIR.START_TIME AS start_time,
    TIR.END_TIME AS end_time,
    CASE 
        WHEN TIR.RUN_STATUS_CODE = 3 THEN 'Failed'
        WHEN TIR.RUN_STATUS_CODE = 4 THEN 'Stopped'
        WHEN TIR.RUN_STATUS_CODE = 5 THEN 'Aborted'
        WHEN TIR.RUN_STATUS_CODE = 15 THEN 'Terminated'
        ELSE 'Unknown'
    END AS status
FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
WHERE TIR.TASK_TYPE_NAME = 'Session'
AND TRUNC(TIR.START_TIME) = TRUNC(SYSDATE)
AND TIR.RUN_STATUS_CODE IN (3, 4, 5, 15)
AND TIR.INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
AND (TIR.INSTANCE_NAME, TIR.START_TIME) IN (
    SELECT INSTANCE_NAME, MAX(START_TIME)
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TASK_TYPE_NAME = 'Session'
    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
    GROUP BY INSTANCE_NAME
)
ORDER BY TIR.START_TIME DESC
"""

print("\n" + "="*60)
print("Testing PENDING-ONLY query (should return 5 rows)")
print("="*60)

results = fetch_all(test_query)
print(f"\n✓ Query returned: {len(results)} rows")
print("\nSessions found:")
for i, row in enumerate(results, 1):
    session = row.get('session_name', '')
    status = row.get('status', '')
    start = row.get('start_time', '')
    folder = row.get('folder_name', '')
    print(f"  {i}. {session[:50]:<50} | {status:<8} | Folder: {folder or '(empty)'}")

print("\n" + "="*60)
print(f"Expected: 5 pending failures")
print(f"Actual:   {len(results)} rows")
if len(results) == 5:
    print("✅ CORRECT! Query is working as expected")
else:
    print(f"❌ MISMATCH! Should be 5, got {len(results)}")
print("="*60)
