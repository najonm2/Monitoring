# portal/services/level3_service.py
from portal.db.oracle_client import fetch_all, fetch_all_mapdqprd
from portal.sql.level3_queries import MAIN_QUERY, clean_sql


def get_level3_failed_jobs():
    """
    Fetch failed job status from Oracle
    Returns: (summary_dict, failed_rows_list)
    """
    try:
        query = clean_sql(MAIN_QUERY)
        failed_rows = fetch_all(query)
        
        # Summarize
        summary = {
            "total_failed": len(failed_rows),
            "today_failed": sum(1 for r in failed_rows if str(r.get("status", "")).lower() == "failed"),
        }
        
        return summary, failed_rows
    except Exception as e:
        print(f"Error fetching level3 failed jobs: {e}")
        return {"total_failed": 0, "today_failed": 0}, []


def get_level3_failed_with_error():
    """
    Fetch failed sessions from Oracle - ONLY sessions still failed, not recovered
    Returns: Failed sessions that do NOT have a successful run after the failure
    """
    import time
    start_time = time.time()
    
    try:
        # Get currently failed sessions - exclude those that have recovered/completed
        query = """
        SELECT 
            grid_name,
            subject_area,
            workflow_name,
            session_name,
            start_time,
            end_time,
            status,
            error_message
        FROM (
            SELECT 
                TIR.SERVER_NAME AS grid_name,
                TIR.SUBJECT_AREA AS subject_area,
                TIR.WORKFLOW_NAME AS workflow_name,
                TIR.INSTANCE_NAME AS session_name,
                TIR.START_TIME AS start_time,
                TIR.END_TIME AS end_time,
                DECODE(TIR.RUN_STATUS_CODE, 3, 'Failed', 4, 'Stopped', 5, 'Aborted', 15, 'Terminated') AS status,
                SUBSTR(TIR.RUN_ERR_MSG, 1, 500) AS error_message,
                ROW_NUMBER() OVER (PARTITION BY TIR.INSTANCE_NAME ORDER BY TIR.START_TIME DESC) AS rn,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM INFA_PCREPO.REP_TASK_INST_RUN T2
                        WHERE T2.INSTANCE_NAME = TIR.INSTANCE_NAME
                          AND T2.RUN_STATUS_CODE = 1
                          AND T2.START_TIME >= TRUNC(SYSDATE)
                          AND T2.START_TIME < TRUNC(SYSDATE) + 1
                          AND T2.START_TIME > TIR.START_TIME
                    )
                    THEN 1
                    ELSE 0
                END AS has_recovery
            FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
            WHERE TIR.RUN_STATUS_CODE IN (3, 4, 5, 15)
              AND TIR.TASK_TYPE_NAME = 'Session'
              AND TIR.START_TIME >= TRUNC(SYSDATE)
              AND TIR.START_TIME < TRUNC(SYSDATE) + 1
        )
        WHERE rn = 1
          AND has_recovery = 0
        ORDER BY start_time DESC
        """
        
        result = fetch_all(query)
        elapsed = time.time() - start_time
        print(f"[PERFORMANCE] Failed with error query: {elapsed:.2f}s, {len(result)} rows")
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] Failed with error query after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_level3_long_running():
    """
    Fetch long-running sessions from Oracle (sessions running longer than their historical average)
    Returns: rows_list
    OPTIMIZED: Better query structure with proper hints and efficient filtering
    """
    try:
        query = """
        SELECT /*+ FIRST_ROWS(50) */
            grid_name,
            subject_area,
            workflow_name,
            session_name,
            start_time,
            current_duration_min,
            avg_duration_min
        FROM (
            SELECT 
                R.SERVER_NAME AS grid_name,
                R.SUBJECT_AREA AS subject_area,
                R.WORKFLOW_NAME AS workflow_name,
                R.INSTANCE_NAME AS session_name,
                R.START_TIME AS start_time,
                ROUND((SYSDATE - R.START_TIME) * 24 * 60) AS current_duration_min,
                AVG_DATA.AVG_RUN_DURATION_IN_MIN AS avg_duration_min
            FROM 
                INFA_PCREPO.REP_TASK_INST_RUN R
            INNER JOIN (
                SELECT /*+ PARALLEL(2) */
                    INSTANCE_NAME,
                    ROUND(AVG((END_TIME - START_TIME) * 24 * 60)) AS AVG_RUN_DURATION_IN_MIN
                FROM 
                    INFA_PCREPO.REP_TASK_INST_RUN
                WHERE 
                    END_TIME IS NOT NULL
                    AND START_TIME >= TRUNC(SYSDATE) - 7
                    AND INSTANCE_NAME IS NOT NULL
                    AND END_TIME > START_TIME
                    AND TASK_TYPE_NAME = 'Session'
                GROUP BY INSTANCE_NAME
                HAVING AVG((END_TIME - START_TIME) * 24 * 60) > 0
            ) AVG_DATA ON R.INSTANCE_NAME = AVG_DATA.INSTANCE_NAME
            WHERE 
                R.RUN_STATUS_CODE = 6
                AND R.TASK_TYPE_NAME = 'Session'
                AND R.START_TIME >= TRUNC(SYSDATE) - 2
                AND ROUND((SYSDATE - R.START_TIME) * 24 * 60) > AVG_DATA.AVG_RUN_DURATION_IN_MIN
            ORDER BY 
                current_duration_min DESC
        )
        WHERE ROWNUM <= 100
        """
        return fetch_all(query)
    except Exception as e:
        print(f"Error fetching level3 long running: {e}")
        return []


