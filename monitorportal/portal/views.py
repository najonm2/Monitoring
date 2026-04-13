from django.shortcuts import render
from django.http import Http404
from django.views.decorators.http import require_http_methods
from .ssrs_registry import APPS


def home(request):
    return render(request, "portal/home.html")


def dashboards(request):
    return render(request, "portal/dashboards_home.html", {"apps": APPS})


def app_dashboards(request, app_slug):
    app = next((a for a in APPS if a["slug"] == app_slug), None)
    if not app:
        raise Http404("Application not found")
    
    context = {
        "app": app,
        "reports": app.get("reports", []),
    }
    
    # Add Level3 TODAY stats only (no 7-day insights on main page)
    if app_slug == "level3":
        try:
            from portal.services.level3_service import get_level3_jobs_today_only, get_level3_folders_with_metrics
            from django.core.cache import cache
            
            # Cache for 2 minutes to avoid slow repeated DB calls
            cache_key = 'level3_dashboard_data'
            cached = cache.get(cache_key)
            
            if cached:
                context["today_stats"] = cached["today_stats"]
                context["folders"] = cached["folders"]
            else:
                # Add only TODAY stats
                today_stats = get_level3_jobs_today_only()
                from datetime import datetime
                today_stats['date'] = datetime.now()
                today_stats['date_str'] = 'TODAY'
                
                # Add folders with 7-day metrics
                folders = get_level3_folders_with_metrics()
                
                context["today_stats"] = today_stats
                context["folders"] = folders
                
                # Cache for 2 minutes
                cache.set(cache_key, {"today_stats": today_stats, "folders": folders}, 120)
        except Exception as e:
            print(f"Error loading Level3 TODAY stats: {e}")
            context["today_stats"] = None
            context["folders"] = []
    
    return render(request, "portal/app_dashboards.html", context)


@require_http_methods(["GET"])
def report_view(request, app_slug, report_slug):
    """
    Render report view page (data loaded via API or directly)
    Handles special view types with custom data loading
    """
    from django.shortcuts import redirect
    
    app = next((a for a in APPS if a["slug"] == app_slug), None)
    if not app:
        raise Http404("Application not found")

    report = next((r for r in app.get("reports", []) if r["slug"] == report_slug), None)
    if not report:
        raise Http404("Report not found")
    
    # Handle redirect view type
    if report.get("view_type") == "redirect" and report.get("redirect_url"):
        return redirect(report["redirect_url"])

    ctx = {
        "app": app,
        "report": report,
    }
    
    # Handle special view types with custom data loading
    view_type = report.get("view_type", "")
    
    # Level3 Failed Jobs Status - Summary + Failed Jobs List
    if view_type == "level3_failed_jobs_status":
        from portal.services.level3_service import get_level3_failed_jobs_status, get_level3_folders_with_metrics
        from django.core.cache import cache
        from datetime import datetime
        
        # Cache for 2 minutes
        cache_key = 'level3_failed_jobs_status_data'
        cached = cache.get(cache_key)
        
        if cached:
            ctx.update(cached)
            ctx["current_date"] = datetime.now()
        else:
            try:
                summary, failed_jobs = get_level3_failed_jobs_status()
                folders = get_level3_folders_with_metrics()
                ctx["summary"] = summary
                ctx["failed_jobs"] = failed_jobs
                ctx["folders"] = folders
                ctx["current_date"] = datetime.now()
                
                cache.set(cache_key, {
                    "summary": summary,
                    "failed_jobs": failed_jobs,
                    "folders": folders,
                }, 120)
            except Exception as e:
                print(f"Error loading Level3 failed jobs status: {e}")
                ctx["summary"] = {
                    'total_failed': 0,
                    'completed_after_restart': 0,
                    'pending_jobs': 0,
                    'restarted_running': 0
                }
                ctx["failed_jobs"] = []
                ctx["folders"] = []
                ctx["current_date"] = datetime.now()
        
        return render(request, "portal/level3_failed_jobs_status.html", ctx)
    
    # Level3 7-Day Insights - Historical Performance
    elif view_type == "level3_7day_insights":
        from portal.services.level3_service import get_level3_jobs_last_7_days_optimized, get_level3_jobs_by_folder_7_days
        
        # Get folder filter from query params
        folder_filter = request.GET.get('folder', None)
        
        try:
            if folder_filter:
                # Show 7-day insights for specific folder
                daily_stats = get_level3_jobs_by_folder_7_days(folder_filter)
                ctx["folder_name"] = folder_filter
            else:
                # Show overall 7-day insights
                daily_stats = get_level3_jobs_last_7_days_optimized()
                ctx["folder_name"] = None
                
            if daily_stats and len(daily_stats) > 0:
                ctx["today_stats"] = daily_stats[0]
                ctx["historical_days"] = daily_stats[1:]
                ctx["total_stats"] = {
                    'succeeded': sum(day.get('succeeded', 0) for day in daily_stats),
                    'failed': sum(day.get('failed', 0) for day in daily_stats),
                    'running': sum(day.get('running', 0) for day in daily_stats),
                    'stopped': sum(day.get('stopped', 0) for day in daily_stats),
                    'disabled': sum(day.get('disabled', 0) for day in daily_stats),
                    'total': sum(day.get('total', 0) for day in daily_stats),
                }
            else:
                ctx["today_stats"] = None
                ctx["historical_days"] = []
                ctx["total_stats"] = None
        except Exception as e:
            print(f"Error loading Level3 7-day insights: {e}")
            import traceback
            traceback.print_exc()
            ctx["today_stats"] = None
            ctx["historical_days"] = []
            ctx["total_stats"] = None
            ctx["folder_name"] = None
        
        return render(request, "portal/level3_7day_insights.html", ctx)
    
    
    # Default: Generic report view with API data loading
    return render(request, "portal/report_view.html", ctx)


