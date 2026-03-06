# portal/sql/level3_queries.py

def clean_sql(sql: str) -> str:
    """
    Fix common HTML entity encodings that break SQL:
      &gt;  -> >
      &gt;= -> >=
      &lt;  -> <
      &lt;= -> <=
      &amp; -> &
    """
    return (
        sql.replace("&gt;=", ">=")
           .replace("&gt;", ">")
           .replace("&lt;=", "<=")
           .replace("&lt;", "<")
           .replace("&amp;", "&")
    ).strip()


# ---------------- QUERIES (PASTE YOUR EXACT QUERIES BELOW) ----------------

MAIN_QUERY = r"""
with ABC AS (SELECT A.GRID_NAME,
       A.SUBJECT_AREA,
       A.WORKFLOW_NAME,
       A.SESSION_NAME,
       A.START_TIME,
       A.END_TIME,
       A.STATUS,
       A.NEXT_RESTART_TIME,
       A.COMPLETION_TIME_AFTER_FAILURE,
       CASE WHEN A.SESSION_NAME = B.SESSION_NAME THEN 'Y' ELSE 'N' END AS PREV_FAILURE
FROM (SELECT SERVER_NAME AS GRID_NAME,
  SUBJECT_AREA,
  WORKFLOW_NAME,
  INSTANCE_NAME AS SESSION_NAME,
  START_TIME,
  END_TIME,
  DECODE (RUN_STATUS_CODE, 3, 'Failed', 4, 'Stopped', 5, 'Aborted', 15, 'Terminated') AS STATUS,
  suc_START_TIME NEXT_RESTART_TIME,
suc_END_TIME COMPLETION_TIME_AFTER_FAILURE
FROM (
select F.*, row_number() OVER (partition BY F.instance_id, F.workflow_id,F.START_TIME ORDER BY suc.START_TIME ASC) srnk,
suc.START_TIME suc_START_TIME, suc.END_TIME suc_END_TIME
from (
select TIR.*,
row_number() OVER (partition BY TIR.instance_id, TIR.workflow_id ORDER BY TIR.workflow_run_id DESC) rnk
from INFA_PCREPO.REP_TASK_INST_RUN TIR where RUN_STATUS_CODE IN (3,4,15) and TASK_TYPE_NAME = 'Session'
) F
left join INFA_PCREPO.REP_TASK_INST_RUN suc ON suc.RUN_STATUS_CODE IN (1) and suc.TASK_TYPE_NAME = 'Session'
and SUC.instance_id     =F.instance_id AND SUC.workflow_id     =F.workflow_id
and SUC.START_TIME > F.END_TIME
where 1=1
) where srnk=1
AND  TRUNC (START_TIME) = TRUNC (SYSDATE)
               AND (INSTANCE_NAME, START_TIME) IN
              (  SELECT INSTANCE_NAME, MAX (START_TIME)
                   FROM INFA_PCREPO.REP_TASK_INST_RUN
                  WHERE TASK_TYPE_NAME = 'Session'
               GROUP BY INSTANCE_NAME) ) A
LEFT JOIN (
    SELECT DISTINCT SESSION_NAME
    FROM (
        SELECT SESSION_NAME
        FROM (
            SELECT TIR.SERVER_NAME AS GRID_NAME,
                   TIR.SUBJECT_AREA,
                   TIR.WORKFLOW_NAME,
                   TIR.INSTANCE_NAME AS SESSION_NAME,
                   TIR.START_TIME,
                   TIR.END_TIME,
                   DECODE(TIR.RUN_STATUS_CODE,
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
            WHERE TIR.TASK_TYPE_NAME = 'Session'
              AND TRUNC(TIR.START_TIME) = TRUNC(SYSDATE)
              AND TIR.RUN_STATUS_CODE IN (3, 4, 5, 15)
              AND (TIR.INSTANCE_NAME, TIR.START_TIME) IN (
                    SELECT INSTANCE_NAME, MAX(START_TIME)
                    FROM INFA_PCREPO.REP_TASK_INST_RUN
                    WHERE TASK_TYPE_NAME = 'Session'
                    GROUP BY INSTANCE_NAME
                )
        )
        WHERE SESSION_NAME IN (
            SELECT DISTINCT SESSION_NAME
            FROM (
                SELECT TIR.INSTANCE_NAME AS SESSION_NAME
                FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
                WHERE TIR.TASK_TYPE_NAME = 'Session'
               AND TRUNC(TIR.START_TIME) BETWEEN TRUNC(SYSDATE) - 3 AND TRUNC(SYSDATE) - 1
                  AND TIR.RUN_STATUS_CODE IN (3, 4, 15)
            )
        )
    )
) B ON A.SESSION_NAME = B.SESSION_NAME)
,XYZ AS (
Select Workflow_name, Session_name, MAX (COMPLETION_TIME_AFTER_FAILURE) AS LAST_COMP_TIME from (
Select Workflow_name, Session_name, (COMPLETION_TIME_AFTER_FAILURE) from ABC
where COMPLETION_TIME_AFTER_FAILURE IS NOT NULL
UNION 
Select Workflow_name, Session_name, (COMPLETION_TIME_AFTER_FAILURE) from INFA_PCREPO.SOX_TABLE_FOR_LEVEL3_FALIURE_LIST
where COMPLETION_TIME_AFTER_FAILURE IS NOT NULL)
group by WORKFLOW_NAME,Session_name)

,CDE AS (Select A.GRID_NAME,
       A.SUBJECT_AREA,
       A.WORKFLOW_NAME,
       A.SESSION_NAME,
       A.START_TIME,
       A.END_TIME,
       A.STATUS,
       A.NEXT_RESTART_TIME,
       A.COMPLETION_TIME_AFTER_FAILURE,
       CASE WHEN A.FAILDED_DAYS_COUNT > 5 THEN 'Y' ELSE 'N' END AS PREV_FAILURE,
       A.LAST_COMP_TIME,A.FAILDED_DAYS_COUNT
       FROM (
(Select A.*,CASE WHEN A.PREV_FAILURE='Y' THEN B.LAST_COMP_TIME ELSE NULL END AS LAST_COMP_TIME,
CASE WHEN A.PREV_FAILURE='Y'  AND B.LAST_COMP_TIME IS NOT NULL  THEN TRUNC(SYSDATE,'DD')-TRUNC(B.LAST_COMP_TIME,'DD')
WHEN  A.PREV_FAILURE='Y' AND B.LAST_COMP_TIME IS NULL THEN 365
ELSE NULL END AS FAILDED_DAYS_COUNT from ABC A
LEFT JOIN XYZ B
ON A.WORKFLOW_NAME =B.WORKFLOW_NAME
AND A.SESSION_NAME =B.SESSION_NAME)
)A) 

Select GRID_NAME,
       SUBJECT_AREA,
       WORKFLOW_NAME,
       SESSION_NAME,
       START_TIME,
       END_TIME,
       STATUS,
       NEXT_RESTART_TIME,
       COMPLETION_TIME_AFTER_FAILURE,
       PREV_FAILURE,
       CASE WHEN PREV_FAILURE ='N' AND LAST_COMP_TIME IS NOT NULL THEN NULL ELSE LAST_COMP_TIME END AS LAST_COMP_TIME,
       CASE WHEN PREV_FAILURE ='N' AND FAILDED_DAYS_COUNT IS NOT NULL THEN NULL ELSE FAILDED_DAYS_COUNT END AS FAILDED_DAYS_COUNT
        From CDE
        ORDER BY PREV_FAILURE DESC

"""