def get_mdm_job_status():
    """
    Fetch MDM job status from IICS CDI (latest run per asset)
    Returns: rows_list
    """
    try:
        query = """
        WITH latest_runs AS (
          SELECT 
            ASSET_NAME,
            START_TIME,
            END_TIME,
            STATUS,
            ROW_NUMBER() OVER (PARTITION BY ASSET_NAME ORDER BY SUBTASK_START_TIME DESC) AS row_num
          FROM MAPDQPRD.IICS_CDI_RUN_INFO
          WHERE START_TIME > TRUNC(SYSDATE)
        )
        SELECT 
          a.ASSET_NAME AS asset_name,
          r.START_TIME AS start_time,
          r.END_TIME AS end_time,
          COALESCE(r.STATUS, 'NOT STARTED') AS status
        FROM (
          SELECT 'tf_Load_MDM_Account_Master_CDW' AS ASSET_NAME FROM DUAL UNION ALL
          SELECT 'tf_Load_Billing_Account_CDW' FROM DUAL UNION ALL
          SELECT 'tf_RE_STG_TABLES' FROM DUAL UNION ALL
          SELECT 'tf_RE_RULES_200' FROM DUAL UNION ALL
          SELECT 'tf_Load_MDM_Match_B2C' FROM DUAL UNION ALL
          SELECT 'tf_RE_MDM_Load' FROM DUAL UNION ALL
          SELECT 'tf_Load_MDM_Account_Master_NRT' FROM DUAL UNION ALL
          SELECT 'tf_Load_Account_Recon_Report' FROM DUAL UNION ALL
          SELECT 'tf_Load_Mass_Market_Master' FROM DUAL UNION ALL
          SELECT 'tf_MM_CUST_DELTA_LOAD' FROM DUAL UNION ALL
          SELECT 'tf_MM_CUST_DELTA_UPDATE' FROM DUAL UNION ALL
          SELECT 'tf_MM_RECONCILE_AND_OUTBOUND' FROM DUAL UNION ALL
          SELECT 'tf_Load_MDM_Account_B2C' FROM DUAL UNION ALL
          SELECT 'tf_Load_MDM_Customer_Master' FROM DUAL UNION ALL
          SELECT 'tf_Load_Customer_Salesforce' FROM DUAL UNION ALL
          SELECT 'tf_Sync_MDM_Customer_Attr' FROM DUAL UNION ALL
          SELECT 'tf_Load_KAFKA_LOB_HIER_MDM' FROM DUAL
        ) a
        LEFT JOIN latest_runs r
          ON a.ASSET_NAME = r.ASSET_NAME AND r.row_num = 1
        ORDER BY 
          CASE COALESCE(r.STATUS, 'NOT STARTED')
            WHEN 'FAILED' THEN 1
            WHEN 'RUNNING' THEN 2
            WHEN 'SUCCESS' THEN 3
            WHEN 'NOT STARTED' THEN 4
            ELSE 5
          END
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error fetching MDM job status: {e}")
        return []


def get_erp_job_status():
    """
    Fetch ERP job status from IICS CDI (latest run per asset with timezone conversion)
    Returns: rows_list
    """
    try:
        query = """
        SELECT
            ASSET_NAME AS asset_name,
            SUBTASK_ASSET_NAME AS subtask_asset_name,
            LOCATION AS location,
            TO_CHAR(
                FROM_TZ(CAST(START_TIME AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH:MI:SS AM'
            ) AS start_time_mst,
            TO_CHAR(
                FROM_TZ(CAST(END_TIME AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH:MI:SS AM'
            ) AS end_time_mst,
            STATUS AS status
        FROM (
            SELECT
                ASSET_NAME,
                SUBTASK_ASSET_NAME,
                LOCATION,
                START_TIME,
                END_TIME,
                STATUS,
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
        WHERE RN <= 1
        ORDER BY
            CASE
                WHEN STATUS = 'FAILED' THEN 0
                WHEN STATUS IN ('SUSPENDED', 'CHILD_SUSPENDED') THEN 1
                WHEN STATUS = 'RUNNING' THEN 2
                WHEN STATUS = 'SUCCESS' THEN 3
                ELSE 4
            END,
            ASSET_NAME,
            START_TIME DESC
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error fetching ERP job status: {e}")
        return []


def get_erp_last_8_runs():
    """
    Fetch last 8 ERP runs using wkf_ERP_DAILY_REFRESH_MASTER and TASKFLOW_RUN_ID
    Returns summary of each run with status counts
    
    Status logic (using End Job marker s_m_Load_ERP_MASTER_ICSM_ENTRY_END):
      - End Job present with SUCCESS  -> run_status = 'SUCCESS' (Completed)
      - Jobs still RUNNING            -> run_status = 'RUNNING'
      - End Job NOT present            -> run_status = 'SUSPENDED'
    
    Completion time uses the End Job's END_TIME for accurate tracking.
    Also returns latest_success_end_time for reference when current run is suspended.
    """
    try:
        query = """
        WITH all_runs AS (
            SELECT DISTINCT TASKFLOW_RUN_ID
            FROM MAPDQPRD.IICS_CDI_RUN_INFO
            WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
            AND START_TIME >= SYSDATE - 7
        ),
        run_times AS (
            SELECT 
                r.TASKFLOW_RUN_ID,
                MIN(r.START_TIME) as run_start_time,
                MAX(r.END_TIME) as run_end_time,
                MAX(CASE 
                    WHEN r.SUBTASK_ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END' AND r.STATUS = 'SUCCESS'
                    THEN r.END_TIME 
                END) AS end_job_time,
                MAX(CASE 
                    WHEN r.SUBTASK_ASSET_NAME = 's_m_Load_ERP_MASTER_ICSM_ENTRY_END' AND r.STATUS = 'SUCCESS'
                    THEN 1 ELSE 0
                END) AS has_end_job
            FROM MAPDQPRD.IICS_CDI_RUN_INFO r
            WHERE r.ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
            AND r.TASKFLOW_RUN_ID IN (SELECT TASKFLOW_RUN_ID FROM all_runs)
            GROUP BY r.TASKFLOW_RUN_ID
        ),
        latest_8_runs AS (
            SELECT TASKFLOW_RUN_ID, run_start_time, run_end_time, end_job_time, has_end_job
            FROM run_times
            ORDER BY run_start_time DESC
            FETCH FIRST 8 ROWS ONLY
        ),
        latest_job_status AS (
            SELECT 
                j.TASKFLOW_RUN_ID,
                j.ASSET_NAME,
                j.SUBTASK_ASSET_NAME,
                j.STATUS,
                ROW_NUMBER() OVER (
                    PARTITION BY j.TASKFLOW_RUN_ID, COALESCE(j.SUBTASK_ASSET_NAME, j.ASSET_NAME)
                    ORDER BY j.END_TIME DESC NULLS LAST, j.START_TIME DESC
                ) AS rn
            FROM MAPDQPRD.IICS_CDI_RUN_INFO j
            INNER JOIN latest_8_runs l ON j.TASKFLOW_RUN_ID = l.TASKFLOW_RUN_ID
            WHERE (
                -- Get subtasks of the master workflow
                (j.SUBTASK_ASSET_NAME IS NOT NULL AND j.ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER')
                OR 
                -- Or get jobs from ERP locations (fallback)
                j.LOCATION IN (
                    'CDW_DSL_ERP\\Workflows',
                    'CDW_DSL_ERP\\Sessions',
                    'CDW_ASL_SAPS4\\Workflows',
                    'ASL_ERP_DATAHUB\\Workflows'
                )
            )
            AND COALESCE(j.SUBTASK_ASSET_NAME, j.ASSET_NAME) NOT LIKE '%TAX%'
        ),
        job_counts AS (
            SELECT 
                TASKFLOW_RUN_ID,
                COUNT(*) AS total_jobs,
                SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) AS succeeded,
                SUM(CASE WHEN STATUS = 'RUNNING' THEN 1 ELSE 0 END) AS running,
                SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) AS failed,
                SUM(CASE WHEN STATUS IN ('SUSPENDED', 'CHILD_SUSPENDED') THEN 1 ELSE 0 END) AS suspended
            FROM latest_job_status
            WHERE rn = 1
            GROUP BY TASKFLOW_RUN_ID
        ),
        latest_success AS (
            SELECT MAX(end_job_time) AS latest_success_end_time
            FROM run_times
            WHERE has_end_job = 1
        )
        SELECT
            TO_CHAR(
                FROM_TZ(CAST(l.run_start_time AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH12:MI AM'
            ) AS run_label,
            l.TASKFLOW_RUN_ID AS taskflow_run_id,
            l.run_start_time AS run_start_time_raw,
            TO_CHAR(
                FROM_TZ(CAST(l.run_start_time AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH12:MI:SS AM'
            ) AS start_time_mst,
            CASE
                WHEN l.has_end_job = 1 THEN
                    TO_CHAR(
                        FROM_TZ(CAST(l.end_job_time AS TIMESTAMP), 'UTC')
                        AT TIME ZONE 'America/Denver',
                        'DD-MON-YYYY HH12:MI:SS AM'
                    )
                ELSE
                    TO_CHAR(
                        FROM_TZ(CAST(l.run_end_time AS TIMESTAMP), 'UTC')
                        AT TIME ZONE 'America/Denver',
                        'DD-MON-YYYY HH12:MI:SS AM'
                    )
            END AS end_time_mst,
            CASE 
                WHEN l.has_end_job = 1 AND l.end_job_time IS NOT NULL THEN 
                    ROUND((CAST(l.end_job_time AS DATE) - CAST(l.run_start_time AS DATE)) * 24 * 60, 2)
                WHEN l.run_end_time IS NOT NULL THEN 
                    ROUND((CAST(l.run_end_time AS DATE) - CAST(l.run_start_time AS DATE)) * 24 * 60, 2)
                ELSE NULL
            END AS duration_minutes,
            240 AS sla_minutes,
            jc.total_jobs,
            jc.succeeded,
            jc.running,
            jc.failed,
            jc.suspended,
            CASE 
                WHEN COALESCE(jc.total_jobs, 0) > 0 THEN ROUND(COALESCE(jc.succeeded, 0) * 100.0 / jc.total_jobs, 1)
                ELSE 0
            END AS success_rate,
            CASE 
                -- Use End Job marker to determine completion status
                WHEN l.has_end_job = 1 THEN 'SUCCESS'
                WHEN COALESCE(jc.running, 0) > 0 THEN 'RUNNING'
                WHEN COALESCE(jc.suspended, 0) > 0 THEN 'SUSPENDED'
                WHEN l.run_end_time IS NULL THEN 'RUNNING'
                ELSE 'SUSPENDED'
            END AS run_status,
            TO_CHAR(
                FROM_TZ(CAST(ls.latest_success_end_time AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH12:MI:SS AM'
            ) AS latest_success_end_time
        FROM latest_8_runs l
        LEFT JOIN job_counts jc ON l.TASKFLOW_RUN_ID = jc.TASKFLOW_RUN_ID
        CROSS JOIN latest_success ls
        ORDER BY l.run_start_time DESC
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error fetching ERP last 8 runs: {e}")
        return []


def get_erp_current_run_details():
    """
    Fetch latest run for each ERP job (your query approach)
    Shows current status of all ERP workflows regardless of master run
    """
    try:
        query = """
        WITH latest_per_asset AS (
            SELECT
                ASSET_NAME,
                SUBTASK_ASSET_NAME,
                LOCATION,
                START_TIME,
                END_TIME,
                STATUS,
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
            AND START_TIME >= SYSDATE - 1
        ),
        subtask_counts AS (
            SELECT
                ASSET_NAME,
                COUNT(*) AS task_count
            FROM MAPDQPRD.IICS_CDI_RUN_INFO
            WHERE START_TIME >= SYSDATE - 1
            AND LOCATION IN (
                'CDW_DSL_ERP\\Workflows',
                'CDW_DSL_ERP\\Sessions',
                'CDW_ASL_SAPS4\\Workflows',
                'ASL_ERP_DATAHUB\\Workflows'
            )
            GROUP BY ASSET_NAME
        )
        SELECT
            lpa.ASSET_NAME AS asset_name,
            lpa.SUBTASK_ASSET_NAME AS subtask_asset_name,
            lpa.LOCATION AS location,
            TO_CHAR(
                FROM_TZ(CAST(lpa.START_TIME AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'HH12:MI:SS AM'
            ) AS start_time_mst,
            TO_CHAR(
                FROM_TZ(CAST(lpa.END_TIME AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'HH12:MI:SS AM'
            ) AS end_time_mst,
            lpa.STATUS AS status,
            COALESCE(sc.task_count, 1) AS subtask_count,
            ROUND(
                CASE
                    WHEN lpa.END_TIME IS NOT NULL THEN
                        (CAST(lpa.END_TIME AS DATE) - CAST(lpa.START_TIME AS DATE)) * 24 * 60
                    ELSE
                        (SYSDATE - CAST(lpa.START_TIME AS DATE)) * 24 * 60
                END,
                2
            ) AS duration_minutes
        FROM latest_per_asset lpa
        LEFT JOIN subtask_counts sc ON lpa.ASSET_NAME = sc.ASSET_NAME
        WHERE lpa.RN = 1
        ORDER BY
            CASE
                WHEN lpa.STATUS = 'FAILED' THEN 0
                WHEN lpa.STATUS IN ('SUSPENDED', 'CHILD_SUSPENDED') THEN 1
                WHEN lpa.STATUS = 'RUNNING' THEN 2
                WHEN lpa.STATUS = 'SUCCESS' THEN 3
                ELSE 4
            END,
            lpa.START_TIME DESC,
            lpa.ASSET_NAME
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error fetching ERP current run details: {e}")
        return []


def get_adf_run_status():
    """
    Fetch ADF run status (second latest run per job for today)
    Returns: rows_list
    """
    try:
        query = """
        WITH RankedJobs AS (
            SELECT 
                job_name,
                resource_type,
                start_time,
                end_time,
                job_status,
                error_message,
                ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY start_time DESC) AS rn
            FROM asl.metadata_framework.ingestion_log
            WHERE start_time >= TRUNC(SYSDATE)
              AND start_time < TRUNC(SYSDATE) + 1
              AND resource_type = 'ADF'
        )
        SELECT 
            job_name,
            resource_type,
            start_time,
            end_time,
            job_status,
            error_message
        FROM RankedJobs
        WHERE rn = 2
        ORDER BY job_status DESC
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error fetching ADF run status: {e}")
        return []


def get_adf_failed_jobs():
    """
    Fetch ADF failed jobs (latest failed run per job for today)
    Returns: rows_list
    """
    try:
        query = """
        WITH RankedJobs AS (
            SELECT 
                job_name,
                resource_type,
                start_time,
                end_time,
                job_status,
                error_message,
                ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY start_time DESC) AS rn
            FROM asl.metadata_framework.ingestion_log
            WHERE start_time >= TRUNC(SYSDATE)
              AND start_time < TRUNC(SYSDATE) + 1
              AND job_status = 'Failed'
        )
        SELECT 
            job_name,
            resource_type,
            start_time,
            end_time,
            job_status,
            error_message
        FROM RankedJobs
        WHERE rn = 1
        ORDER BY job_status DESC
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error fetching ADF failed jobs: {e}")
        return []


def get_level3_all_jobs_status():
    """
    Fetch ALL Level3 job statuses from INFA_PCREPO.REP_TASK_INST_RUN
    Returns: (summary_dict, rows_list) 
    
    Shows ALL records from today, sorted by start_time DESC (latest first).
    """
    import time
    start_time = time.time()
    
    try:
        # Fast query - get all records from today, sorted by start_time DESC
        # No expensive calculations or window functions
        query = """
        SELECT
            TIR.SUBJECT_AREA AS folder,
            TIR.WORKFLOW_NAME AS workflow_name,
            TIR.INSTANCE_NAME AS session_name,
            TO_CHAR(TIR.START_TIME, 'YYYY-MM-DD HH24:MI:SS') AS sess_start_time,
            TO_CHAR(TIR.END_TIME, 'YYYY-MM-DD HH24:MI:SS') AS sess_end_time,
            CASE 
                WHEN TIR.RUN_STATUS_CODE = 1 THEN 'Succeeded'
                WHEN TIR.RUN_STATUS_CODE = 3 THEN 'Failed'
                WHEN TIR.RUN_STATUS_CODE = 4 THEN 'Stopped'
                WHEN TIR.RUN_STATUS_CODE = 5 THEN 'Aborted'
                WHEN TIR.RUN_STATUS_CODE = 6 THEN 'Running'
                WHEN TIR.RUN_STATUS_CODE = 15 THEN 'Terminated'
                ELSE 'Other'
            END AS status,
            CASE 
                WHEN TIR.END_TIME IS NOT NULL AND TIR.START_TIME IS NOT NULL THEN
                    LPAD(TRUNC((TIR.END_TIME - TIR.START_TIME) * 24), 2, '0') || ':' ||
                    LPAD(TRUNC(MOD((TIR.END_TIME - TIR.START_TIME) * 24 * 60, 60)), 2, '0') || ':' ||
                    LPAD(TRUNC(MOD((TIR.END_TIME - TIR.START_TIME) * 24 * 60 * 60, 60)), 2, '0')
                ELSE NULL
            END AS duration_in_mins
        FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
        WHERE TIR.TASK_TYPE_NAME = 'Session'
          AND TIR.START_TIME >= TRUNC(SYSDATE)
          AND TIR.START_TIME < TRUNC(SYSDATE) + 1
          AND TIR.RUN_STATUS_CODE != 2
        ORDER BY TIR.START_TIME DESC
        """
        rows = fetch_all(query)
        elapsed = time.time() - start_time
        print(f"[PERFORMANCE] All jobs status query: {elapsed:.2f}s, {len(rows)} rows")
        
        # Compute summary from data
        total_succeeded = sum(1 for r in rows if r.get("status") == "Succeeded")
        total_failed = sum(1 for r in rows if r.get("status") in ["Failed", "Stopped", "Aborted", "Terminated"])
        total_running = sum(1 for r in rows if r.get("status") == "Running")
        total_other = len(rows) - (total_succeeded + total_failed + total_running)
        
        summary = {
            "total_jobs": len(rows),
            "total_succeeded": total_succeeded,
            "total_failed": total_failed,
            "total_running": total_running,
            "total_other": total_other,
        }
        
        return summary, rows
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] All jobs status query after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        # RE-RAISE so API can fallback to mock data
        raise


def get_level3_jobs_summary():
    """
    Fetch Level3 job status summary from REP_SESS_LOG for today
    Returns: dict with status counts
    """
    try:
        query = """
        SELECT 
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
                   15, 'Terminated') AS status,
            COUNT(*) AS count
        FROM INFA_PCREPO.REP_SESS_LOG
        WHERE ACTUAL_START >= TRUNC(SYSDATE)
          AND ACTUAL_START < TRUNC(SYSDATE) + 1
        GROUP BY RUN_STATUS_CODE
        ORDER BY DECODE(RUN_STATUS_CODE,
                        3, 1,  -- Failed first
                        4, 2,  -- Stopped
                        5, 3,  -- Aborted
                        15, 4, -- Terminated
                        6, 5,  -- Running
                        1, 6,  -- Succeeded
                        99)    -- Others last
        """
        rows = fetch_all(query)
        
        # Organize data for easy display
        summary = {
            "succeeded": 0,
            "failed": 0,
            "running": 0,
            "stopped": 0,
            "other": 0,
            "total": 0,
            "details": []
        }
        
        for row in rows:
            status = str(row.get("status", "")).lower()
            count = row.get("count", 0)
            summary["total"] += count
            
            if status == "succeeded":
                summary["succeeded"] = count
            elif status == "failed":
                summary["failed"] = count
            elif status == "running":
                summary["running"] = count
            elif status in ["stopped", "aborted", "terminated"]:
                summary["stopped"] += count
            else:
                summary["other"] += count
            
            summary["details"].append({
                "status": row.get("status", "Unknown"),
                "count": count
            })
        
        return summary
    except Exception as e:
        print(f"Error fetching level3 jobs summary: {e}")
        return {
            "succeeded": 0,
            "failed": 0,
            "running": 0,
            "stopped": 0,
            "other": 0,
            "total": 0,
            "details": []
        }


def get_level3_jobs_today_only():
    """
    Fast query for TODAY's job status only
    Returns: Dictionary with today's stats
    """
    try:
        query = """
        SELECT 
            COUNT(*) AS total_jobs,
            SUM(CASE WHEN run_status_code = 1 THEN 1 ELSE 0 END) AS succeeded,
            SUM(CASE WHEN run_status_code IN (3, 4, 15) THEN 1 ELSE 0 END) AS failed,
            SUM(CASE WHEN run_status_code = 6 THEN 1 ELSE 0 END) AS running,
            SUM(CASE WHEN run_status_code = 7 THEN 1 ELSE 0 END) AS stopped,
            SUM(CASE WHEN run_status_code = 8 THEN 1 ELSE 0 END) AS disabled
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE task_type_name = 'Session'
          AND start_time >= TRUNC(SYSDATE)
          AND start_time < TRUNC(SYSDATE) + 1
        """
        
        rows = fetch_all(query)
        if rows and len(rows) > 0:
            row = rows[0]
            from datetime import datetime
            return {
                'date': datetime.now().date(),
                'is_today': True,
                'total': int(row.get('total_jobs', 0)),
                'succeeded': int(row.get('succeeded', 0)),
                'failed': int(row.get('failed', 0)),
                'running': int(row.get('running', 0)),
                'stopped': int(row.get('stopped', 0)),
                'disabled': int(row.get('disabled', 0))
            }
        else:
            from datetime import datetime
            return {
                'date': datetime.now().date(),
                'is_today': True,
                'total': 0,
                'succeeded': 0,
                'failed': 0,
                'running': 0,
                'stopped': 0,
                'disabled': 0
            }
        
    except Exception as e:
        print(f"Error fetching today's job data: {e}")
        import traceback
        traceback.print_exc()
        from datetime import datetime
        return {
            'date': datetime.now().date(),
            'is_today': True,
            'total': 0,
            'succeeded': 0,
            'failed': 0,
            'running': 0,
            'stopped': 0,
            'disabled': 0
        }


def get_level3_jobs_single_day(days_ago=1):
    """
    Fast query for a single historical day
    Args:
        days_ago: Number of days before today (1 = yesterday, 2 = 2 days ago, etc.)
    Returns: Dictionary with that day's stats
    """
    try:
        query = """
        SELECT 
            TRUNC(SYSDATE) - :days_ago AS job_date,
            COUNT(*) AS total_jobs,
            SUM(CASE WHEN run_status_code = 1 THEN 1 ELSE 0 END) AS succeeded,
            SUM(CASE WHEN run_status_code IN (3, 4, 15) THEN 1 ELSE 0 END) AS failed,
            SUM(CASE WHEN run_status_code = 6 THEN 1 ELSE 0 END) AS running,
            SUM(CASE WHEN run_status_code = 7 THEN 1 ELSE 0 END) AS stopped,
            SUM(CASE WHEN run_status_code = 8 THEN 1 ELSE 0 END) AS disabled
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE task_type_name = 'Session'
          AND start_time >= TRUNC(SYSDATE) - :days_ago
          AND start_time < TRUNC(SYSDATE) - :days_ago + 1
        GROUP BY TRUNC(SYSDATE) - :days_ago
        """
        
        rows = fetch_all(query, {"days_ago": days_ago})
        if rows and len(rows) > 0:
            row = rows[0]
            from datetime import datetime, timedelta
            return {
                'date': (datetime.now() - timedelta(days=days_ago)).date(),
                'is_today': False,
                'total': int(row.get('total_jobs', 0)),
                'succeeded': int(row.get('succeeded', 0)),
                'failed': int(row.get('failed', 0)),
                'running': int(row.get('running', 0)),
                'stopped': int(row.get('stopped', 0)),
                'disabled': int(row.get('disabled', 0))
            }
        else:
            from datetime import datetime, timedelta
            return {
                'date': (datetime.now() - timedelta(days=days_ago)).date(),
                'is_today': False,
                'total': 0,
                'succeeded': 0,
                'failed': 0,
                'running': 0,
                'stopped': 0,
                'disabled': 0
            }
        
    except Exception as e:
        print(f"Error fetching job data for {days_ago} days ago: {e}")
        import traceback
        traceback.print_exc()
        from datetime import datetime, timedelta
        return {
            'date': (datetime.now() - timedelta(days=days_ago)).date(),
            'is_today': False,
            'total': 0,
            'succeeded': 0,
            'failed': 0,
            'running': 0,
            'stopped': 0,
            'disabled': 0
        }


def get_level3_jobs_last_7_days_optimized():
    """
    Fetch job status for last 7 days using SINGLE optimized query
    Returns: List of daily summaries [today, yesterday, ..., 6 days ago]
    OPTIMIZED: Single query with parallel hint instead of 7 separate queries
    """
    import time
    start = time.time()
    
    try:
        # SINGLE QUERY for all 7 days - MUCH faster than 7 separate queries!
        query = """
        SELECT /*+ PARALLEL(4) */
            TRUNC(start_time) AS job_date,
            COUNT(*) AS total_jobs,
            SUM(CASE WHEN run_status_code = 1 THEN 1 ELSE 0 END) AS succeeded,
            SUM(CASE WHEN run_status_code IN (3, 4, 15) THEN 1 ELSE 0 END) AS failed,
            SUM(CASE WHEN run_status_code = 6 THEN 1 ELSE 0 END) AS running,
            SUM(CASE WHEN run_status_code = 7 THEN 1 ELSE 0 END) AS stopped,
            SUM(CASE WHEN run_status_code = 8 THEN 1 ELSE 0 END) AS disabled
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE task_type_name = 'Session'
          AND TRUNC(start_time) >= TRUNC(SYSDATE) - 6
          AND TRUNC(start_time) <= TRUNC(SYSDATE)
        GROUP BY TRUNC(start_time)
        ORDER BY TRUNC(start_time) DESC
        """
        
        rows = fetch_all(query)
        
        # Convert to list format (today to 6 days ago)
        from datetime import datetime, timedelta
        results = []
        
        # Create a map of date -> data for quick lookup
        data_map = {}
        for row in rows:
            job_date = row.get('job_date')
            if isinstance(job_date, str):
                from datetime import datetime
                job_date = datetime.strptime(job_date, '%Y-%m-%d').date()
            elif hasattr(job_date, 'date'):
                job_date = job_date.date()
            
            data_map[job_date] = {
                'date': job_date,
                'is_today': job_date == datetime.now().date(),
                'total': int(row.get('total_jobs', 0)),
                'succeeded': int(row.get('succeeded', 0)),
                'failed': int(row.get('failed', 0)),
                'running': int(row.get('running', 0)),
                'stopped': int(row.get('stopped', 0)),
                'disabled': int(row.get('disabled', 0))
            }
        
        # Fill in all 7 days (today to 6 days ago) even if no data
        for days_ago in range(0, 7):
            target_date = (datetime.now() - timedelta(days=days_ago)).date()
            if target_date in data_map:
                results.append(data_map[target_date])
            else:
                results.append({
                    'date': target_date,
                    'is_today': days_ago == 0,
                    'total': 0,
                    'succeeded': 0,
                    'failed': 0,
                    'running': 0,
                    'stopped': 0,
                    'disabled': 0
                })
        
        elapsed = time.time() - start
        print(f"[PERFORMANCE] 7-day stats fetched in {elapsed:.2f} seconds using SINGLE query (was 7 queries)")
        
        return results
        
    except Exception as e:
        print(f"Error fetching 7-day job stats: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty data for 7 days
        from datetime import datetime, timedelta
        return [
            {
                'date': (datetime.now() - timedelta(days=i)).date(),
                'is_today': i == 0,
                'total': 0,
                'succeeded': 0,
                'failed': 0,
                'running': 0,
                'stopped': 0,
                'disabled': 0
            }
            for i in range(0, 7)
        ]


def get_level3_jobs_by_date(target_date):
    """
    Fetch detailed job list for a specific date
    Args:
        target_date: datetime.date object
    Returns: List of job details
    """
    try:
        query = """
        SELECT 
            grid_name,
            subject_area,
            workflow_name,
            session_name,
            start_time,
            end_time,
            status,
            duration_min
        FROM (
            SELECT 
                SERVER_NAME AS grid_name,
                SUBJECT_AREA AS subject_area,
                WORKFLOW_NAME AS workflow_name,
                INSTANCE_NAME AS session_name,
                START_TIME AS start_time,
                END_TIME AS end_time,
                CASE 
                    WHEN RUN_STATUS_CODE = 1 THEN 'Completed'
                    WHEN RUN_STATUS_CODE = 3 THEN 'Failed'
                    WHEN RUN_STATUS_CODE = 4 THEN 'Stopped'
                    WHEN RUN_STATUS_CODE = 6 THEN 'Running'
                    WHEN RUN_STATUS_CODE = 15 THEN 'Terminated'
                    ELSE 'Other'
                END AS status,
                ROUND(NVL((END_TIME - START_TIME) * 24 * 60, (SYSDATE - START_TIME) * 24 * 60), 2) AS duration_min,
                RUN_STATUS_CODE
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE TASK_TYPE_NAME = 'Session'
              AND TRUNC(START_TIME) = TO_DATE(:target_date, 'YYYY-MM-DD')
        )
        ORDER BY 
            CASE WHEN RUN_STATUS_CODE IN (3, 4, 15) THEN 1 ELSE 2 END,
            start_time DESC
        """
        
        from datetime import datetime
        if isinstance(target_date, datetime):
            target_date = target_date.date()
        
        date_str = target_date.strftime('%Y-%m-%d')
        
        return fetch_all(query, {"target_date": date_str})
        
    except Exception as e:
        print(f"Error fetching jobs for date {target_date}: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_level3_failed_jobs_status():
    """
    Fetch comprehensive failed jobs status with restart tracking.
    OPTIMIZED: Single combined query instead of 5 separate queries.
    Performance: ~10-15 seconds instead of 90+ seconds.
    
    Returns: (summary_dict, failed_jobs_list)
    
    Summary includes:
        - total_failed: Total number of failed sessions
        - completed_after_restart: Sessions that failed, restarted, and completed
        - pending_jobs: Failed sessions not yet restarted
        - restarted_running: Restarted sessions currently running
    """
    try:
        import time
        start_time = time.time()
        
        # OPTIMIZED: Single query that gets failed jobs + computes all summary counts
        # No redundant table scans - everything in one pass
        combined_query = """
        WITH failed_sessions AS (
            SELECT 
                TIR.SERVER_NAME AS grid_name,
                TIR.SUBJECT_AREA AS subject_area,
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
                END AS status,
                COMP.MAX_COMPLETED_TIME AS last_comp_time,
                CASE 
                    WHEN COMP.MAX_COMPLETED_TIME IS NOT NULL 
                    THEN TRUNC(SYSDATE) - TRUNC(COMP.MAX_COMPLETED_TIME)
                    ELSE NULL
                END AS failded_days_count,
                CASE 
                    WHEN MAX(CASE WHEN HAS_RUN.HAS_SUCCESS = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY TIR.INSTANCE_NAME) = 1 THEN 'completed'
                    WHEN MAX(CASE WHEN HAS_RUN.HAS_RUNNING = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY TIR.INSTANCE_NAME) = 1 THEN 'running'
                    ELSE 'pending'
                END AS status_type,
                ROW_NUMBER() OVER (PARTITION BY TIR.INSTANCE_NAME ORDER BY TIR.START_TIME DESC) AS rn
            FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
            LEFT JOIN (
                SELECT 
                    INSTANCE_NAME,
                    MAX(END_TIME) AS MAX_COMPLETED_TIME
                FROM INFA_PCREPO.REP_TASK_INST_RUN
                WHERE RUN_STATUS_CODE = 1
                AND TASK_TYPE_NAME = 'Session'
                GROUP BY INSTANCE_NAME
            ) COMP ON TIR.INSTANCE_NAME = COMP.INSTANCE_NAME
            LEFT JOIN (
                SELECT DISTINCT
                    INSTANCE_NAME,
                    MAX(CASE WHEN RUN_STATUS_CODE = 1 THEN 1 ELSE 0 END) AS HAS_SUCCESS,
                    MAX(CASE WHEN RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) AS HAS_RUNNING
                FROM INFA_PCREPO.REP_TASK_INST_RUN
                WHERE TASK_TYPE_NAME = 'Session'
                AND START_TIME >= TRUNC(SYSDATE)
                AND START_TIME < TRUNC(SYSDATE) + 1
                GROUP BY INSTANCE_NAME
            ) HAS_RUN ON TIR.INSTANCE_NAME = HAS_RUN.INSTANCE_NAME
            WHERE TIR.TASK_TYPE_NAME = 'Session'
            AND TIR.START_TIME >= TRUNC(SYSDATE)
            AND TIR.START_TIME < TRUNC(SYSDATE) + 1
            AND TIR.RUN_STATUS_CODE IN (3, 4, 5, 15)
            AND TIR.INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
        ),
        latest_failures AS (
            SELECT * FROM failed_sessions WHERE rn = 1
        )
        SELECT * FROM latest_failures ORDER BY start_time DESC
        """
        
        failed_jobs = fetch_all(combined_query)
        elapsed = time.time() - start_time
        print(f"[PERFORMANCE] Combined failed jobs query: {elapsed:.2f}s, {len(failed_jobs)} rows")
        
        # Compute summary from the results (no additional DB queries)
        total_failed = len(failed_jobs)
        completed_after_restart = sum(1 for row in failed_jobs if row.get('status_type') == 'completed')
        pending_jobs = sum(1 for row in failed_jobs if row.get('status_type') == 'pending')
        restarted_running = sum(1 for row in failed_jobs if row.get('status_type') == 'running')
        
        # FILTER: Only display pending jobs in the table
        # Keep summary counts for all statuses, but show only pending in table
        pending_failed_jobs = [row for row in failed_jobs if row.get('status_type') == 'pending']
        
        summary = {
            'total_failed': total_failed,
            'completed_after_restart': completed_after_restart,
            'pending_jobs': pending_jobs,
            'restarted_running': restarted_running
        }
        
        print(f"[PERFORMANCE] Summary: {summary} | Displaying {len(pending_failed_jobs)} pending jobs")
        
        return summary, pending_failed_jobs
        
    except Exception as e:
        print(f"Error fetching Level3 failed jobs status: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_failed': 0,
            'completed_after_restart': 0,
            'pending_jobs': 0,
            'restarted_running': 0
        }, []


def get_all_failed_jobs_status_details(status_filter=None):
    """
    Fetch ALL failed jobs details with status type classification.
    Can filter by status_type: 'total', 'completed', 'pending', 'running'
    
    Returns: list of failed job records with status_type field
    """
    try:
        # Same query as get_level3_failed_jobs_status() but returns ALL jobs
        combined_query = """
        WITH failed_sessions AS (
            SELECT 
                TIR.SERVER_NAME AS grid_name,
                TIR.SUBJECT_AREA AS subject_area,
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
                END AS status,
                COMP.MAX_COMPLETED_TIME AS last_comp_time,
                CASE 
                    WHEN COMP.MAX_COMPLETED_TIME IS NOT NULL 
                    THEN TRUNC(SYSDATE) - TRUNC(COMP.MAX_COMPLETED_TIME)
                    ELSE NULL
                END AS failded_days_count,
                CASE 
                    WHEN MAX(CASE WHEN HAS_RUN.HAS_SUCCESS = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY TIR.INSTANCE_NAME) = 1 THEN 'completed'
                    WHEN MAX(CASE WHEN HAS_RUN.HAS_RUNNING = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY TIR.INSTANCE_NAME) = 1 THEN 'running'
                    ELSE 'pending'
                END AS status_type,
                ROW_NUMBER() OVER (PARTITION BY TIR.INSTANCE_NAME ORDER BY TIR.START_TIME DESC) AS rn
            FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
            LEFT JOIN (
                SELECT 
                    INSTANCE_NAME,
                    MAX(END_TIME) AS MAX_COMPLETED_TIME
                FROM INFA_PCREPO.REP_TASK_INST_RUN
                WHERE RUN_STATUS_CODE = 1
                AND TASK_TYPE_NAME = 'Session'
                GROUP BY INSTANCE_NAME
            ) COMP ON TIR.INSTANCE_NAME = COMP.INSTANCE_NAME
            LEFT JOIN (
                SELECT DISTINCT
                    INSTANCE_NAME,
                    MAX(CASE WHEN RUN_STATUS_CODE = 1 THEN 1 ELSE 0 END) AS HAS_SUCCESS,
                    MAX(CASE WHEN RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) AS HAS_RUNNING
                FROM INFA_PCREPO.REP_TASK_INST_RUN
                WHERE TASK_TYPE_NAME = 'Session'
                AND START_TIME >= TRUNC(SYSDATE)
                AND START_TIME < TRUNC(SYSDATE) + 1
                GROUP BY INSTANCE_NAME
            ) HAS_RUN ON TIR.INSTANCE_NAME = HAS_RUN.INSTANCE_NAME
            WHERE TIR.TASK_TYPE_NAME = 'Session'
            AND TIR.START_TIME >= TRUNC(SYSDATE)
            AND TIR.START_TIME < TRUNC(SYSDATE) + 1
            AND TIR.RUN_STATUS_CODE IN (3, 4, 5, 15)
            AND TIR.INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
        ),
        latest_failures AS (
            SELECT * FROM failed_sessions WHERE rn = 1
        )
        SELECT * FROM latest_failures ORDER BY start_time DESC
        """
        
        failed_jobs = fetch_all(combined_query)
        
        # Filter by status_type if specified
        if status_filter and status_filter.lower() in ['completed', 'pending', 'running']:
            filtered_jobs = [row for row in failed_jobs if row.get('status_type') == status_filter.lower()]
            return filtered_jobs
        
        # Return all jobs
        return failed_jobs if failed_jobs else []
        
    except Exception as e:
        print(f"Error fetching failed jobs status details: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_level3_folders_with_metrics():
    """
    Get list of folders (SUBJECT_AREA) with 7-day job metrics.
    Returns folders that had failed jobs in the last 7 days.
    """
    try:
        query = """
        SELECT 
            SUBJECT_AREA,
            COUNT(*) AS job_count,
            SUM(CASE WHEN RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1 ELSE 0 END) AS failed_count,
            SUM(CASE WHEN RUN_STATUS_CODE = 1 THEN 1 ELSE 0 END) AS success_count,
            SUM(CASE WHEN RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) AS running_count
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE TASK_TYPE_NAME = 'Session'
        AND START_TIME >= TRUNC(SYSDATE) - 7
        AND START_TIME < TRUNC(SYSDATE) + 1
        AND SUBJECT_AREA IS NOT NULL
        GROUP BY SUBJECT_AREA
        HAVING SUM(CASE WHEN RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1 ELSE 0 END) > 0
        ORDER BY failed_count DESC, SUBJECT_AREA
        """
        
        folders = fetch_all(query)
        print(f"[DEBUG] Found {len(folders)} folders with failed jobs in last 7 days")
        return folders
        
    except Exception as e:
        print(f"Error fetching Level3 folders: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_level3_jobs_by_folder_7_days(folder_name):
    """
    Get 7-day job statistics for a specific folder.
    Same format as get_level3_jobs_last_7_days_optimized but filtered by folder.
    """
    try:
        query = """
        SELECT 
            TRUNC(START_TIME) AS run_date,
            SUM(CASE WHEN RUN_STATUS_CODE = 1 THEN 1 ELSE 0 END) AS succeeded,
            SUM(CASE WHEN RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1 ELSE 0 END) AS failed,
            SUM(CASE WHEN RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) AS running,
            SUM(CASE WHEN RUN_STATUS_CODE = 2 THEN 1 ELSE 0 END) AS stopped,
            SUM(CASE WHEN RUN_STATUS_CODE = 7 THEN 1 ELSE 0 END) AS disabled,
            COUNT(*) AS total
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE TASK_TYPE_NAME = 'Session'
        AND START_TIME >= TRUNC(SYSDATE) - 6
        AND START_TIME < TRUNC(SYSDATE) + 1
        AND SUBJECT_AREA = :folder_name
        GROUP BY TRUNC(START_TIME)
        ORDER BY run_date DESC
        """
        
        results = fetch_all(query, {'folder_name': folder_name})
        
        # Convert to list of dicts with date objects
        daily_stats = []
        for row in results:
            daily_stats.append({
                'date': row.get('run_date'),
                'succeeded': row.get('succeeded', 0),
                'failed': row.get('failed', 0),
                'running': row.get('running', 0),
                'stopped': row.get('stopped', 0),
                'disabled': row.get('disabled', 0),
                'total': row.get('total', 0),
            })
        
        print(f"[DEBUG] Folder '{folder_name}': {len(daily_stats)} days of data")
        return daily_stats
        
    except Exception as e:
        print(f"Error fetching Level3 jobs by folder: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_erp_long_running_sessions():
    """
    Identify ERP workflows/subtasks that are currently RUNNING longer than their average runtime.
    Focuses on workflows with subtasks only from the current run.
    Compares current duration against 10-day average.
    Returns only RUNNING sessions that exceed their average runtime.
    """
    try:
        query = """
        WITH current_master AS (
            -- Get the latest master workflow run to identify current run
            SELECT 
                TASKFLOW_RUN_ID
            FROM MAPDQPRD.IICS_CDI_RUN_INFO
            WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
            AND START_TIME >= SYSDATE - 1
            ORDER BY START_TIME DESC
            FETCH FIRST 1 ROW ONLY
        ),
        historical_avg AS (
            -- Calculate 10-day average runtime per subtask
            SELECT
                SUBTASK_ASSET_NAME,
                AVG(SUBTASK_DURATION / 60) AS avg_duration_minutes,
                COUNT(*) AS run_count,
                MIN(SUBTASK_DURATION / 60) AS min_duration_minutes,
                MAX(SUBTASK_DURATION / 60) AS max_duration_minutes
            FROM MAPDQPRD.IICS_CDI_RUN_INFO
            WHERE LOCATION IN (
                'CDW_DSL_ERP\\Workflows',
                'CDW_DSL_ERP\\Sessions', 
                'CDW_ASL_SAPS4\\Workflows',
                'ASL_ERP_DATAHUB\\Workflows'
            )
            AND SUBTASK_ASSET_NAME IS NOT NULL
            AND SUBTASK_END_TIME IS NOT NULL  -- Only completed runs for avg
            AND SUBTASK_START_TIME >= SYSDATE - 10  -- Last 10 days
            AND STATUS = 'SUCCESS'  -- Only successful runs for baseline
            GROUP BY SUBTASK_ASSET_NAME
            HAVING COUNT(*) >= 3  -- Need at least 3 runs for meaningful average
        ),
        current_runs AS (
            -- Get currently RUNNING sessions only from current TASKFLOW_RUN_ID
            SELECT
                j.ASSET_NAME,
                j.SUBTASK_ASSET_NAME,
                j.LOCATION,
                j.SUBTASK_START_TIME,
                j.SUBTASK_END_TIME,
                j.STATUS,
                ROUND((SYSDATE - j.SUBTASK_START_TIME) * 24 * 60, 2) AS current_duration_minutes
            FROM MAPDQPRD.IICS_CDI_RUN_INFO j
            INNER JOIN current_master cm ON j.TASKFLOW_RUN_ID = cm.TASKFLOW_RUN_ID
            WHERE j.LOCATION IN (
                'CDW_DSL_ERP\\Workflows',
                'CDW_DSL_ERP\\Sessions',
                'CDW_ASL_SAPS4\\Workflows',
                'ASL_ERP_DATAHUB\\Workflows'
            )
            AND j.SUBTASK_ASSET_NAME IS NOT NULL
            AND j.STATUS = 'RUNNING'  -- Only currently running sessions
        )
        SELECT
            cr.ASSET_NAME AS asset_name,
            cr.SUBTASK_ASSET_NAME AS subtask_name,
            cr.LOCATION AS location,
            TO_CHAR(
                FROM_TZ(CAST(cr.SUBTASK_START_TIME AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'MM/DD/YYYY HH12:MI:SS AM'
            ) AS start_time_mst,
            TO_CHAR(
                FROM_TZ(CAST(cr.SUBTASK_END_TIME AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'MM/DD/YYYY HH12:MI:SS AM'
            ) AS end_time_mst,
            cr.STATUS AS status,
            cr.current_duration_minutes,
            ha.avg_duration_minutes,
            ha.min_duration_minutes,
            ha.max_duration_minutes,
            ha.run_count AS historical_count,
            ROUND((cr.current_duration_minutes / ha.avg_duration_minutes), 2) AS ratio_to_avg,
            ROUND((cr.current_duration_minutes - ha.avg_duration_minutes), 2) AS minutes_over_avg
        FROM current_runs cr
        INNER JOIN historical_avg ha ON cr.SUBTASK_ASSET_NAME = ha.SUBTASK_ASSET_NAME
        WHERE cr.current_duration_minutes > ha.avg_duration_minutes  -- Only if exceeding average
        ORDER BY 
            cr.current_duration_minutes DESC,
            (cr.current_duration_minutes - ha.avg_duration_minutes) DESC
        """
        
        results = fetch_all_mapdqprd(query)
        print(f"[DEBUG] Found {len(results)} long-running ERP sessions")
        return results
        
    except Exception as e:
        print(f"Error fetching ERP long-running sessions: {e}")
        import traceback
        traceback.print_exc()
        return []


# ===================================
# LEVEL3 TODAY JOB DETAILS (New)
# ===================================

def get_today_all_job_details():
    """
    Fetch ALL job details for today from INFA_PCREPO.REP_SESS_LOG
    Returns: list of job records
    """
    try:
        query = """
        SELECT 
            SUBJECT_AREA AS FOLDER,
            WORKFLOW_NAME,
            SESSION_NAME,
            TRUNC(ACTUAL_START) AS LOAD_DATE,
            TO_CHAR(ACTUAL_START, 'HH12:MI:SS AM') AS SESS_START_TIME,
            TO_CHAR(SESSION_TIMESTAMP, 'HH12:MI:SS AM') AS SESS_END_TIME,
            TO_CHAR(
                TO_DATE('1970-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
                + (SESSION_TIMESTAMP - ACTUAL_START),
                'HH24:MI:SS'
            ) AS DURATION_IN_MINS,
            SUCCESSFUL_SOURCE_ROWS AS SOURCE_SUCCESS_ROWS,
            SUCCESSFUL_ROWS AS TARGET_SUCCESS_ROWS,
            LAST_ERROR AS ERROR_MESSAGE,
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
                15, 'Terminated',
                'Unknown'
            ) AS STATUS,
            FAILED_ROWS,
            FAILED_SOURCE_ROWS
        FROM INFA_PCREPO.REP_SESS_LOG
        WHERE TRUNC(ACTUAL_START) = TRUNC(SYSDATE)
        ORDER BY ACTUAL_START DESC
        """
        
        results = fetch_all(query)
        return results if results else []
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch all job details: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_today_succeeded_job_details(limit=2000):
    """
    Fetch SUCCEEDED job details for today from INFA_PCREPO.REP_SESS_LOG
    Returns: list of succeeded job records (limited to 2000)
    """
    try:
        query = f"""
        SELECT * FROM (
            SELECT 
                SUBJECT_AREA AS FOLDER,
                WORKFLOW_NAME,
                SESSION_NAME,
                TO_CHAR(ACTUAL_START, 'HH12:MI:SS AM') AS SESS_START_TIME,
                TO_CHAR(SESSION_TIMESTAMP, 'HH12:MI:SS AM') AS SESS_END_TIME,
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
                    15, 'Terminated',
                    'Unknown'
                ) AS STATUS,
                ROW_NUMBER() OVER (ORDER BY ACTUAL_START DESC) AS rn
            FROM INFA_PCREPO.REP_SESS_LOG
            WHERE TRUNC(ACTUAL_START) = TRUNC(SYSDATE)
              AND RUN_STATUS_CODE = 1
        )
        WHERE rn <= {limit}
        ORDER BY SESS_START_TIME DESC
        """
        
        results = fetch_all(query)
        return results if results else []
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch succeeded job details: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_today_failed_job_details(limit=1000):
    """
    Fetch FAILED job details for today from INFA_PCREPO.REP_SESS_LOG
    Returns: list of failed job records (status codes 3,4,7,8 - limited to 1000)
    """
    try:
        query = f"""
        SELECT * FROM (
            SELECT 
                SUBJECT_AREA AS FOLDER,
                WORKFLOW_NAME,
                SESSION_NAME,
                TO_CHAR(ACTUAL_START, 'HH12:MI:SS AM') AS SESS_START_TIME,
                TO_CHAR(SESSION_TIMESTAMP, 'HH12:MI:SS AM') AS SESS_END_TIME,
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
                    15, 'Terminated',
                    'Unknown'
                ) AS STATUS,
                LAST_ERROR AS ERROR_MESSAGE,
                ROW_NUMBER() OVER (ORDER BY ACTUAL_START DESC) AS rn
            FROM INFA_PCREPO.REP_SESS_LOG
            WHERE TRUNC(ACTUAL_START) = TRUNC(SYSDATE)
              AND RUN_STATUS_CODE IN (3, 4, 7, 8)
        )
        WHERE rn <= {limit}
        ORDER BY SESS_START_TIME DESC
        """
        
        results = fetch_all(query)
        return results if results else []
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch failed job details: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_today_running_job_details(limit=1000):
    """
    Fetch RUNNING job details for today from INFA_PCREPO.REP_SESS_LOG
    Returns: list of running job records (limited to 1000)
    Note: No end time or error message for running sessions
    """
    try:
        query = f"""
        SELECT * FROM (
            SELECT 
                SUBJECT_AREA AS FOLDER,
                WORKFLOW_NAME,
                SESSION_NAME,
                TO_CHAR(ACTUAL_START, 'HH12:MI:SS AM') AS SESS_START_TIME,
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
                    15, 'Terminated',
                    'Unknown'
                ) AS STATUS,
                ROW_NUMBER() OVER (ORDER BY ACTUAL_START DESC) AS rn
            FROM INFA_PCREPO.REP_SESS_LOG
            WHERE TRUNC(ACTUAL_START) = TRUNC(SYSDATE)
              AND RUN_STATUS_CODE = 6
        )
        WHERE rn <= {limit}
        ORDER BY SESS_START_TIME DESC
        """
        
        results = fetch_all(query)
        return results if results else []
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch running job details: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_last_6_days_historical():
    """
    Fetch last 6 days historical job summary with counts and rates
    Returns: list of dicts with date, day, completed, failed, running, total, success_rate, failure_rate
    """
    try:
        query = """
        SELECT 
            DATE_VAL,
            TO_CHAR(DATE_VAL, 'fmDay') AS DAY_NAME,
            SUM(SUCCEEDED_COUNT) AS COMPLETED,
            SUM(FAILED_COUNT) AS FAILED,
            SUM(RUNNING_COUNT) AS RUNNING,
            SUM(TOTAL_COUNT) AS TOTAL,
            ROUND(SUM(SUCCEEDED_COUNT) * 100.0 / NULLIF(SUM(TOTAL_COUNT), 0), 2) AS SUCCESS_RATE,
            ROUND(SUM(FAILED_COUNT) * 100.0 / NULLIF(SUM(TOTAL_COUNT), 0), 2) AS FAILURE_RATE
        FROM (
            SELECT 
                TRUNC(ACTUAL_START) AS DATE_VAL,
                SUM(CASE WHEN RUN_STATUS_CODE = 1 THEN 1 ELSE 0 END) AS SUCCEEDED_COUNT,
                SUM(CASE WHEN RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1 ELSE 0 END) AS FAILED_COUNT,
                SUM(CASE WHEN RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) AS RUNNING_COUNT,
                COUNT(*) AS TOTAL_COUNT
            FROM INFA_PCREPO.REP_SESS_LOG
            WHERE TRUNC(ACTUAL_START) >= TRUNC(SYSDATE) - 6
              AND TRUNC(ACTUAL_START) < TRUNC(SYSDATE)
            GROUP BY TRUNC(ACTUAL_START)
        )
        GROUP BY DATE_VAL, TO_CHAR(DATE_VAL, 'fmDay')
        ORDER BY DATE_VAL DESC
        """
        
        results = fetch_all(query)
        return results if results else []
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch 6-day historical data: {e}")
        import traceback
        traceback.print_exc()
        return []