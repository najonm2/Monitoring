# portal/services/bi_service.py
from portal.db.oracle_client import fetch_all
from datetime import datetime, timedelta


# Application mapping with SLA details - Updated as per Level3 BI Feed requirements (Mar 11, 2026)
# 19 applications numbered 1-19 with correct target_next_day flags and application names
APP_SLA_CONFIG = {
    1: {
        "name": "CDW-ASR ODS",
        "priority": 1,
        "category": "",
        "start_time": "15:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
        "job_name": "B_CDW_ODS_OFFNET >wkf_LOAD_ASR",
    },
    2: {
        "name": "CDW-AML",
        "priority": 1,
        "category": "",
        "start_time": "11:00",
        "target_sla_time": "09:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_AML --> wkf_Load_AML_ALL",
    },
    3: {
        "name": "CDW-Orders ODS",
        "priority": 1,
        "category": "",
        "start_time": "12:00",
        "target_sla_time": "07:00",
        "target_next_day": True,
        "job_name": "B_CDW_ODS > wkf_LOAD_ODS_LEAD_TO_ORDER",
    },
    4: {
        "name": "CDW-Network Inventory ODS",
        "priority": 1,
        "category": "",
        "start_time": "21:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
        "job_name": "B_CDW_ODS_NETINV > wkf_Load_CIRCUIT_ALL",
    },
    5: {
        "name": "SMMART",
        "priority": 1,
        "category": "",
        "start_time": "19:00",
        "target_sla_time": "03:30",
        "target_next_day": True,
        "job_name": "B_SMMART>",
    },
    6: {
        "name": "CDW-DSL-SALES-PERIOD",
        "priority": 1,
        "category": "",
        "start_time": "03:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_SALES_PERIOD>wkf_Load_DSL_SALES_PERIOD",
    },
    7: {
        "name": "DSL_SD",
        "priority": 1,
        "category": "",
        "start_time": "19:00",
        "target_sla_time": "05:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_SD/wkf_LOAD_CDW_DSL_SD",
    },
    8: {
        "name": "DSL_CALL_CENTER",
        "priority": 1,
        "category": "",
        "start_time": "20:00",
        "target_sla_time": "08:30",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_CALL_CENTER>wkf_Load_DSL_CALL_CENTER_CONVERSATION_HIST",
    },
    9: {
        "name": "DSL_AIM",
        "priority": 3,
        "category": "",
        "start_time": "09:30",
        "target_sla_time": "12:00",
        "target_next_day": False,
        "job_name": "B_CDW_DSL_AIM > wkf_Load_ACCRUAL_EXPENSE",
    },
    10: {
        "name": "CODS_TN",
        "priority": 2,
        "category": "",
        "start_time": "02:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
        "job_name": "B_CDW_ODS_TN> wkf_Load_CODS_TN",
    },
    11: {
        "name": "ASPEN",
        "priority": 2,
        "category": "",
        "start_time": "18:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_ASPEN > wkf_Rollup_Daily",
    },
    12: {
        "name": "CRFTPS-SMS files",
        "priority": 2,
        "category": "",
        "start_time": "07:00",
        "target_sla_time": "08:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_PHONEBOOK > wkf_Generate_SMS",
    },
    13: {
        "name": "CRFTPS-Phonebook files",
        "priority": 2,
        "category": "",
        "start_time": "19:33",
        "target_sla_time": "08:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_PHONEBOOK > wkf_Generate_PHBK",
    },
    14: {
        "name": "DataMarketplace-ALL",
        "priority": 2,
        "category": "",
        "start_time": "06:00",
        "target_sla_time": "11:00",
        "target_next_day": False,
        "job_name": "B_DATAMKTP > wkf_Load_DATAMKTP",
    },
    15: {
        "name": "SOLR_LUCENE(Daily)",
        "priority": 3,
        "category": "",
        "start_time": "06:20",
        "target_sla_time": "12:00",
        "target_next_day": True,
        "job_name": "B_IAC_SOLR_LUCENE>wkf_Load_Refresh_Solr_Lucene_Index_TNLookup",
    },
    16: {
        "name": "DSL_MARGIN",
        "priority": 3,
        "category": "",
        "start_time": "09:00",
        "target_sla_time": "12:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_MARGIN>wkf_Load_DSL_Margin",
    },
    17: {
        "name": "Planned Bill Cost",
        "priority": 3,
        "category": "",
        "start_time": "06:00",
        "target_sla_time": "12:00",
        "target_next_day": True,
        "job_name": "B_CDW_DSL_AML/wkf_Load_AML_PLANNED_COST",
    },
    18: {
        "name": "SDP/Sales Orders (fCTL Data Lake/ASL)",
        "priority": 3,
        "category": "",
        "start_time": "01:00",
        "target_sla_time": "07:00",
        "target_next_day": True,
        "job_name": "B_CDW_ASL_SDP_ORDER>wkf_load_CDW_ASL_SDP_ORDER",
    },
    19: {
        "name": "Service Lookup Refresh (SLV)",
        "priority": 3,
        "category": "",
        "start_time": "02:00",
        "target_sla_time": "12:00",
        "target_next_day": True,
        "job_name": "B_CDW_ERM > wkf_Load_Service_Lookup_Refresh",
    },
}


