# portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # Optional apps cards page
    path("dashboards/", views.dashboards, name="dashboards"),

    # App dashboards + report view
    path("dashboards/<slug:app_slug>/", views.app_dashboards, name="app_dashboards"),
    path("dashboards/<slug:app_slug>/<slug:report_slug>/", views.report_view, name="report_view"),
    
    path("", views.home, name="home"),
    path("dashboards/", views.dashboards, name="dashboards"),
    path("dashboards/<slug:app_slug>/", views.app_dashboards, name="app_dashboards"),
    path("dashboards/<slug:app_slug>/<slug:report_slug>/", views.report_view, name="report_view"),

    # ✅ Portal-native Level3 report
    path("reports/level3/failed-job-status/", views.level3_failed_job_status, name="level3_failed_job_status"),

]

