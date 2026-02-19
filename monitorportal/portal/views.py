from django.shortcuts import render
from django.http import Http404
from .ssrs_registry import APPS
from portal.services.level3_service import get_level3_failed_jobs

def home(request):
    # you already show user_display in home.html [3](https://centurylink-my.sharepoint.com/personal/naresh_m_lumen_com/Documents/Microsoft%20Copilot%20Chat%20Files/urls.py)
    ctx = {"user_display": request.user.username if request.user.is_authenticated else "Guest"}
    return render(request, "portal/home.html", ctx)

def dashboards(request):
    # Optional page: show applications as cards (your dashboards_home.html) [1](https://centurylink-my.sharepoint.com/personal/naresh_m_lumen_com/Documents/Microsoft%20Copilot%20Chat%20Files/settings.py)
    return render(request, "portal/dashboards_home.html", {"apps": APPS})

def app_dashboards(request, app_slug):
    app = next((a for a in APPS if a["slug"] == app_slug), None)
    if not app:
        raise Http404("Application not found")
    return render(request, "portal/app_dashboards.html", {
        "app": app,
        "reports": app.get("reports", []),
    })

def report_view(request, app_slug, report_slug):
    app = next((a for a in APPS if a["slug"] == app_slug), None)
    if not app:
        raise Http404("Application not found")

    report = next((r for r in app.get("reports", []) if r["slug"] == report_slug), None)
    if not report:
        raise Http404("Report not found")

    return render(request, "portal/report_view.html", {"app": app, "report": report})

def dashboard_view(request, app_slug, dash_slug):
    # If you have "dashboards" separate from reports, extend registry similarly.
    # Keeping placeholder consistent with your dashboard_view.html structure. [1](https://centurylink-my.sharepoint.com/personal/naresh_m_lumen_com/Documents/Microsoft%20Copilot%20Chat%20Files/settings.py)
    raise Http404("Not implemented yet")

def level3_failed_job_status(request):
    """
    Portal-native version of 'LVL3 FAILED JOB STATUS UPDATED'
    Pulls data from Oracle using the same RDL dataset logic.
    """
    cache_key = "lvl3_failed_job_status_v1"
    cached = cache.get(cache_key)
    if cached:
        return render(request, "portal/level3_failed_job_status.html", cached)

    kpis, failed_list, long_running = get_level3_failed_job_status_data()
    ctx = {
        "kpis": kpis,
        "failed_list": failed_list,
        "long_running": long_running,
    }

    # cache for 60 seconds to reduce DB load
    cache.set(cache_key, ctx, 60)
    return render(request, "portal/level3_failed_job_status.html", ctx)


def level3_failed_job_status(request):
    summary_map, main_rows, long_rows = get_level3_failed_jobs()
    ctx = {
        "summary": summary_map,
        "failed": main_rows,
        "long_running": long_rows,
    }
    return render(request, "portal/level3_failed_job_status.html", ctx)