def calculate_sla_met_miss(actual_completion, target_sla):
    """
    Calculate SLA met/miss in minutes
    Positive = Met, Negative = Missed
    """
    try:
        if not actual_completion or not target_sla:
            return None
        
        diff = target_sla - actual_completion
        minutes = int(diff.total_seconds() / 60)
        return minutes
    except:
        return None


def format_time_difference(minutes):
    """
    Format minutes into hh:mm format
    """
    if minutes is None:
        return "N/A"
    
    abs_minutes = abs(minutes)
    hours = abs_minutes // 60
    mins = abs_minutes % 60
    
    sign = "-" if minutes < 0 else ""
    return f"{sign}{hours:02d}:{mins:02d}"


def get_level3_bi_feed():
    """
    Fetch Level3 BI feed data (Combined Excel feed + CAPEX)
    Enhanced with SLA calculations and application mappings
    OPTIMIZED: Uses query hints for better performance
    Returns: rows_list with enriched data
    """
    try:
        query = """
        SELECT Excel_no,
               application_name,
               dependency_name,
               end_dt_in_MST 
        FROM (
            SELECT 1 as Excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name='B_CDW_ODS_OFFNET' 
              AND dependency_name='wkf_Load_ASR' 
              AND STATUS_CD = 'Succeeded'
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 2 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name='B_CDW_DSL_AML' 
              AND dependency_name='wkf_Load_AML_ALL' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 3 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name='B_CDW_ODS' 
              AND dependency_name='wkf_LOAD_ODS_LEAD_TO_ORDER' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 4 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name='B_CDW_ODS_NETINV' 
              AND dependency_name='wkf_Load_CIRCUIT_ALL' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 5 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name = 'B_SMMART' 
              AND dependency_name='wkf_SMMART_Controller' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 6 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_SALES_PERIOD' 
              AND dependency_name='wkf_Load_DSL_SALES_PERIOD' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 7 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_SD' 
              AND dependency_name='wkf_Load_CDW_DSL_SD' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION
            SELECT 8 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_CALL_CENTER' 
              AND dependency_name='wkf_Load_DSL_CALL_CENTER_CONVERSATION_HIST' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION
            SELECT 9 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_AIM' 
              AND dependency_name='wkf_Load_DSL_AIM' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION
            SELECT 10 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_ODS_TN' 
              AND dependency_name='wkf_Load_CODS_TN' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 11 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_ASPEN' 
              AND dependency_name='wkf_Rollup_Daily' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 12 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_PHONEBOOK' 
              AND dependency_name='wkf_Generate_SMS' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 13 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_PHONEBOOK' 
              AND dependency_name='wkf_Generate_PHBK' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 14 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name='B_DATAMKTP' 
              AND dependency_name='wkf_Load_DATAMKTP' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION
            SELECT 15 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_IAC_SOLR_LUCENE' 
              AND dependency_name='wkf_Refresh_Solr_Lucene_Index_TNLookup' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 16 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_MARGIN' 
              AND dependency_name='wkf_Load_DSL_Margin' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION
            SELECT 17 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_DSL_AML' 
              AND dependency_name='wkf_Load_AML_PLANNED_COST' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION 
            SELECT 18 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_ASL_SDP_ORDER' 
              AND dependency_name='wkf_Load_CDW_ASL_SDP_ORDER' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
            
            UNION
            SELECT 19 as excel_no, application_name, dependency_name, 
                   (MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR')) as end_dt_in_MST 
            FROM ICSM.app_control_status  
            WHERE application_name ='B_CDW_ERM' 
              AND dependency_name='wkf_Load_Service_Lookup_Refresh' 
              AND STATUS_CD = 'Succeeded' 
            GROUP BY application_name, dependency_name
        )
        ORDER BY Excel_no
        """
        rows = fetch_all(query)
        
        # Enrich data with SLA information
        today = datetime.now()
        enriched_rows = []
        
        for row in rows:
            excel_no = row.get("excel_no")
            end_dt_in_mst = row.get("end_dt_in_mst")
            
            # Get SLA configuration
            config = APP_SLA_CONFIG.get(excel_no, {})
            
            enriched_row = {
                "date": today.strftime("%m/%d/%Y %a"),
                "app_num": excel_no,
                "priority": config.get("priority", ""),
                "sla_application": config.get("name", "Unknown"),
                "category": config.get("category", ""),
                "status": "Complete" if end_dt_in_mst else "Pending",
                "start_time_mt": config.get("start_time", ""),
                "actual_completion_time_mt": end_dt_in_mst.strftime("%Y/%m/%d %H:%M") if end_dt_in_mst else "N/A",
                "target_sla_time_mt": "N/A",
                "sla_met_miss_min": None,
                "sla_met_miss_formatted": "N/A",
                "met_or_miss": "",
                # Original fields
                "excel_no": excel_no,
                "application_name": row.get("application_name"),
                "dependency_name": row.get("dependency_name"),
                "end_dt_in_mst": end_dt_in_mst,
            }
            
            # Calculate SLA if we have completion time and target
            if end_dt_in_mst and config.get("start_time") and config.get("start_time") != "Various":
                try:
                    # Create target SLA datetime based on today's date and target_next_day flag
                    target_time_str = config.get("target_sla_time")
                    target_next_day = config.get("target_next_day", False)
                    start_time_str = config.get("start_time")
                    
                    if target_time_str and target_time_str not in ["Various", "+3 hours"]:
                        target_hour, target_min = map(int, target_time_str.split(":"))
                        start_hour, start_min = map(int, start_time_str.split(":"))
                        
                        # Use today's date as reference for target SLA date
                        today_date = today.date()
                        
                        # If target_next_day is True, target is today; if False, target is yesterday
                        if target_next_day:
                            target_date = today_date
                        else:
                            target_date = today_date - timedelta(days=1)
                        
                        # Calculate target SLA based on target date and time
                        target_sla = datetime.combine(target_date, datetime.min.time()).replace(
                            hour=target_hour, minute=target_min, second=0, microsecond=0
                        )
                        
                        # Display target SLA as full datetime
                        enriched_row["target_sla_time_mt"] = target_sla.strftime("%Y/%m/%d %H:%M")
                        
                        # Calculate difference in minutes
                        sla_minutes = calculate_sla_met_miss(end_dt_in_mst, target_sla)
                        enriched_row["sla_met_miss_min"] = sla_minutes
                        enriched_row["sla_met_miss_formatted"] = str(sla_minutes)  # Show as minutes, not hh:mm
                        enriched_row["met_or_miss"] = "Miss" if sla_minutes and sla_minutes < 0 else "Met"
                except Exception as e:
                    print(f"Error calculating SLA for app {excel_no}: {e}")
            
            enriched_rows.append(enriched_row)
        
        return enriched_rows
    except Exception as e:
        print(f"Error fetching Level3 BI feed: {e}")
        return []


