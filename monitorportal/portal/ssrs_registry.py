# portal/ssrs_registry.py
# Central registry for Applications + SSRS reports

APPS = [
    {
        "name": "Level3 Application",
        "slug": "level3",
        "description": "Level3 SSRS Monitoring Dashboards",
        "reports": [
            {
                "name": "LVL3 Failed Jobs Status",
                "slug": "lvl3-failed-jobs-status",
                "description": "LVL3 FAILED JOB STATUS - Track failed, completed after restart, pending, and running jobs",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20FAILED%20JOB%20STATUS%20UPDATED",
                "view_type": "level3_failed_jobs_status",
            },
            {
                "name": "Level3 Failures with Error",
                "slug": "lvl3-failed-with-error",
                "description": "LVL3 FAILED SESSIONS WITH ERRORS",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20FAILED%20SESSIONS%20WITH%20ERRORS",
                "view_type": "level3_error",
            },
            {
                "name": "Long Running Sessions",
                "slug": "lvl3-long-running-sessions",
                "description": "LVL3 Long Running List Session level",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20Long%20Running%20List%20Session%20level",
                "view_type": "level3_long_running",
            },
            {
                "name": "All Level3 job Status",
                "slug": "lvl3-all-jobs-status",
                "description": "ALL LEVEL3 JOBS STATUS",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/ALL%20LEVEL3%20JOBS%20STATUS",
                "view_type": "level3_all_jobs",
            },
            {
                "name": "LVL3 7-Day Job Insights",
                "slug": "lvl3-7day-insights",
                "description": "Level3 7-Day Job Performance Trends by Date",
                "ssrs_url": "",
                "view_type": "level3_7day_insights",
            },
        ],
    },
    {
        "name": "MDM Application",
        "slug": "mdm",
        "description": "MDM SSRS Monitoring Dashboard",
        "reports": [
            {
                "name": "MDM Job Status",
                "slug": "mdm-job-status",
                "description": "MDM JOB STATUS",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/ADF/MDM%20JOB%20STATUS",
                "view_type": "mdm_job_status",
                "portal_url_name": "mdm_job_status",
            }
        ],
    },
    {
        "name": "ERP Application",
        "slug": "erp",
        "description": "ERP SSRS Monitoring Dashboard",
        "reports": [
            {
                "name": "ERP Job Status Latest",
                "slug": "erp-job-status-latest",
                "description": "ERP JOB STATUS Latest",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/ERP%20JOB%20STATUS%20Latest",
                "view_type": "erp_job_status",
                "portal_url_name": "erp_job_status",
            }
        ],
    },
    {
        "name": "ADF Application",
        "slug": "adf",
        "description": "Azure Data Factory (ADF) & Databricks Monitoring Dashboard",
        "reports": [
            {
                "name": "ADF Status",
                "slug": "adf-status",
                "description": "ADF Pipeline Status Overview",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/ADF/ADFStatus",
                "view_type": "adf_status",
            },
            {
                "name": "Databricks Status",
                "slug": "databricks-status",
                "description": "Databricks Job Status Overview",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/ADF/DatabricksStatus",
                "view_type": "databricks_status",
            },
            {
                "name": "Databricks & ADF Failed Jobs",
                "slug": "databricks-adf-failed",
                "description": "Databricks and ADF Failed Jobs Combined Report",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/ADF/DATABRICKS_AND_ADF_FAILED_JOBS",
                "view_type": "databricks_adf_failed",
            }
        ],
    },
]