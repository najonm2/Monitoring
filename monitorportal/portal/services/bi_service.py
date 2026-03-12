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
