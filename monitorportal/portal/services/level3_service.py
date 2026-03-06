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
    Fetch DISTINCT sessions with errors from Oracle (Latest failure per session, not restarted)
    Returns: rows_list with full error messages
    OPTIMIZED: Uses hints and limits for better performance
    """
    try:
        query = """
        SELECT /*+ FIRST_ROWS(100) */ 
            grid_name,
            subject_area,
            workflow_name,
            session_name,
            start_time,
            end_time,
            status,
            error_message
        FROM (
            SELECT /*+ INDEX(TIR) PARALLEL(TIR, 4) */
                TIR.SERVER_NAME AS grid_name,
                TIR.SUBJECT_AREA AS subject_area,
                TIR.WORKFLOW_NAME AS workflow_name,
                TIR.INSTANCE_NAME AS session_name,
                TIR.START_TIME AS start_time,
                TIR.END_TIME AS end_time,
                DECODE(TIR.RUN_STATUS_CODE, 3, 'Failed', 4, 'Stopped', 5, 'Aborted', 15, 'Terminated') AS status,
                TIR.RUN_ERR_MSG AS error_message,
                ROW_NUMBER() OVER (PARTITION BY TIR.INSTANCE_NAME 
                                   ORDER BY TIR.START_TIME DESC) AS rn,
                (SELECT COUNT(*) 
                 FROM INFA_PCREPO.REP_TASK_INST_RUN SUC
                 WHERE SUC.INSTANCE_NAME = TIR.INSTANCE_NAME
                   AND SUC.RUN_STATUS_CODE = 1
                   AND SUC.TASK_TYPE_NAME = 'Session'
                   AND SUC.START_TIME > TIR.END_TIME
                   AND ROWNUM = 1) AS success_count
            FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
            WHERE TIR.RUN_STATUS_CODE IN (3, 4, 15)
              AND TIR.TASK_TYPE_NAME = 'Session'
              AND TRUNC(TIR.START_TIME) = TRUNC(SYSDATE)
        )
        WHERE rn = 1
          AND success_count = 0
          AND ROWNUM <= 500
        ORDER BY start_time DESC
        """
        return fetch_all(query)
    except Exception as e:
        print(f"Error fetching level3 failed with error: {e}")
        return []


def get_level3_long_running():
    """
    Fetch long-running sessions from Oracle (sessions running longer than their historical average)
    Returns: rows_list
    OPTIMIZED: Uses hints and limits for better performance
    """
    try:
        query = """
        SELECT /*+ FIRST_ROWS(50) */
            A.SERVER_NAME AS grid_name,
            A.SUBJECT_AREA AS subject_area,
            A.WORKFLOW_NAME AS workflow_name,
            A.INSTANCE_NAME AS session_name,
            A.START_TIME AS start_time,
            A.CURRENT_RUN_DURATION_IN_MIN AS current_duration_min,
            B.AVG_RUN_DURATION_IN_MIN AS avg_duration_min
        FROM (
            SELECT /*+ INDEX(R) PARALLEL(R, 4) */
                R.SERVER_NAME,
                R.SUBJECT_AREA,
                R.WORKFLOW_NAME,
                R.INSTANCE_NAME,
                R.START_TIME,
                ROUND((SYSDATE - R.START_TIME) * 24 * 60) AS CURRENT_RUN_DURATION_IN_MIN
            FROM 
                INFA_PCREPO.REP_TASK_INST_RUN R
            WHERE 
                R.RUN_STATUS_CODE = 6
                AND R.START_TIME >= TRUNC(SYSDATE) - 2
                AND ROWNUM <= 200
        ) A
        JOIN (
            SELECT 
                INSTANCE_NAME,
                ROUND(AVG((END_TIME - START_TIME) * 24 * 60)) AS AVG_RUN_DURATION_IN_MIN
            FROM 
                INFA_PCREPO.REP_TASK_INST_RUN
            WHERE 
                END_TIME IS NOT NULL
                AND START_TIME >= TRUNC(SYSDATE) - 7
                AND INSTANCE_NAME IS NOT NULL
                AND END_TIME > START_TIME
            GROUP BY INSTANCE_NAME
        ) B ON A.INSTANCE_NAME = B.INSTANCE_NAME
        WHERE 
            A.CURRENT_RUN_DURATION_IN_MIN > B.AVG_RUN_DURATION_IN_MIN
            AND ROWNUM <= 100
        ORDER BY 
            A.CURRENT_RUN_DURATION_IN_MIN DESC
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
    """
    try:
        query = """
        WITH master_runs AS (
            SELECT DISTINCT
                m.TASKFLOW_RUN_ID,
                FIRST_VALUE(m.START_TIME) OVER (
                    PARTITION BY m.TASKFLOW_RUN_ID 
                    ORDER BY m.START_TIME
                ) AS run_start_time,
                FIRST_VALUE(m.END_TIME) OVER (
                    PARTITION BY m.TASKFLOW_RUN_ID 
                    ORDER BY m.START_TIME
                ) AS run_end_time,
                FIRST_VALUE(m.STATUS) OVER (
                    PARTITION BY m.TASKFLOW_RUN_ID 
                    ORDER BY m.START_TIME
                ) AS run_status
            FROM MAPDQPRD.IICS_CDI_RUN_INFO m
            WHERE m.ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
            AND m.START_TIME >= SYSDATE - 3
        ),
        latest_8_runs AS (
            SELECT *
            FROM master_runs
            ORDER BY run_start_time DESC
            FETCH FIRST 8 ROWS ONLY
        ),
        latest_job_status AS (
            SELECT 
                j.TASKFLOW_RUN_ID,
                j.ASSET_NAME,
                j.STATUS,
                ROW_NUMBER() OVER (
                    PARTITION BY j.TASKFLOW_RUN_ID, j.ASSET_NAME 
                    ORDER BY j.START_TIME DESC, j.END_TIME DESC NULLS LAST
                ) AS rn
            FROM MAPDQPRD.IICS_CDI_RUN_INFO j
            INNER JOIN latest_8_runs l ON j.TASKFLOW_RUN_ID = l.TASKFLOW_RUN_ID
            WHERE j.LOCATION IN (
                'CDW_DSL_ERP\\Workflows',
                'CDW_DSL_ERP\\Sessions',
                'CDW_ASL_SAPS4\\Workflows',
                'ASL_ERP_DATAHUB\\Workflows'
            )
            AND j.ASSET_NAME NOT LIKE '%TAX%'
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
        )
        SELECT
            TO_CHAR(
                FROM_TZ(CAST(l.run_start_time AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH12:MI AM'
            ) AS run_label,
            l.TASKFLOW_RUN_ID AS taskflow_run_id,
            TO_CHAR(
                FROM_TZ(CAST(l.run_start_time AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH12:MI:SS AM'
            ) AS start_time_mst,
            TO_CHAR(
                FROM_TZ(CAST(l.run_end_time AS TIMESTAMP), 'UTC')
                AT TIME ZONE 'America/Denver',
                'DD-MON-YYYY HH12:MI:SS AM'
            ) AS end_time_mst,
            CASE 
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
                WHEN COALESCE(jc.running, 0) > 0 THEN 'RUNNING'
                WHEN COALESCE(jc.failed, 0) > 0 THEN 'FAILED'
                WHEN COALESCE(jc.succeeded, 0) = COALESCE(jc.total_jobs, 0) AND COALESCE(jc.total_jobs, 0) > 0 THEN 'SUCCESS'
                WHEN COALESCE(jc.suspended, 0) > 0 THEN 'SUSPENDED'
                WHEN l.run_end_time IS NULL THEN 'RUNNING'
                ELSE 'UNKNOWN'
            END AS run_status
        FROM latest_8_runs l
        LEFT JOIN job_counts jc ON l.TASKFLOW_RUN_ID = jc.TASKFLOW_RUN_ID
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
            WHERE TRUNC(start_time) = TRUNC(SYSDATE)
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
            WHERE TRUNC(start_time) = TRUNC(SYSDATE)
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
    Fetch ALL Level3 job statuses from INFA_PCREPO.REP_SESS_LOG
    Returns: (summary_dict, rows_list) with total counts (no application breakdown)
    """
    try:
        query = """
        SELECT 
            SUBJECT_AREA AS folder,
            WORKFLOW_NAME,
            SESSION_NAME,
            TO_CHAR(ACTUAL_START, 'HH12:MI:SS AM') AS sess_start_time,
            TO_CHAR(SESSION_TIMESTAMP, 'HH12:MI:SS AM') AS sess_end_time,
            TO_CHAR(
                TO_DATE('1970-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
                + (SESSION_TIMESTAMP - ACTUAL_START),
                'HH24:MI:SS'
            ) AS duration_in_mins,
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
                   15, 'Terminated') AS status
        FROM INFA_PCREPO.REP_SESS_LOG
        WHERE TRUNC(ACTUAL_START) = TRUNC(SYSDATE)
        ORDER BY 
            CASE 
                WHEN RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1  -- Failed/Stopped/Aborted/Terminated
                WHEN RUN_STATUS_CODE = 6 THEN 2               -- Running
                WHEN RUN_STATUS_CODE = 1 THEN 3               -- Succeeded
                ELSE 4                                         -- Other
            END,
            ACTUAL_START DESC
        """
        rows = fetch_all(query)
        
        # Calculate summary totals (no application breakdown)
        total_succeeded = 0
        total_failed = 0
        total_running = 0
        total_other = 0
        
        for row in rows:
            status = str(row.get("status", "")).lower()
            
            if status == "succeeded":
                total_succeeded += 1
            elif status in ["failed", "stopped", "aborted", "terminated"]:
                total_failed += 1
            elif status == "running":
                total_running += 1
            else:
                total_other += 1
        
        summary = {
            "total_jobs": len(rows),
            "total_succeeded": total_succeeded,
            "total_failed": total_failed,
            "total_running": total_running,
            "total_other": total_other
        }
        
        return summary, rows
    except Exception as e:
        print(f"Error fetching level3 all jobs status: {e}")
        import traceback
        traceback.print_exc()
        return {"total_jobs": 0, "total_succeeded": 0, "total_failed": 0, "total_running": 0, "total_other": 0}, []


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
        WHERE TRUNC(ACTUAL_START) = TRUNC(SYSDATE)
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
          AND TRUNC(start_time) = TRUNC(SYSDATE)
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
          AND TRUNC(start_time) = TRUNC(SYSDATE) - :days_ago
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
    Fetch job status for last 7 days using separate optimized queries
    Returns: List of daily summaries [today, yesterday, ..., 6 days ago]
    """
    import time
    start = time.time()
    
    results = []
    
    # Get TODAY first (most important)
    today_data = get_level3_jobs_today_only()
    results.append(today_data)
    
    # Get each historical day separately (can be parallelized in future)
    for days_ago in range(1, 7):
        day_data = get_level3_jobs_single_day(days_ago)
        results.append(day_data)
    
    elapsed = time.time() - start
    print(f"[PERFORMANCE] 7-day stats fetched in {elapsed:.2f} seconds using separate queries")
    
    return results


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
    Uses SIMPLIFIED queries for better performance (< 15 seconds vs 2 minutes).
    
    Returns: (summary_dict, failed_jobs_list)
    
    Summary includes:
        - total_failed: Total number of failed sessions
        - completed_after_restart: Sessions that failed, restarted, and completed
        - pending_jobs: Failed sessions not yet restarted
        - restarted_running: Restarted sessions currently running
    """
    try:
        # SIMPLIFIED Main Query - Shows DISTINCT sessions (latest failure per session)
        # Counts unique failed sessions today, not ALL occurrences
        main_query = """
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
            END AS failded_days_count
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
        
        # Count DISTINCT failed sessions today
        total_query = """
        SELECT COUNT(DISTINCT INSTANCE_NAME) AS total_count
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE TASK_TYPE_NAME = 'Session'
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        AND RUN_STATUS_CODE IN (3, 4, 5, 15)
        AND INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
        """
        
        # Completed jobs - DISTINCT sessions that failed then succeeded
        completed_query = """
        SELECT COUNT(DISTINCT session_name) AS completed_failed_jobs
        FROM (
            SELECT 
                TIR.INSTANCE_NAME AS session_name,
                MIN(CASE WHEN TIR.RUN_STATUS_CODE IN (3, 4, 5, 15) THEN TIR.START_TIME END) AS first_failure,
                MAX(CASE WHEN TIR.RUN_STATUS_CODE = 1 THEN TIR.START_TIME END) AS last_success
            FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
            WHERE TIR.TASK_TYPE_NAME = 'Session'
            AND TRUNC(TIR.START_TIME) = TRUNC(SYSDATE)
            AND TIR.INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
            GROUP BY TIR.INSTANCE_NAME
            HAVING 
                MIN(CASE WHEN TIR.RUN_STATUS_CODE IN (3, 4, 5, 15) THEN TIR.START_TIME END) IS NOT NULL
                AND MAX(CASE WHEN TIR.RUN_STATUS_CODE = 1 THEN TIR.START_TIME END) IS NOT NULL
                AND MAX(CASE WHEN TIR.RUN_STATUS_CODE = 1 THEN TIR.START_TIME END) > MIN(CASE WHEN TIR.RUN_STATUS_CODE IN (3, 4, 5, 15) THEN TIR.START_TIME END)
        )
        """
        
        # Pending jobs - DISTINCT sessions where latest status is still failed
        pending_query = """
        SELECT COUNT(DISTINCT INSTANCE_NAME) AS pending_count
        FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
        WHERE TASK_TYPE_NAME = 'Session'
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        AND RUN_STATUS_CODE IN (3, 4, 5, 15)
        AND INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
        AND (INSTANCE_NAME, START_TIME) IN (
            SELECT INSTANCE_NAME, MAX(START_TIME)
            FROM INFA_PCREPO.REP_TASK_INST_RUN
            WHERE TASK_TYPE_NAME = 'Session'
            AND TRUNC(START_TIME) = TRUNC(SYSDATE)
            GROUP BY INSTANCE_NAME
        )
        """
        
        # Running jobs - DISTINCT sessions that are currently running after failure
        running_query = """
        SELECT COUNT(DISTINCT session_name) AS running_jobs
        FROM (
            SELECT 
                TIR.INSTANCE_NAME AS session_name,
                MAX(CASE WHEN TIR.RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1 ELSE 0 END) AS had_failure,
                MAX(CASE WHEN TIR.RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) AS is_running
            FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
            WHERE TIR.TASK_TYPE_NAME = 'Session'
            AND TRUNC(TIR.START_TIME) = TRUNC(SYSDATE)
            AND TIR.INSTANCE_NAME NOT IN ('s_m_Check_App_Cntrl_Status_TN_Aging_Update_Parameters_Load_End_Time')
            GROUP BY TIR.INSTANCE_NAME
            HAVING 
                MAX(CASE WHEN TIR.RUN_STATUS_CODE IN (3, 4, 5, 15) THEN 1 ELSE 0 END) = 1
                AND MAX(CASE WHEN TIR.RUN_STATUS_CODE = 6 THEN 1 ELSE 0 END) = 1
        )
        """
        
        # Execute queries in parallel (faster)
        print("[DEBUG] Executing Level3 failed jobs queries...")
        import time
        start_time = time.time()
        
        failed_jobs = fetch_all(main_query)
        print(f"[DEBUG] Main query: {time.time() - start_time:.2f}s, {len(failed_jobs)} rows")
        
        start_time = time.time()
        total_result = fetch_all(total_query)
        completed_result = fetch_all(completed_query)
        pending_result = fetch_all(pending_query)
        running_result = fetch_all(running_query)
        print(f"[DEBUG] Summary queries: {time.time() - start_time:.2f}s")
        
        # Extract summary values
        total_failed = total_result[0].get('total_count', 0) if total_result else 0
        completed_after_restart = completed_result[0].get('completed_failed_jobs', 0) if completed_result else 0
        pending_jobs = pending_result[0].get('pending_count', 0) if pending_result else 0
        restarted_running = running_result[0].get('running_jobs', 0) if running_result else 0
        
        summary = {
            'total_failed': total_failed,
            'completed_after_restart': completed_after_restart,
            'pending_jobs': pending_jobs,
            'restarted_running': restarted_running
        }
        
        print(f"[DEBUG] Summary: {summary}")
        
        return summary, failed_jobs
        
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
