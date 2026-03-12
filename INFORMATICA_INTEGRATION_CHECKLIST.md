"""
INFORMATICA CLOUD API INTEGRATION - IMPLEMENTATION CHECKLIST
==============================================================

Estimated time: 30 minutes setup + 5 minutes testing
Difficulty level: MEDIUM (straightforward integration)

═══════════════════════════════════════════════════════════════════════════════
  PHASE 1: PREPARATION (5 minutes)
═══════════════════════════════════════════════════════════════════════════════

□ Gather Informatica credentials
  □ Informatica Cloud username (email address)
  □ Informatica Cloud password
  □ OR API token (preferred, more secure)
  □ Region/URL (e.g., usw3.dm1-us for US)

□ Check current Django setup
  □ Django is running (python manage.py runserver works)
  □ Database is accessible (SQLite or PostgreSQL)
  □ settings.py file is accessible

□ Review documentation
  □ INFORMATICA_CLOUD_SOLUTION_SUMMARY.md
  □ INFORMATICA_CLOUD_API_GUIDE.md
  □ INFORMATICA_CLOUD_ARCHITECTURE_DIAGRAM.md

═══════════════════════════════════════════════════════════════════════════════
  PHASE 2: SYSTEM SETUP (15 minutes)
═══════════════════════════════════════════════════════════════════════════════

STEP 1: Add Django Model
  □ File: portal/models.py
  □ Status: ALREADY CREATED ✅
  □ Contains: InformaticaTaskStatus model
  □ Features:
    ✓ Captures suspended/restart data
    ✓ Auto-expires after 2 days
    ✓ Indexed for performance
    ✓ Query methods built-in

STEP 2: Create Database Migration
  □ Run: python manage.py makemigrations
  □ Verify: See "Create model InformaticaTaskStatus" message
  □ Run: python manage.py migrate
  □ Verify: Table 'informatica_task_status' exists in database

STEP 3: Add API Service
  □ File: portal/services/informatica_cloud_service.py
  □ Status: ALREADY CREATED ✅
  □ Contains:
    ✓ InformaticaCloudAPI class
    ✓ Filtering logic for ERP keywords
    ✓ Database sync methods
    ✓ Helper functions

STEP 4: Create Management Command
  □ File: portal/management/commands/sync_informatica_erp_tasks.py
  □ Status: ALREADY CREATED ✅
  □ Can run manually for testing:
    python manage.py sync_informatica_erp_tasks --show-summary

STEP 5: Configure Django Settings
  □ Edit: monitorportal/settings.py (or local_settings.py)
  □ Add these settings:
    
    # Where to get API credentials
    # Settings can be from:
    # 1. environment variables: export INFORMATICA_CLOUD_USER=...
    # 2. Django settings.py (see INFORMATICA_SETTINGS_EXAMPLE.py)
    # 3. secrets management (12-factor approach)
    
    INFORMATICA_CLOUD_URL = 'https://usw3.dm1-us.informaticacloud.com/active-bpel/services'
    INFORMATICA_CLOUD_USER = os.getenv('INFORMATICA_CLOUD_USER', '')
    INFORMATICA_CLOUD_PASSWORD = os.getenv('INFORMATICA_CLOUD_PASSWORD', '')

  □ Alternative: Use environment variables (recommended for production)
    
    # In your .bashrc, .env, or CI/CD pipeline:
    export INFORMATICA_CLOUD_USER="your_email@company.com"
    export INFORMATICA_CLOUD_PASSWORD="your_api_token"
    
    # Then in settings.py:
    import os
    INFORMATICA_CLOUD_USER = os.getenv('INFORMATICA_CLOUD_USER', '')
    INFORMATICA_CLOUD_PASSWORD = os.getenv('INFORMATICA_CLOUD_PASSWORD', '')

═══════════════════════════════════════════════════════════════════════════════
  PHASE 3: TESTING (10 minutes)
═══════════════════════════════════════════════════════════════════════════════

STEP 1: Run Integration Test Script
  □ File: test_informatica_integration.py
  □ Status: ALREADY CREATED ✅
  □ Run: python test_informatica_integration.py
  □ Expected outputs:
    ✅ Configuration Check - Should show credentials configured
    ✅ ERP Filtering Logic - Should pass all keyword tests
    ✅ ERP Location Extraction - Should correctly identify locations
    ✅ Database Model - Should confirm table exists
    ✅ Data Retention Policy - Should show current stats
    ✅ Mock Data Sync - Should create test records
    ✅ API Query Methods - Should work without errors

STEP 2: Manual Sync Test
  □ Run: python manage.py sync_informatica_erp_tasks --show-summary
  □ Watch for:
    ✅ "Fetching from Informatica Cloud API..." message
    ✅ Task count breakdown (Total tasks, ERP tasks filtered)
    ✅ Records stored/updated count
    ✅ Current summary statistics
  □ If error: Check credentials in settings.py

STEP 3: Verify Data in Database
  □ Open Django admin: http://localhost:8000/admin/
  □ Navigate: Portal > Informatica Task Statuses
  □ Should see: Any synced records from previous step

═══════════════════════════════════════════════════════════════════════════════
  PHASE 4: PERIODIC SYNCING SETUP (Choose ONE option) - 5 minutes each
═══════════════════════════════════════════════════════════════════════════════

OPTION A: CELERY BEAT (Recommended for Django projects using Celery)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Prerequisites:
  □ Celery already installed and running
  □ Redis or RabbitMQ broker configured

□ Step 1: Create Celery task
  □ File: portal/tasks.py (Create if doesn't exist)
  □ Add:
    
    from celery import shared_task
    from portal.services.informatica_cloud_service import get_informatica_task_status
    
    @shared_task
    def sync_informatica_erp_tasks():
        result = get_informatica_task_status()
        return result

□ Step 2: Add to beat schedule
  □ Edit: settings.py
  □ Add:
    
    from celery.schedules import crontab
    
    CELERY_BEAT_SCHEDULE = {
        'sync-informatica-erp-tasks': {
            'task': 'portal.tasks.sync_informatica_erp_tasks',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        },
    }

□ Step 3: Verify it works
  □ Start celery beat: celery -A monitorportal beat --loglevel=info
  □ Watch logs for sync execution
  □ Check database for new records


OPTION B: DJANGO APScheduler (If not using Celery)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Prerequisites:
  □ APScheduler installed: pip install django-apscheduler

□ Step 1: Create scheduler in app config
  □ File: portal/apps.py
  □ Edit ready() method:
    
    from django.apps import AppConfig
    from django.core.management import call_command
    
    class PortalConfig(AppConfig):
        name = 'portal'
        
        def ready(self):
            from apscheduler.schedulers.background import BackgroundScheduler
            scheduler = BackgroundScheduler()
            
            # Add the sync job
            scheduler.add_job(
                lambda: call_command('sync_informatica_erp_tasks'),
                'interval',
                hours=6,
                id='sync_informatica_erp_tasks'
            )
            
            scheduler.start()

□ Step 2: Test it
  □ Run Django: python manage.py runserver
  □ Wait 6 hours or manually trigger: python manage.py sync_informatica_erp_tasks
  □ Verify records are synced

□ Step 3: Configure logging (optional)
  □ Edit settings.py LOGGING section
  □ Add handlers for APScheduler


OPTION C: EXTERNAL CRON JOB (Simple, no Python dependencies)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Step 1: Create shell script
  □ Create file: /scripts/sync_informatica.sh
  □ Content:
    
    #!/bin/bash
    cd /path/to/monitorportal
    source venv/bin/activate  # or .venv
    python manage.py sync_informatica_erp_tasks >> /var/log/informatica_sync.log 2>&1

□ Step 2: Make executable
  □ Run: chmod +x /scripts/sync_informatica.sh

□ Step 3: Add to crontab
  □ Edit: crontab -e
  □ Add line:
    
    # Every 6 hours (00:00, 06:00, 12:00, 18:00)
    0 */6 * * * /scripts/sync_informatica.sh
    
    # Alternative: Every 4 hours
    0 */4 * * * /scripts/sync_informatica.sh
    
    # Alternative: Specific times daily
    0 6 * * * /scripts/sync_informatica.sh  # 6 AM
    0 14 * * * /scripts/sync_informatica.sh # 2 PM
    0 22 * * * /scripts/sync_informatica.sh # 10 PM

□ Step 4: Verify cron is working
  □ Check logs: tail -f /var/log/informatica_sync.log
  □ Check database: django shell → InformaticaTaskStatus.objects.count()


═══════════════════════════════════════════════════════════════════════════════
  PHASE 5: DASHBOARD INTEGRATION (Optional - 15+ minutes)
═══════════════════════════════════════════════════════════════════════════════

STEP 1: Create API Endpoint
  □ Edit: portal/api_views.py
  □ Add function (see guide for template):
    
    @require_http_methods(["GET"])
    def api_informatica_suspended_tasks(request):
        from portal.models import InformaticaTaskStatus
        from portal.services.informatica_cloud_service import get_erp_task_summary
        
        tasks = InformaticaTaskStatus.get_suspended_tasks()
        task_data = [{
            'id': t.task_id,
            'name': t.task_name,
            'status': t.status,
            'suspended_at': t.original_suspend_at.isoformat() if t.original_suspend_at else None,
            'workflow': t.workflow_name,
            'location': t.erp_location,
        } for t in tasks]
        
        return JsonResponse({
            'success': True,
            'data': task_data,
            'summary': get_erp_task_summary(),
        })

□ STEP 2: Add URL routing
  □ Edit: portal/urls.py
  □ Add:
    
    path('api/informatica/suspended-tasks/', 
         api_views.api_informatica_suspended_tasks, 
         name='api_informatica_suspended'),

□ STEP 3: Create dashboard section (HTML)
  □ Add to your ERP dashboard template:
    
    <section class="report-section">
      <h2>📡 Informatica Cloud - ERP Task Status</h2>
      
      <div class="ai-summary-grid">
        <div class="insight-card insight-warning">
          <div class="insight-icon">⏸️</div>
          <div class="insight-content">
            <h3>Currently Suspended</h3>
            <p><strong id="suspended-count">0</strong> tasks</p>
          </div>
        </div>
      </div>
      
      <div id="suspended-tasks-table"></div>
    </section>

□ STEP 4: Add JavaScript to load data
  □ Add to your template javascript:
    
    fetch('/api/informatica/suspended-tasks/')
        .then(r => r.json())
        .then(data => {
            document.getElementById('suspended-count').textContent = data.data.length;
            
            // Build table
            let html = '<table><thead><tr>';
            html += '<th>Task Name</th><th>Location</th>';
            html += '<th>Suspended At</th></tr></thead><tbody>';
            
            for (let task of data.data) {
                html += '<tr>';
                html += '<td>' + task.name + '</td>';
                html += '<td>' + (task.location || '-') + '</td>';
                html += '<td>' + (task.suspended_at ? new Date(task.suspended_at).toLocaleString() : '-') + '</td>';
                html += '</tr>';
            }
            
            html += '</tbody></table>';
            document.getElementById('suspended-tasks-table').innerHTML = html;
        })
        .catch(e => console.error('Error loading suspended tasks:', e));

═══════════════════════════════════════════════════════════════════════════════
  PHASE 6: VERIFICATION & MONITORING
═══════════════════════════════════════════════════════════════════════════════

DAILY CHECKS
□ Check sync logs
□ Verify new records in database
□ Monitor disk space (should be stable ~120 KB)
□ Check for any API errors

WEEKLY CHECKS  
□ Review captured suspended tasks
□ Verify restart completion tracking
□ Check that cleanup is running

TROUBLESHOOTING
□ No records appearing?
  → Check credentials in settings.py
  → Run: python manage.py sync_informatica_erp_tasks --show-summary
  → Check server/firewall access to usw3.dm1-us.informaticacloud.com

□ Disk space growing?
  → Check expiration dates: all should be 2 days from creation
  → Force cleanup: python manage.py sync_informatica_erp_tasks --cleanup-only
  → Verify filtering is working correctly

□ Sync task not running?
  → Celery: celery -A monitorportal worker -B (check logs)
  → APScheduler: Check Django startup logs
  → Cron: Check /var/log/cron

═══════════════════════════════════════════════════════════════════════════════
  FILES SUMMARY
═══════════════════════════════════════════════════════════════════════════════

CODE FILES CREATED:
✅ portal/models.py - Added InformaticaTaskStatus model (500KB→250 lines added)
✅ portal/services/informatica_cloud_service.py - Main service (NEW, ~350 lines)
✅ portal/management/commands/sync_informatica_erp_tasks.py - CLI tool (NEW, ~200 lines)

DOCUMENTATION CREATED:
✅ INFORMATICA_CLOUD_API_GUIDE.md - Complete setup guide
✅ INFORMATICA_CLOUD_API_IMPLEMENTATION.md - Technical details & analysis
✅ INFORMATICA_CLOUD_SOLUTION_SUMMARY.md - Executive summary
✅ INFORMATICA_CLOUD_ARCHITECTURE_DIAGRAM.md - Visual flows & diagrams
✅ INFORMATICA_SETTINGS_EXAMPLE.py - Settings configuration example
✅ test_informatica_integration.py - Test suite (NEW)
✅ INFORMATICA_CLOUD_INTEGRATION_CHECKLIST.md - This file

═══════════════════════════════════════════════════════════════════════════════
  SUCCESS CRITERIA
═══════════════════════════════════════════════════════════════════════════════

✅ SUCCESS WHEN:
  □ Test script passes all 7 tests
  □ Can run: python manage.py sync_informatica_erp_tasks --show-summary
  □ Database has records from Informatica Cloud (if configured)
  □ Periodic sync runs without errors
  □ Dashboard displays suspended/restarted tasks
  □ Disk usage stays under 200 KB
  □ No errors in application logs

═══════════════════════════════════════════════════════════════════════════════
  SUPPORT & QUESTIONS
═══════════════════════════════════════════════════════════════════════════════

Read these docs in order:
  1. INFORMATICA_CLOUD_SOLUTION_SUMMARY.md ← Start here
  2. INFORMATICA_CLOUD_API_GUIDE.md ← Setup & integration
  3. INFORMATICA_CLOUD_ARCHITECTURE_DIAGRAM.md ← How it works
  4. INFORMATICA_CLOUD_API_IMPLEMENTATION.md ← Technical details

Still have questions?
  → Check the troubleshooting section in each guide
  → Review code comments in informatica_cloud_service.py
  → Check Django logs: tail -f logs/django.log
  → Run test script: python test_informatica_integration.py
"""