def level3_failed_job_status(request):
    from django.core.cache import cache


def level3_bi_report(request):
    """
    Level3 BI Report view showing BI Feed, CAPEX details, BI Status Query, and ERP Status
    OPTIMIZED: Cached for 3 minutes to improve performance
    """
    from portal.services.bi_service import get_level3_bi_feed, get_capex_details, get_bi_status_query
    from portal.erp_mdm_insights import get_erp_run_history
    from django.core.cache import cache
    
    # Try to get cached data (cache for 3 minutes)
    cache_key = 'level3_bi_report_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        # Use cached data
        context = cached_data
    else:
        # Fetch fresh data
        context = {
            "bi_feed_data": [],
            "capex_data": [],
            "bi_status_data": [],
            "erp_data": {},
            "error": None,
        }
        
        try:
            context["bi_feed_data"] = get_level3_bi_feed()
            context["capex_data"] = get_capex_details()
            context["bi_status_data"] = get_bi_status_query()
            context["erp_data"] = get_erp_run_history()
            
            # Cache the successful result for 3 minutes
            cache.set(cache_key, context, 180)
        except Exception as e:
            context["error"] = str(e)
            print(f"Error loading Level3 BI Report: {e}")
    
    return render(request, "portal/level3_bi_report.html", context)


def level3_failed_job_status(request):
    from django.core.cache import cache
    from portal.services.level3_service import (
        get_level3_failed_with_error, 
        get_level3_long_running, 
        get_level3_jobs_last_7_days_optimized,
        get_level3_jobs_by_date
    )
    from portal.practical_insights import get_practical_insights
    import time
    
    # Try to get cached data (cache for 2 minutes)
    cache_key = 'level3_job_status_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        # Use cached data
        failed_rows = cached_data['failed_rows']
        long_running = cached_data['long_running']
        ai_insights = cached_data['ai_insights']
        daily_stats = cached_data.get('daily_stats', [])
    else:
        # Fetch fresh data (only once, not duplicate queries)
        start_time = time.time()
        failed_rows = get_level3_failed_with_error()
        long_running = get_level3_long_running()
        
        # Fetch 7-day statistics using optimized separate queries
        daily_stats = get_level3_jobs_last_7_days_optimized()
        
        # Pass data to AI insights to avoid duplicate queries
        ai_insights = get_practical_insights(
            long_running=long_running,
            failed_with_errors=failed_rows,
            all_failed=failed_rows  # Use failed_with_errors as all_failed
        )
        
        # Cache the results for 2 minutes (120 seconds)
        cache.set(cache_key, {
            'failed_rows': failed_rows,
            'long_running': long_running,
            'ai_insights': ai_insights,
            'daily_stats': daily_stats,
        }, 120)
        
        fetch_time = time.time() - start_time
        print(f"[PERFORMANCE] Data fetched in {fetch_time:.2f} seconds")
    
    # Prepare flash messages for critical issues
    flash_messages = []
    if ai_insights.get('success'):
        critical_count = ai_insights.get('summary', {}).get('critical_issues', 0)
        if critical_count > 0:
            flash_messages.append({
                'type': 'error',
                'message': f'🚨 CRITICAL: {critical_count} critical issues require immediate attention!'
            })
        
        dba_count = ai_insights.get('summary', {}).get('dba_tasks_count', 0)
        dev_count = ai_insights.get('summary', {}).get('dev_tasks_count', 0)
        
        if dba_count > 0:
            flash_messages.append({
                'type': 'warning',
                'message': f'⚠️ DBA TEAM: {dba_count} database-related issues need attention'
            })
        
        if dev_count > 0:
            flash_messages.append({
                'type': 'info',
                'message': f'ℹ️ DEV TEAM: {dev_count} ETL/code issues need review'
            })
    
    # Create summary from distinct records
    summary = {
        "total_failed": len(failed_rows),
        "pending_restart": len([r for r in failed_rows if r.get('status', '').lower() in ['failed', 'stopped', 'aborted', 'terminated']])
    }
    
    # Calculate totals across all 7 days
    total_stats = {
        'succeeded': sum(day.get('succeeded', 0) for day in daily_stats) if daily_stats else 0,
        'failed': sum(day.get('failed', 0) for day in daily_stats) if daily_stats else 0,
        'running': sum(day.get('running', 0) for day in daily_stats) if daily_stats else 0,
        'stopped': sum(day.get('stopped', 0) for day in daily_stats) if daily_stats else 0,
        'disabled': sum(day.get('disabled', 0) for day in daily_stats) if daily_stats else 0,
        'total': sum(day.get('total', 0) for day in daily_stats) if daily_stats else 0,
    }
    
    # Separate today from historical days
    today_stats = daily_stats[0] if daily_stats and daily_stats[0].get('is_today') else None
    historical_days = daily_stats[1:] if len(daily_stats) > 1 else []
    
    # For historical days, fetch detailed jobs only on demand (not here to save time)
    # The template will need to load these via JavaScript/AJAX or we skip detailed view
    # For now, let's skip detailed jobs to improve performance
    # for day in historical_days:
    #     day['detailed_jobs'] = get_level3_jobs_by_date(day['date'])
    
    return render(request, "portal/level3_job_insights_fresh.html", {
        "summary": summary,
        "failed": failed_rows,
        "long_running": long_running,
        "ai_insights": ai_insights,
        "flash_messages": flash_messages,
        "today_stats": today_stats,
        "historical_days": historical_days,
        "total_stats": total_stats,
    })


