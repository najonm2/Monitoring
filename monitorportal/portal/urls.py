# portal/urls.py
from django.urls import path
from . import views
from . import api_views
from . import ai_views
from . import informatica_credentials_views

urlpatterns = [
    # Home
    path("", views.home, name="home"),
    
    # Applications & Reports
    path("dashboards/", views.dashboards, name="dashboards"),
    path("dashboards/mdm/", views.mdm_job_status, name="app_dashboards_mdm"),  # Direct access to MDM job status
    path("dashboards/erp/", views.erp_job_status, name="app_dashboards_erp"),  # Direct access to ERP job status
    path("dashboards/<slug:app_slug>/", views.app_dashboards, name="app_dashboards"),
    path("dashboards/<slug:app_slug>/<slug:report_slug>/", views.report_view, name="report_view"),
    
    # API Endpoints
    path("api/reports/<slug:app_slug>/<slug:report_slug>/", api_views.api_report_data, name="api_report_data"),
    path("api/level3/today-job-details/", api_views.level3_today_job_details, name="level3_today_job_details"),
    path("api/level3/failed-jobs-details/", api_views.level3_failed_jobs_details, name="level3_failed_jobs_details"),
    path("api/level3/application-monitoring/", api_views.application_monitoring_data, name="application_monitoring_data"),
    
    # ICSM API
    path("api/icsm/check-entry/", api_views.icsm_check_entry, name="icsm_check_entry"),
    
    # BI Report Comments API
    path("api/bi-report/comments/", api_views.bi_report_comments, name="bi_report_comments"),
    path("api/bi-report/comment/save/", api_views.save_bi_report_comment, name="save_bi_report_comment"),
    path("api/bi-report/comment/delete/", api_views.delete_bi_report_comment, name="delete_bi_report_comment"),
    
    # Informatica Workflow Restart API
    path("api/informatica/restart-workflow/", api_views.restart_workflow, name="restart_workflow"),
    path("api/informatica/check-workflow-status/", api_views.check_workflow_status, name="check_workflow_status"),
    path("api/informatica/restart-with-options/", api_views.restart_workflow_with_options, name="restart_workflow_with_options"),
    path("api/informatica/stop-workflow/", api_views.stop_workflow, name="stop_workflow"),
    path("api/informatica/schedule-workflow/", api_views.schedule_workflow, name="schedule_workflow"),
    path("api/informatica/scheduled-workflows/", api_views.get_scheduled_workflows, name="get_scheduled_workflows"),
    path("api/informatica/test-connection/", api_views.test_informatica_connection, name="test_informatica_connection"),
    path("api/informatica/folders/", api_views.get_informatica_folders, name="get_informatica_folders"),
    path("api/informatica/workflows/", api_views.get_informatica_workflows, name="get_informatica_workflows"),
    path("api/informatica/tasks/", api_views.get_informatica_tasks, name="get_informatica_tasks"),
    path("api/informatica/workflow-status/", api_views.get_workflow_session_status, name="get_workflow_session_status"),
    path("api/informatica/workflow-status-any-folder/", api_views.get_workflow_session_status_any_folder, name="get_workflow_session_status_any_folder"),
    
    # Informatica Manual Restart and Stop Pages
    # Informatica Login and Authentication
    path("informatica/login/", informatica_credentials_views.informatica_login, name="informatica_login"),
    path("informatica/logout/", informatica_credentials_views.informatica_logout, name="informatica_logout"),
    path("informatica/guest-restricted/", informatica_credentials_views.guest_restricted, name="guest_restricted"),
    
    # Informatica Manual Operations (requires credentials)
    path("informatica/manual-restart/", views.manual_informatica_restart, name="manual_informatica_restart"),
    path("informatica/manual-stop/", views.manual_informatica_stop, name="manual_informatica_stop"),
    path("informatica/schedule-workflow/", views.schedule_workflow_page, name="schedule_workflow_page"),
    path("informatica/workflow-status/", views.workflow_status_checker, name="workflow_status_checker"),
    
    # Informatica Credentials Management
    path("informatica/credentials/", informatica_credentials_views.informatica_credentials, name="informatica_credentials"),
    path("api/informatica/credentials/clear/", informatica_credentials_views.clear_credentials, name="clear_informatica_credentials"),
    path("api/informatica/credentials/check/", informatica_credentials_views.check_credentials, name="check_informatica_credentials"),
    
    # Level3 BI Report
    path("level3-bi/", views.level3_bi_report, name="level3_bi_report"),
    
    # Application-wise Monitoring
    path("application-monitoring/", views.application_monitoring, name="application_monitoring"),
    
    # DH Health Dashboard
    path("dh-health/", views.dh_health_dashboard, name="dh_health_dashboard"),
    
    # AI Dashboard and Endpoints
    path("ai/", ai_views.ai_dashboard, name="ai_dashboard"),
    path("ai/api/run-analysis/", ai_views.run_analysis, name="ai_run_analysis"),
    path("ai/api/insights/", ai_views.get_insights_summary, name="ai_insights"),
    path("ai/api/anomalies/", ai_views.get_anomalies, name="ai_anomalies"),
    path("ai/api/predictions/", ai_views.get_predictions, name="ai_predictions"),
    path("ai/api/patterns/", ai_views.get_patterns, name="ai_patterns"),
    path("ai/api/alerts/", ai_views.get_alerts, name="ai_alerts"),
    path("ai/api/analyze-error/", ai_views.analyze_error_api, name="ai_analyze_error"),
    path("ai/api/status/", ai_views.get_agent_status, name="ai_status"),
    
    # Backward compatibility - Level3
    path("reports/level3/failed-job-status/", views.level3_failed_job_status, name="level3_failed_job_status"),
    
    # ERP and MDM with AI insights
    path("reports/erp/job-status/", views.erp_job_status, name="erp_job_status"),
    path("reports/mdm/job-status/", views.mdm_job_status, name="mdm_job_status"),
]

