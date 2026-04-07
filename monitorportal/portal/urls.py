# portal/urls.py
from django.urls import path
from . import views
from . import api_views
from . import ai_views

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
    
    # Informatica Workflow Restart API
    path("api/informatica/restart-workflow/", api_views.restart_workflow, name="restart_workflow"),
    path("api/informatica/check-workflow-status/", api_views.check_workflow_status, name="check_workflow_status"),
    
    # Level3 BI Report
    path("level3-bi/", views.level3_bi_report, name="level3_bi_report"),
    
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