def erp_job_status(request):
    """
    ERP Job Status with AI Insights - Shows last 8 runs and current run details
    ERP runs every 4 hours: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
    CACHE: 30 seconds for real-time status updates after recovery
    """
    from django.core.cache import cache
    from portal.erp_mdm_insights import get_erp_run_history
    import time
    
    # Try to get cached data (cache for 30 seconds - shorter for real-time monitoring)
    cache_key = 'erp_run_history_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        # Use cached data
        erp_data = cached_data
    else:
        # Fetch fresh data
        start_time = time.time()
        erp_data = get_erp_run_history()
        
        # Cache the results for 30 seconds (faster updates for recovery monitoring)
        cache.set(cache_key, erp_data, 30)
        
        fetch_time = time.time() - start_time
        print(f"[PERFORMANCE] ERP data fetched in {fetch_time:.2f} seconds")
    
    # Prepare flash messages based on current run
    flash_messages = []
    if erp_data.get('success'):
        current_run = erp_data.get('current_run', {})
        failed_count = current_run.get('failed', 0)
        running_count = current_run.get('running', 0)
        completed_count = current_run.get('completed', 0)
        
        if failed_count > 0:
            flash_messages.append({
                'type': 'error',
                'message': f'🚨 CURRENT RUN ALERT: {failed_count} ERP jobs have failed!'
            })
        
        if running_count > 0:
            flash_messages.append({
                'type': 'warning',
                'message': f'⏱️ IN PROGRESS: {running_count} ERP jobs are currently running'
            })
        
        if completed_count > 0 and failed_count == 0 and running_count == 0:
            flash_messages.append({
                'type': 'success',
                'message': f'✅ SUCCESS: Current run completed with {completed_count} jobs succeeded!'
            })
    
    return render(request, "portal/erp_job_status.html", {
        "erp_data": erp_data,
        "flash_messages": flash_messages,
    })

