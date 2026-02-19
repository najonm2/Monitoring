# portal/ssrs_registry.py
# Central registry for Applications + SSRS reports

APPS = [
    {
        "name": "Level3 Application",
        "slug": "level3",
        "description": "Level3 SSRS Monitoring Dashboards",
        "reports": [
            {
                "name": "Level3 Failed Job Status",
                "slug": "lvl3-failed-job-status",
                "description": "LVL3 FAILED JOB STATUS UPDATED",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20FAILED%20JOB%20STATUS%20UPDATED",
                "portal_url_name": "level3_failed_job_status",
            },
            {
                "name": "Failed with Error",
                "slug": "lvl3-failed-with-error",
                "description": "LVL3 FAILED SESSIONS WITH ERRORS",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20FAILED%20SESSIONS%20WITH%20ERRORS",
            },
            {
                "name": "Long Running Sessions",
                "slug": "lvl3-long-running-sessions",
                "description": "LVL3 Long Running List Session level",
                "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20Long%20Running%20List%20Session%20level",
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
            }
        ],
    },
]

{
  "name": "Level3 Failed Job Status",
  "slug": "lvl3-failed-job-status",
  "description": "LVL3 FAILED JOB STATUS UPDATED",
  "ssrs_url": "http://usidcvssrs0005/Reports/report/DWBIPASE/UAT%20Folder/LVL3%20FAILED%20JOB%20STATUS%20UPDATED",
  "portal_url_name": "level3_failed_job_status",
}