def get_capex_details():
    """
    Fetch CAPEX details with SLA information
    OPTIMIZED: Uses hints and limits rows to last 3 days
    TIMEZONE: Uses NUMTODSINTERVAL(6, 'HOUR') for UTC to MDT conversion
    Returns: rows_list
    """
    try:
        query = """
        SELECT /*+ FIRST_ROWS(10) INDEX(app_control_status) */
            APPLICATION_NAME,
            DEPENDENCY_NAME, 
            CAST((start_dt - NUMTODSINTERVAL(6, 'HOUR')) AS DATE) AS START_DATE_MDT,
            CAST((end_dt - NUMTODSINTERVAL(6, 'HOUR')) AS DATE) AS END_DATE_MDT,
            round(((3*60) - (end_dt-start_dt)*24*60), 0) as SLA_Met_Miss_MIN, 
            start_dt as START_DT_GMT, 
            end_dt as END_DT_GMT,
            status_cd 
        FROM (
            select /*+ PARALLEL(2) */ * from ICSM.app_control_status 
            where 1=1
            and application_name='A_MASTER_JOB_CONTROL'
            and dependency_name='wkf_SCM_DAILY_CAPEX_REFRESH'
        ) X
        where end_dt >= sysdate-3
        order by end_dt desc
        """
        return fetch_all(query)
    except Exception as e:
        print(f"Error fetching CAPEX details: {e}")
        return []