SUMMARY_QUERY = r"""
 Select * from (Select 'TOTAL_FAILED_JOBS'  AS TOTAL_FAILED_COUNT, Count (DISTINCT SESSION_NAME ) FROM (SELECT TIR.SERVER_NAME AS GRID_NAME,
        TIR.SUBJECT_AREA,
       TIR.WORKFLOW_NAME,
       TIR.INSTANCE_NAME AS SESSION_NAME,
       TIR.START_TIME,
       TIR.END_TIME,
      DECODE (RUN_STATUS_CODE,
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
15, 'Terminated')
          AS STATUS
  FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
 WHERE     TASK_TYPE_NAME = 'Session'
  --AND RUN_STATUS_CODE IN (6)
AND TRUNC (START_TIME) = TRUNC (SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15))
    
    UNION ALL
    
        (Select 'COMPLETED_JOBS' AS COMPLETED_FAILED_COUNT,COUNT( DISTINCT SESSION_NAME) AS COMPLETED_FAILED_JOBS from ( SELECT  SERVER_NAME AS GRID_NAME,
  SUBJECT_AREA,
  WORKFLOW_NAME,
  INSTANCE_NAME AS SESSION_NAME, 
START_TIME,
 END_TIME,
  DECODE (RUN_STATUS_CODE, 3, 'Failed', 4, 'Stopped', 5, 'Aborted', 15, 'Terminated') AS STATUS,
suc_START_TIME NEXT_RESTART_TIME,
suc_END_TIME COMPLETION_TIME_AFTER_FAILURE
FROM (
select F.*, row_number() OVER (partition BY F.instance_id, F.workflow_id,F.START_TIME ORDER BY suc.START_TIME ASC) srnk,
suc.START_TIME suc_START_TIME, suc.END_TIME suc_END_TIME
from (
select TIR.*,
row_number() OVER (partition BY TIR.instance_id, TIR.workflow_id ORDER BY TIR.workflow_run_id DESC) rnk
from INFA_PCREPO.REP_TASK_INST_RUN TIR where RUN_STATUS_CODE IN (3,4,15) and TASK_TYPE_NAME = 'Session'
) F
left join INFA_PCREPO.REP_TASK_INST_RUN suc ON suc.RUN_STATUS_CODE IN (1) and suc.TASK_TYPE_NAME = 'Session'
and SUC.instance_id     =F.instance_id AND SUC.workflow_id     =F.workflow_id
and SUC.START_TIME > F.END_TIME
where 1=1
) where srnk=1
AND  TRUNC (START_TIME) = TRUNC (SYSDATE))
WHERE COMPLETION_TIME_AFTER_FAILURE IS NOT NULL)
    
    
    
    UNION ALL
    
     Select 'PENDING_FAILED_JOBS'  AS TOTAL_FAILED_COUNT, Count (DISTINCT SESSION_NAME ) FROM (SELECT TIR.SERVER_NAME AS GRID_NAME,
        TIR.SUBJECT_AREA,
       TIR.WORKFLOW_NAME,
       TIR.INSTANCE_NAME AS SESSION_NAME,
       TIR.START_TIME,
       TIR.END_TIME,
      DECODE (RUN_STATUS_CODE,
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
15, 'Terminated')
          AS STATUS
  FROM INFA_PCREPO.REP_TASK_INST_RUN TIR
 WHERE     TASK_TYPE_NAME = 'Session'
  --AND RUN_STATUS_CODE IN (6)
AND TRUNC (START_TIME) = TRUNC (SYSDATE)
    AND RUN_STATUS_CODE IN (3, 4, 5, 15)
       AND (INSTANCE_NAME, START_TIME) IN
              (  SELECT INSTANCE_NAME, MAX (START_TIME)
                   FROM INFA_PCREPO.REP_TASK_INST_RUN
                  WHERE TASK_TYPE_NAME = 'Session'
               GROUP BY INSTANCE_NAME)))
         
"""

LONG_RUNNING_QUERY = r"""
SELECT * FROM (
  SELECT 
    ROUND((SYSDATE - start_time) * 24) AS Current_run_Duration_in_Hours,
    SERVER_NAME AS GRID_NAME,
    SUBJECT_AREA,
    WORKFLOW_NAME,
    INSTANCE_NAME AS SESSION_NAME,
    START_TIME,
    DECODE(RUN_STATUS_CODE, 6, 'Running') AS STATUS
  FROM 
    INFA_PCREPO.REP_TASK_INST_RUN
  WHERE 
    RUN_STATUS_CODE = 6
)
WHERE Current_run_Duration_in_Hours >= 24
ORDER BY Current_run_Duration_in_Hours DESC
"""