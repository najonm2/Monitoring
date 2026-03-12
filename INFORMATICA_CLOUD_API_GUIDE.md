"""
INFORMATICA CLOUD API INTEGRATION GUIDE
========================================

This guide explains how to integrate with Informatica Cloud API to capture 
ERP-related suspended and restart data with a 2-day retention policy.

FEATURES:
---------
✅ Captures only ERP-related tasks (filters by workflow name)
✅ Records suspended status and restart completion data
✅ Stores 2 days of data (~50-100 KB disk space)
✅ Auto-cleanup of expired records
✅ API endpoint for dashboard integration
✅ Management command for manual/periodic sync

STEP 1: CONFIGURE API CREDENTIALS
==================================

In your Django settings.py, add:

    # Informatica Cloud API Configuration
    INFORMATICA_CLOUD_URL = 'https://usw3.dm1-us.informaticacloud.com/active-bpel/services'
    INFORMATICA_CLOUD_USER = 'your_informatica_username'  # Usually email
    INFORMATICA_CLOUD_PASSWORD = 'your_api_authentication_token'
    
    # Optional: Sync settings
    INFORMATICA_SYNC_INTERVAL = 3600  # Sync every hour (in seconds)


STEP 2: CREATE DATABASE MIGRATION
==================================

Run migration to create the InformaticaTaskStatus table:

    python manage.py makemigrations
    python manage.py migrate


STEP 3: (OPTIONAL) SETUP PERIODIC SYNCING
===========================================

Option A: Using Celery Beat (Recommended)
------------------------------------------

In your celery.py:

    from celery.schedules import crontab
    
    CELERY_BEAT_SCHEDULE = {
        'sync-informatica-erp-tasks': {
            'task': 'portal.tasks.sync_informatica_erp_tasks',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        },
    }

In portal/tasks.py:

    from celery import shared_task
    from portal.services.informatica_cloud_service import get_informatica_task_status
    
    @shared_task
    def sync_informatica_erp_tasks():
        result = get_informatica_task_status()
        return result


Option B: Using Django APScheduler
-----------------------------------

In your Django app's apps.py:

    from django.apps import AppConfig
    from django.core.management import call_command
    
    class YourAppConfig(AppConfig):
        name = 'portal'
        
        def ready(self):
            from apscheduler.schedulers.background import BackgroundScheduler
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                lambda: call_command('sync_informatica_erp_tasks'),
                'interval',
                hours=6,
                id='sync_informatica_erp_tasks'
            )
            scheduler.start()


Option C: Using Cron Job (External)
-----------------------------------

Add to your crontab (every 6 hours):

    0 */6 * * * cd /path/to/monitorportal && python manage.py sync_informatica_erp_tasks >> sync.log 2>&1


STEP 4: MANUAL TESTING
========================

Test the integration without storing data:

    python manage.py sync_informatica_erp_tasks --show-summary

Show current summary:

    python manage.py sync_informatica_erp_tasks --show-summary

Only cleanup expired records:

    python manage.py sync_informatica_erp_tasks --cleanup-only


STEP 5: ACCESS DATA IN YOUR VIEWS/TEMPLATES
===============================================

In your Django views:

    from portal.services.informatica_cloud_service import (
        get_erp_suspended_tasks,
        get_erp_restarted_tasks,
        get_erp_task_summary,
    )
    
    def erp_dashboard(request):
        suspended = get_erp_suspended_tasks()
        restarted = get_erp_restarted_tasks()
        summary = get_erp_task_summary()
        
        return render(request, 'erp_dashboard.html', {
            'suspended_tasks': suspended,
            'restarted_tasks': restarted,
            'summary': summary,
        })


In your templates (Django template syntax):

    {% load custom_filters %}
    
    <h2>Currently Suspended ERP Tasks</h2>
    <table>
        {% for task in suspended_tasks %}
        <tr>
            <td>{{ task.task_name }}</td>
            <td>{{ task.status }}</td>
            <td>{{ task.original_suspend_at|date:"SHORT_DATETIME_FORMAT" }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <h2>Restart History</h2>
    <table>
        {% for task in restarted_tasks %}
        <tr>
            <td>{{ task.task_name }}</td>
            <td>{{ task.restart_completed_at|date:"SHORT_DATETIME_FORMAT" }}</td>
            <td>{{ task.restart_completed_status }}</td>
        </tr>
        {% endfor %}
    </table>


STEP 6: ADD API ENDPOINT
==========================

In portal/api_views.py:

    from portal.services.informatica_cloud_service import get_erp_task_summary
    
    def api_informatica_suspended_tasks(request):
        \"\"\"API endpoint for suspended ERP tasks\"\"\"
        from portal.models import InformaticaTaskStatus
        
        tasks = InformaticaTaskStatus.get_suspended_tasks()
        data = [{
            'id': t.task_id,
            'name': t.task_name,
            'status': t.status,
            'suspended_at': t.original_suspend_at.isoformat() if t.original_suspend_at else None,
            'workflow': t.workflow_name,
            'location': t.erp_location,
        } for t in tasks]
        
        return JsonResponse({
            'success': True,
            'data': data,
            'summary': get_erp_task_summary(),
        })


In portal/urls.py:

    path('api/informatica/suspended-tasks/', 
         api_views.api_informatica_suspended_tasks, 
         name='api_informatica_suspended'),


ACCESS IN JAVASCRIPT:

    fetch('/api/informatica/suspended-tasks/')
        .then(r => r.json())
        .then(data => {
            console.log('Suspended tasks:', data.data);
            console.log('Summary:', data.summary);
        });


DATA RETENTION POLICY
======================

✅ Records expire after 2 days
✅ Auto-cleanup runs with every sync
✅ Max storage: ~100 KB for typical ERP workloads
✅ No memory issues from accumulated data

Example calculation:
- ~50 ERP tasks per sync
- Each record ~500 bytes
- Syncing every 6 hours = 4 syncs/day
- 4 syncs × 50 tasks × 500 bytes = ~100 KB/day
- 2 days max storage = ~200 KB
- Auto-cleanup prevents buildup


TROUBLESHOOTING
================

Q: "Informatica Cloud API credentials not configured"
A: Add INFORMATICA_CLOUD_USER and INFORMATICA_CLOUD_PASSWORD to settings.py

Q: "Connection timeout to Informatica Cloud"
A: Check VPN/firewall, verify URL is correct for your region (usw3.dm1-us is US)

Q: "Getting 401 Unauthorized"
A: Verify API credentials are correct. May need to generate new API token.

Q: "Records not syncing regularly"
A: Ensure periodic task (Celery/APScheduler/Cron) is running.
   Check logs: tail -f sync.log

Q: "Database table doesn't exist"
A: Run migrations: python manage.py migrate

Q: "Want to see what's being synced"
A: Run: python manage.py sync_informatica_erp_tasks --show-summary


EXAMPLE DASHBOARD INTEGRATION
==============================

You can add a section to your ERP dashboard:

    <section class="report-section">
        <h2>📡 Informatica Cloud Status - ERP Tasks</h2>
        
        <div class="ai-summary-grid">
            <div class="insight-card insight-warning">
                <div class="insight-icon">⏸️</div>
                <div class="insight-content">
                    <h3>Suspended Tasks</h3>
                    <p><strong>{{ summary.currently_suspended }}</strong> task(s) currently suspended</p>
                </div>
            </div>
            
            <div class="insight-card insight-success">
                <div class="insight-icon">✅</div>
                <div class="insight-content">
                    <h3>Restarted & Completed</h3>
                    <p><strong>{{ summary.completed_after_restart }}</strong> task(s) completed after restart</p>
                </div>
            </div>
            
            <div class="insight-card insight-critical">
                <div class="insight-icon">❌</div>
                <div class="insight-content">
                    <h3>Failed After Restart</h3>
                    <p><strong>{{ summary.failed_after_restart }}</strong> task(s) failed to complete</p>
                </div>
            </div>
        </div>
        
        <table class="table">
            <thead>
                <tr>
                    <th>Task Name</th>
                    <th>Status</th>
                    <th>Suspended At</th>
                    <th>Restarted At</th>
                    <th>Restart Status</th>
                </tr>
            </thead>
            <tbody>
                {% for task in suspended_tasks | slice:":10" %}
                <tr>
                    <td>{{ task.task_name }}</td>
                    <td><span class="badge badge-{{ task.status|lower }}">{{ task.status }}</span></td>
                    <td>{{ task.original_suspend_at|date:"SHORT_DATETIME_FORMAT" }}</td>
                    <td>{{ task.last_restart_at|date:"SHORT_DATETIME_FORMAT"|default:"—" }}</td>
                    <td>{{ task.restart_completed_status|default:"—" }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>


NEXT STEPS
===========

1. Configure API credentials in settings.py
2. Run migrations: python manage.py migrate
3. Test: python manage.py sync_informatica_erp_tasks --show-summary
4. Setup periodic syncing (Celery/APScheduler/Cron)
5. Add dashboard widgets as shown above
6. Monitor sync logs

Questions? Check the service code in:
- portal/services/informatica_cloud_service.py
- portal/models.py (InformaticaTaskStatus model)
"""