def get_bi_status_query():
    """
    Fetch BI Status Query with complete SLA calculations
    Returns: List of dicts with columns:
    - Date, App#, Pri., SLA Application, Status, Start time (MT), 
    - Actual Completion Time (MT), Target SLA (MT), SLA Met By (Minutes), Met or Miss?
    """
    try:
        query = """
        WITH
        /* ============================================================
           1) SLA MASTER
           ============================================================ */
        sla_def AS (
            SELECT 1 app_no, 1 pri, 'CDW-ASR ODS' sla_application,
                   '15:00' start_time_mt, '11:00' target_time_mt,
                   'B_CDW_ODS_OFFNET' application_name, 'wkf_Load_ASR' dependency_name FROM dual UNION ALL
            SELECT 2,1,'CDW-AML','11:00','09:00','B_CDW_DSL_AML','wkf_Load_AML_ALL' FROM dual UNION ALL
            SELECT 3,1,'CDW-Orders ODS','12:00','07:00','B_CDW_ODS','wkf_LOAD_ODS_LEAD_TO_ORDER' FROM dual UNION ALL
            SELECT 4,1,'CDW-Network Inventory ODS','21:00','11:00','B_CDW_ODS_NETINV','wkf_Load_CIRCUIT_ALL' FROM dual UNION ALL
            SELECT 5,1,'SMMART','19:00','03:30','B_SMMART','wkf_SMMART_Controller' FROM dual UNION ALL
            SELECT 6,1,'CDW-DSL-SALES-PERIOD','03:00','11:00','B_CDW_DSL_SALES_PERIOD','wkf_Load_DSL_SALES_PERIOD' FROM dual UNION ALL
            SELECT 7,1,'DSL_SD','19:00','05:00','B_CDW_DSL_SD','wkf_Load_CDW_DSL_SD' FROM dual UNION ALL
            SELECT 8,1,'DSL_CALL_CENTER','20:00','08:30','B_CDW_DSL_CALL_CENTER','wkf_Load_DSL_CALL_CENTER_CONVERSATION_HIST' FROM dual UNION ALL
            SELECT 9,3,'DSL_AIM','09:30','12:00','B_CDW_DSL_AIM','wkf_Load_DSL_AIM' FROM dual UNION ALL
            SELECT 10,2,'CODS_TN','02:00','11:00','B_CDW_ODS_TN','wkf_Load_CODS_TN' FROM dual UNION ALL
            SELECT 11,2,'ASPEN','18:00','11:00','B_CDW_DSL_ASPEN','wkf_Rollup_Daily' FROM dual UNION ALL
            SELECT 12,2,'CRFTPS-SMS files','07:00','08:00','B_CDW_DSL_PHONEBOOK','wkf_Generate_SMS' FROM dual UNION ALL
            SELECT 13,2,'CRFTPS-Phonebook files','19:33','08:00','B_CDW_DSL_PHONEBOOK','wkf_Generate_PHBK' FROM dual UNION ALL
            SELECT 14,2,'DataMarketplace-ALL','06:00','11:00','B_DATAMKTP','wkf_Load_DATAMKTP' FROM dual UNION ALL
            SELECT 15,3,'SOLR_LUCENE(Daily)','06:20','12:00','B_IAC_SOLR_LUCENE','wkf_Refresh_Solr_Lucene_Index_TNLookup' FROM dual UNION ALL
            SELECT 16,3,'DSL_MARGIN','09:00','12:00','B_CDW_DSL_MARGIN','wkf_Load_DSL_Margin' FROM dual UNION ALL
            SELECT 17,3,'Planned Bill Cost','06:00','12:00','B_CDW_DSL_AML','wkf_Load_AML_PLANNED_COST' FROM dual UNION ALL
            SELECT 18,3,'SDP/Sales Orders (fCTL Data Lake/ASL)','01:00','07:00',
                   'B_CDW_ASL_SDP_ORDER','wkf_Load_CDW_ASL_SDP_ORDER' FROM dual UNION ALL
            SELECT 19,3,'Service Lookup Refresh (SLV)','02:00','12:00',
                   'B_CDW_ERM','wkf_Load_Service_Lookup_Refresh' FROM dual
        ),
        
        /* ============================================================
           2) TARGET SLA DATE LOGIC
           ============================================================ */
        targets AS (
            SELECT
                s.*,
                TRUNC(SYSDATE) report_dt,
                TO_DATE(
                    TO_CHAR(
                        CASE
                            WHEN sla_application IN ('DSL_AIM','DataMarketplace-ALL')
                            THEN TRUNC(SYSDATE) - 1
                            ELSE TRUNC(SYSDATE)
                        END,
                    'YYYY-MM-DD') || ' ' || target_time_mt,
                'YYYY-MM-DD HH24:MI') AS target_sla_dt_mt
            FROM sla_def s
        ),
        
        /* ============================================================
           3) Latest run per app
           ============================================================ */
        latest_run AS (
            SELECT application_name, dependency_name, status_cd, end_dt
            FROM (
                SELECT a.*,
                       ROW_NUMBER() OVER (
                           PARTITION BY UPPER(application_name), UPPER(dependency_name)
                           ORDER BY NVL(end_dt, SYSDATE) DESC
                       ) rn
                FROM icsm.app_control_status a
            )
            WHERE rn = 1
        ),
        
        /* ============================================================
           4) Yesterday completion ONLY for the 4 impacted apps (MT date)
           ============================================================ */
        yday_run_4apps AS (
            SELECT application_name, dependency_name, status_cd, end_dt
            FROM (
                SELECT a.*,
                       ROW_NUMBER() OVER (
                           PARTITION BY UPPER(a.application_name), UPPER(a.dependency_name)
                           ORDER BY a.end_dt DESC
                       ) rn
                FROM icsm.app_control_status a
                JOIN targets t
                  ON UPPER(t.application_name) = UPPER(a.application_name)
                 AND UPPER(t.dependency_name)  = UPPER(a.dependency_name)
                WHERE t.sla_application IN (
                      'DSL_AIM',
                      'DataMarketplace-ALL',
                      'Service Lookup Refresh (SLV)'
                )
                  AND a.end_dt IS NOT NULL
                  AND TRUNC(a.end_dt - (6/24)) = TRUNC(SYSDATE) - 1
            )
            WHERE rn = 1
        ),
        
        /* ============================================================
           5) COMPLETION TIME LOGIC
           ============================================================ */
        calc AS (
            SELECT
                t.report_dt,
                t.app_no,
                t.pri,
                t.sla_application,
                t.start_time_mt,
                t.target_sla_dt_mt,
                lr.status_cd        AS latest_status_cd,
                lr.end_dt           AS latest_end_dt,
                CASE
                    WHEN t.sla_application IN (
                         'DSL_AIM','DataMarketplace-ALL','Service Lookup Refresh (SLV)'
                    )
                    THEN yd.status_cd
                    ELSE lr.status_cd
                END AS status_cd,
                CASE
                    WHEN t.sla_application IN (
                         'DSL_AIM','DataMarketplace-ALL','Service Lookup Refresh (SLV)'
                    )
                    THEN (yd.end_dt - (6/24))
                    WHEN t.sla_application IN ('CDW-DSL-SALES-PERIOD','DSL_CALL_CENTER')
                         AND (lr.end_dt IS NULL OR TRUNC(lr.end_dt - (6/24)) < TRUNC(SYSDATE))
                    THEN NULL
                    ELSE (lr.end_dt - (6/24))
                END AS actual_end_dt_mt
            FROM targets t
            LEFT JOIN latest_run lr
              ON UPPER(lr.application_name) = UPPER(t.application_name)
             AND UPPER(lr.dependency_name)  = UPPER(t.dependency_name)
            LEFT JOIN yday_run_4apps yd
              ON UPPER(yd.application_name) = UPPER(t.application_name)
             AND UPPER(yd.dependency_name)  = UPPER(t.dependency_name)
        )
        
        /* ============================================================
           6) FINAL OUTPUT
           ============================================================ */
        SELECT
            TO_CHAR(report_dt,'MM/DD/YYYY Dy') as "Date",
            app_no as "App#",
            pri as "Pri.",
            sla_application as "SLA Application",
            CASE
                WHEN latest_status_cd IS NULL AND latest_end_dt IS NULL THEN 'No Run'
                WHEN actual_end_dt_mt IS NULL THEN 'Running'
                WHEN status_cd = 'Succeeded' THEN 'Complete'
                WHEN status_cd IS NULL THEN 'Complete'
                ELSE status_cd
            END as "Status",
            start_time_mt as "Start time (MT)",
            CASE
                WHEN actual_end_dt_mt IS NULL THEN NULL
                ELSE TO_CHAR(actual_end_dt_mt,'YYYY/MM/DD HH24:MI')
            END as "Actual Completion Time (MT)",
            TO_CHAR(target_sla_dt_mt,'YYYY/MM/DD HH24:MI') as "Target SLA (MT)",
            CASE
                WHEN actual_end_dt_mt IS NULL THEN NULL
                ELSE ROUND((target_sla_dt_mt - actual_end_dt_mt) * 1440)
            END as "SLA Met By (Minutes)",
            CASE
                WHEN actual_end_dt_mt IS NULL THEN NULL
                WHEN (target_sla_dt_mt - actual_end_dt_mt) >= 0 THEN 'Met'
                ELSE 'Miss'
            END as "Met or Miss?"
        FROM calc
        ORDER BY app_no
        """
        
        # Execute the query and return results
        import logging
        logger = logging.getLogger('bi_service')
        
        results = fetch_all(query)
        logger.info(f"BI Status Query returned {len(results) if results else 0} rows")
        
        if not results:
            logger.warning("BI Status Query returned no results")
            return []
        
        # Inspect first row to see available keys
        if results:
            logger.info(f"Available column keys: {list(results[0].keys())}")
        
        # Convert results to a more template-friendly format with normalized keys
        # Note: fetch_all converts column names to lowercase
        formatted_results = []
        for row in results:
            formatted_row = {
                'date': row.get('date'),
                'app_no': row.get('app#'),
                'priority': row.get('pri.'),
                'sla_application': row.get('sla application'),
                'status': row.get('status'),
                'start_time': row.get('start time (mt)'),
                'actual_completion': row.get('actual completion time (mt)'),
                'target_sla': row.get('target sla (mt)'),
                'sla_met_by_minutes': row.get('sla met by (minutes)'),
                'met_or_miss': row.get('met or miss?'),
            }
            formatted_results.append(formatted_row)
        
        logger.info(f"Formatted {len(formatted_results)} BI Status Query rows for template")
        return formatted_results
    except Exception as e:
        import logging
        logger = logging.getLogger('bi_service')
        logger.error(f"Error fetching BI Status Query: {e}")
        import traceback
        traceback.print_exc()
        return []