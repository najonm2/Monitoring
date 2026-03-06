# portal/services/bi_service.py
from portal.db.oracle_client import fetch_all
from datetime import datetime, timedelta


# Application mapping with SLA details
APP_SLA_CONFIG = {
    1: {
        "name": "CDW-ASR ODS",
        "priority": 1,
        "category": "",
        "start_time": "15:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
    },
    2: {
        "name": "CDW-AML",
        "priority": 1,
        "category": "",
        "start_time": "11:00",
        "target_sla_time": "09:00",
        "target_next_day": True,
    },
    3: {
        "name": "CDW-Orders ODS",
        "priority": 1,
        "category": "",
        "start_time": "12:00",
        "target_sla_time": "07:00",
        "target_next_day": True,
    },
    4: {
        "name": "CDW-Network Inventory ODS",
        "priority": 1,
        "category": "",
        "start_time": "21:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
    },
    6: {
        "name": "DSL_FINANCE_DAILY_REFRESH_MASTER",
        "priority": 1,
        "category": "",
        "start_time": "Various",
        "target_sla_time": "Various",
        "target_next_day": False,
    },
    7: {
        "name": "DSL_ERP_20",
        "priority": 1,
        "category": "",
        "start_time": "20:00",
        "target_sla_time": "00:00",
        "target_next_day": True,
    },
    8: {
        "name": "DSL_ERP_00",
        "priority": 1,
        "category": "",
        "start_time": "00:00",
        "target_sla_time": "04:00",
        "target_next_day": False,
    },
    9: {
        "name": "DSL_ERP_04",
        "priority": 1,
        "category": "",
        "start_time": "04:00",
        "target_sla_time": "08:00",
        "target_next_day": False,
    },
    11: {
        "name": "SMMART",
        "priority": 1,
        "category": "",
        "start_time": "19:00",
        "target_sla_time": "03:30",
        "target_next_day": True,
    },
    12: {
        "name": "CDW-DSL-SALES-PERIOD / DSL_CALL_CENTER",
        "priority": 1,
        "category": "",
        "start_time": "03:00 / 20:00",
        "target_sla_time": "11:00 / 08:30",
        "target_next_day": True,
    },
    13: {
        "name": "VSUM Mart",
        "priority": 1,
        "category": "",
        "start_time": "19:00",
        "target_sla_time": "09:00",
        "target_next_day": True,
    },
    14: {
        "name": "IPDS / DataMarketplace",
        "priority": 2,
        "category": "",
        "start_time": "Various",
        "target_sla_time": "11:00",
        "target_next_day": False,
    },
    15: {
        "name": "DSL_SD",
        "priority": 2,
        "category": "",
        "start_time": "19:00",
        "target_sla_time": "05:00",
        "target_next_day": True,
    },
    16: {
        "name": "CODS_TN",
        "priority": 2,
        "category": "",
        "start_time": "02:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
    },
    18: {
        "name": "FEDW / ASPEN",
        "priority": 2,
        "category": "",
        "start_time": "18:00",
        "target_sla_time": "11:00 / 11:00",
        "target_next_day": True,
    },
    19: {
        "name": "CRFTPS-SMS files",
        "priority": 2,
        "category": "",
        "start_time": "07:00",
        "target_sla_time": "08:00",
        "target_next_day": False,
    },
    20: {
        "name": "ASPEN",
        "priority": 2,
        "category": "",
        "start_time": "18:00",
        "target_sla_time": "11:00",
        "target_next_day": True,
    },
    21: {
        "name": "CRFTPS-SMS files",
        "priority": 2,
        "category": "",
        "start_time": "07:00",
        "target_sla_time": "08:00",
        "target_next_day": False,
    },
    22: {
        "name": "CRFTPS-Phonebook files / CIIT",
        "priority": 2,
        "category": "",
        "start_time": "19:33 / 06:00",
        "target_sla_time": "08:00 / 12:00",
        "target_next_day": True,
    },
    23: {
        "name": "CIIT",
        "priority": 2,
        "category": "",
        "start_time": "06:00",
        "target_sla_time": "12:00",
        "target_next_day": False,
    },
    24: {
        "name": "ATLASMART / CTL-EDW ORDER",
        "priority": 3,
        "category": "",
        "start_time": "22:05",
        "target_sla_time": "06:00",
        "target_next_day": True,
    },
    25: {
        "name": "SOLR_LUCENE / CTL-EDW REVENUE",
        "priority": 3,
        "category": "",
        "start_time": "06:20 / 00:23",
        "target_sla_time": "12:00 / 06:00",
        "target_next_day": False,
    },
    26: {
        "name": "GSFDMART / DSL_AIM / CTL-EDW PRODUCT",
        "priority": 3,
        "category": "",
        "start_time": "21:50",
        "target_sla_time": "06:00",
        "target_next_day": True,
    },
    27: {
        "name": "SOLR_LUCENE(Daily)",
        "priority": 3,
        "category": "",
        "start_time": "06:20",
        "target_sla_time": "12:00",
        "target_next_day": False,
    },
    28: {
        "name": "DSL_AIM / DSL_MARGIN",
        "priority": 3,
        "category": "",
        "start_time": "09:30 / 09:00",
        "target_sla_time": "12:00",
        "target_next_day": False,
    },
    29: {
        "name": "Planned Bill Cost / Service Lookup Refresh",
        "priority": 3,
        "category": "",
        "start_time": "06:00 / 02:00",
        "target_sla_time": "12:00",
        "target_next_day": False,
    },
    30: {
        "name": "NINA CONTROLLER",
        "priority": 3,
        "category": "",
        "start_time": "18:00",
        "target_sla_time": "07:00",
        "target_next_day": True,
    },
    32: {
        "name": "SDP/Sales Orders (CTL Data Lake/ASL)",
        "priority": 3,
        "category": "",
        "start_time": "01:00",
        "target_sla_time": "07:00",
        "target_next_day": True,
    },
    33: {
        "name": "CAPEX",
        "priority": 1,
        "category": "",
        "start_time": "Various (3hr cycles)",
        "target_sla_time": "+3 hours",
        "target_next_day": False,
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
    Returns: rows_list with enriched data
    """
    try:
        query = """
        /* ============================================================
           Level3 BI Feed - Only applications in ICSM database
           ============================================================ */
        SELECT excel_no,
               application_name,
               dependency_name,
               end_dt_in_mst
        FROM (
            /* 1 - CDW-ASR ODS */
            SELECT 1 AS excel_no, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR') AS end_dt_in_mst
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_ODS_OFFNET'
              AND dependency_name  = 'wkf_Load_ASR'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 2 - CDW-AML */
            SELECT 2, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_AML'
              AND dependency_name  = 'wkf_Load_AML_ALL'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 3 - CDW-Orders ODS */
            SELECT 3, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_ODS'
              AND dependency_name  = 'wkf_LOAD_ODS_LEAD_TO_ORDER'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 4 - CDW-Network Inventory ODS */
            SELECT 4, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_ODS_NETEX'
              AND dependency_name  = 'wkf_Load_NETEX_SUPPLIER_INV_DETAIL'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 11 - SAMART */
            SELECT 11, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name LIKE '%B_SAMART%'
              AND dependency_name  = 'wkf_PROD_Load_F_PROV_ORDER_ALL'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 11 - SMMART */
            SELECT 11, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name LIKE '%B_SMMART%'
              AND dependency_name  = 'wkf_SMMART_Controller'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 12 - CDW-DSL-SALES-PERIOD */
            SELECT 12, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_SALES_PERIOD'
              AND dependency_name  = 'wkf_Load_DSL_SALES_PERIOD'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 12 - Call Center */
            SELECT 12, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_CALL_CENTER'
              AND dependency_name  = 'wkf_Load_DSL_CALL_CENTER_CONVERSATION_HIST'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 15 - DSL_SD */
            SELECT 15, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_SD'
              AND dependency_name  = 'wkf_Load_CDW_DSL_SD'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 19 - IPBUS_CPIP */
            SELECT 19, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_IPBUS_CPIP'
              AND dependency_name  = 'wkf_Load_Summary_Tables_Main'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 20 - DSL_ASPEN */
            SELECT 20, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_ASPEN'
              AND dependency_name  = 'wkf_Rollup_Daily'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 21 - DSL_PHONEBOOK (SMS) */
            SELECT 21, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_PHONEBOOK'
              AND dependency_name  = 'wkf_Generate_SMS'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 22 - DSL_PHONEBOOK (PHBK) */
            SELECT 22, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_PHONEBOOK'
              AND dependency_name  = 'wkf_Generate_PHBK'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 25 - SOLR_LUCENE */
            SELECT 25, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_IAC_SOLR_LUCENE'
              AND dependency_name  = 'wkf_Refresh_Solr_Lucene_Index_TNLookup'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 26 - LDW_DSL_GSFDMART */
            SELECT 26, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_LDW_DSL_GSFDMART'
              AND dependency_name  = 'wkf_Load_F_GSFD_DTL'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 26 - CDW_DSL_AIM */
            SELECT 26, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_AIM'
              AND dependency_name  = 'wkf_Load_DSL_AIM'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 28 - DSL_MARGIN */
            SELECT 28, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_MARGIN'
              AND dependency_name  = 'wkf_Load_DSL_Margin'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 29 - DSL_AML (PLANNED_COST) */
            SELECT 29, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_DSL_AML'
              AND dependency_name  = 'wkf_Load_AML_PLANNED_COST'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 29 - CDW_ERM */
            SELECT 29, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_ERM'
              AND dependency_name  = 'wkf_Load_Service_Lookup_Refresh'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 30 - NINA_CONTROLLER */
            SELECT 30, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'NINA_CONTROLLER'
              AND dependency_name  = 'ETL_AUDIT'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name

            UNION ALL
            /* 32 - CDW_ASL_SDP_ORDER */
            SELECT 32, application_name, dependency_name,
                   MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR')
            FROM ICSM.app_control_status
            WHERE application_name = 'B_CDW_ASL_SDP_ORDER'
              AND dependency_name  = 'wkf_Load_CDW_ASL_SDP_ORDER'
              AND status_cd        = 'Succeeded'
            GROUP BY application_name, dependency_name
        )
        ORDER BY excel_no, application_name, dependency_name
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
                "target_sla_time_mt": config.get("target_sla_time", ""),
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
                    # Create target SLA datetime based on job start date (inferred from completion)
                    target_time_str = config.get("target_sla_time")
                    target_next_day = config.get("target_next_day", False)
                    start_time_str = config.get("start_time")
                    
                    if target_time_str and target_time_str not in ["Various", "+3 hours"]:
                        target_hour, target_min = map(int, target_time_str.split(":"))
                        start_hour, start_min = map(int, start_time_str.split(":"))
                        
                        # Infer the job's start date from completion time and start time
                        completion_datetime = end_dt_in_mst
                        completion_time = completion_datetime.time()
                        completion_date = completion_datetime.date()
                        
                        # If completion time is before start time, job started previous day
                        start_time_obj = datetime.min.time().replace(hour=start_hour, minute=start_min)
                        if completion_time < start_time_obj:
                            # Job started yesterday
                            job_start_date = completion_date - timedelta(days=1)
                        else:
                            # Job started today
                            job_start_date = completion_date
                        
                        # Calculate target SLA based on job start date
                        target_sla = datetime.combine(job_start_date, datetime.min.time()).replace(
                            hour=target_hour, minute=target_min, second=0, microsecond=0
                        )
                        
                        if target_next_day:
                            target_sla += timedelta(days=1)
                        
                        # Calculate difference in minutes
                        sla_minutes = calculate_sla_met_miss(end_dt_in_mst, target_sla)
                        enriched_row["sla_met_miss_min"] = sla_minutes
                        enriched_row["sla_met_miss_formatted"] = str(sla_minutes)  # Show as minutes, not hh:mm
                        enriched_row["met_or_miss"] = "Miss" if sla_minutes and sla_minutes < 0 else "Met"
                        enriched_row["target_sla_time_mt"] = target_sla.strftime("%Y/%m/%d %H:%M")
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
    Returns: rows_list
    """
    try:
        query = """
        SELECT  
            APPLICATION_NAME,
            DEPENDENCY_NAME, 
            new_time(start_dt,'GMT','MST') AS START_DATE_MDT,
            new_time(end_dt,'GMT','MST') AS END_DATE_MDT,
            round(((3*60) - (end_dt-start_dt)*24*60), 0) as SLA_Met_Miss_MIN, 
            start_dt as START_DT_GMT, 
            end_dt as END_DT_GMT,
            status_cd 
        FROM (
            select * from ICSM.app_control_status 
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