def level3_7day_insights(request):
    """
    7-Day Job Insights Dashboard
    Shows completed, failed, and running jobs for the last 7 days with date-wise breakdown
    """
    from portal.services.level3_service import get_level3_jobs_last_7_days_optimized
    from django.core.cache import cache
    
    # Cache for 3 minutes since this is expensive
    cache_key = 'level3_7day_insights_data'
    daily_stats = cache.get(cache_key)
    
    if not daily_stats:
        daily_stats = get_level3_jobs_last_7_days_optimized()
        cache.set(cache_key, daily_stats, 180)  # 3 minutes
    
    # Calculate totals across all 7 days
    total_stats = {
        'succeeded': sum(day.get('succeeded', 0) for day in daily_stats),
        'failed': sum(day.get('failed', 0) for day in daily_stats),
        'running': sum(day.get('running', 0) for day in daily_stats),
        'total': sum(day.get('total', 0) for day in daily_stats),
    }
    
    # Separate today from historical days
    today_stats = daily_stats[0] if daily_stats and daily_stats[0]['is_today'] else None
    historical_days = daily_stats[1:] if len(daily_stats) > 1 else []
    
    return render(request, "portal/level3_7day_insights.html", {
        "today_stats": today_stats,
        "historical_days": historical_days,
        "total_stats": total_stats,
    })

def mdm_job_status(request):
    """
    MDM Job Status with AI Insights
    """
    from django.core.cache import cache
    from portal.services.level3_service import get_mdm_job_status
    from portal.erp_mdm_insights import get_mdm_insights
    import time
    
    # Try to get cached data (cache for 30 seconds for real-time monitoring)
    cache_key = 'mdm_job_status_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        # Use cached data
        jobs = cached_data['jobs']
        mdm_insights = cached_data['mdm_insights']
    else:
        # Fetch fresh data
        start_time = time.time()
        jobs = get_mdm_job_status()
        
        # Get AI insights
        mdm_insights = get_mdm_insights()
        
        # Cache the results for 30 seconds (real-time monitoring)
        cache.set(cache_key, {
            'jobs': jobs,
            'mdm_insights': mdm_insights,
        }, 30)
        
        fetch_time = time.time() - start_time
        print(f"[PERFORMANCE] MDM data fetched in {fetch_time:.2f} seconds")
    
    # Prepare flash messages
    flash_messages = []
    if mdm_insights.get('success'):
        failed_count = mdm_insights.get('failed_count', 0)
        if failed_count > 0:
            flash_messages.append({
                'type': 'error',
                'message': f'🚨 ALERT: {failed_count} MDM jobs have failed!'
            })
        
        succeeded_count = mdm_insights.get('succeeded_count', 0)
        if succeeded_count > 0:
            flash_messages.append({
                'type': 'success',
                'message': f'✅ SUCCESS: {succeeded_count} MDM jobs completed successfully'
            })
    
    return render(request, "portal/mdm_job_status.html", {
        "jobs": jobs,
        "mdm_insights": mdm_insights,
        "flash_messages": flash_messages,
    })


def dh_health_dashboard(request):
    """
    DH Health Monitoring Dashboard - embedded view
    """
    return render(request, "portal/dh_health_dashboard.html")


def manual_informatica_restart(request):
    """
    Manual Informatica Restart page for developer special requests
    Allows submitting restart requests with Grid selection, Workflow, Task, and restart options
    """
    return render(request, "portal/manual_restart.html")