"""
INFORMATICA CLOUD API INTEGRATION - VISUAL IMPLEMENTATION DIAGRAM
==================================================================

This shows the complete flow from API to Dashboard
"""

ARCHITECTURE_DIAGRAM = """

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                  INFORMATICA CLOUD PLATFORM                                │
│                  (Regional SaaS)                                           │
│                  usw3.dm1-us.informaticacloud.com                          │
│                                                                             │
│  /active-bpel/services/tf/status/                                         │
│  Returns: 200 task status records                                          │
│  - Mix of all workflows (ERP, MDM, Finance, HR, etc.)                     │
│  - Updates every few minutes                                              │
│                                                                             │
│  Sample tasks in response:                                                 │
│  ├─ wkf_Customer_Load (non-ERP) ❌ Filtered out                           │
│  ├─ wkf_ERP_Daily_Refresh (ERP) ✅ Captured                               │
│  ├─ wkf_Payroll_Process (non-ERP) ❌ Filtered out                         │
│  ├─ wkf_CDW_DSL_ERP_Master (ERP) ✅ Captured                              │
│  ├─ wkf_ASL_SAPS4_Load (SAPS4) ✅ Captured                                │
│  └─ ... 195 more tasks ...                                                │
│                                                                             │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                    HTTP GET Request (with auth)
                    ↓
                             │
         ┌───────────────────┴─────────────────────┐
         │                                         │
         │  DJANGO APPLICATION                    │
         │                                         │
         │  ┌─────────────────────────────────┐  │
         │  │ SERVICE LAYER                   │  │
         │  │ informatica_cloud_service.py    │  │
         │  │                                 │  │
         │  │ ┌──────────────────────────┐   │  │
         │  │ │ InformaticaCloudAPI      │   │  │
         │  │ │ - fetch_task_status()    │   │  │
         │  │ │ - is_erp_related()       │   │  │
         │  │ │ - extract_erp_location() │   │  │
         │  │ │ - sync_task_status()     │   │  │
         │  │ └──────────┬───────────────┘   │  │
         │  │            │                   │  │
         │  │      Parse JSON Response       │  │
         │  │      Filter ERP keywords       │  │
         │  │      Extract relevant fields   │  │
         │  │            │                   │  │
         │  │            ↓                   │  │
         │  │ ┌──────────────────────────┐  │  │
         │  │ │ Data Transformation      │  │  │
         │  │ │ - 200 tasks → 45 ERP     │  │  │
         │  │ │ - Extract timestamps     │  │  │
         │  │ │ - Map locations          │  │  │
         │  │ │ - Parse restart status   │  │  │
         │  │ └──────────┬───────────────┘  │  │
         │  │            │                   │  │
         │  │      Result: ~50 ERP tasks     │  │
         │  │      Size: 15 KB               │  │
         │  │                                 │  │
         │  └────────────┬────────────────────┘  │
         │               │                        │
         │               │ ORM Save               │
         │               ↓                        │
         │             ┌─────────────────────────────────────┐
         │             │ DJANGO MODEL                         │
         │             │ InformaticaTaskStatus                │
         │             │                                      │
         │             │ Fields:                              │
         │             │ ├─ task_id (PK)                     │
         │             │ ├─ task_name                        │
         │             │ ├─ status (SUSPENDED, etc.)       │
         │             │ ├─ is_erp_related (True)           │
         │             │ ├─ erp_location                    │
         │             │ ├─ workflow_name                   │
         │             │ ├─ restart_count                   │
         │             │ ├─ original_suspend_at             │
         │             │ ├─ last_restart_at                 │
         │             │ ├─ restart_completed_at            │
         │             │ ├─ restart_completed_status        │
         │             │ ├─ restart_notes                   │
         │             │ ├─ created_at                      │
         │             │ ├─ updated_at                      │
         │             │ └─ expires_at (auto-2days)         │
         │             └─────────────────────────────────────┘
         │               │
         │               │ Database Write
         │               ↓
         │        ┌──────────────┐
         │        │ PostgreSQL/  │
         │        │ SQLite DB    │
         │        │              │
         │        │ informatica_ │
         │        │ task_status  │
         │        │ table        │
         │        │              │
         │        │ 500 bytes    │
         │        │ per record   │
         │        │              │
         │        │ ~120 KB      │
         │        │ (2-day max)  │
         │        └──────────────┘
         │
         └────────────┬──────────────────────────────┐
                      │                              │
                      ↓                              ↓
              ┌──────────────────┐        ┌─────────────────────┐
              │ MANAGEMENT CMD   │        │ API ENDPOINT        │
              │                  │        │                     │
              │ Management       │        │ GET /api/           │
              │ Command to:      │        │   informatica/      │
              │                  │        │   suspended-tasks/  │
              │ Manual sync:     │        │                     │
              │ sync_..._tasks   │        │ Returns JSON:       │
              │                  │        │ {                   │
              │ Show summary:    │        │   data: [tasks],    │
              │ --show-summary   │        │   summary: {...}    │
              │                  │        │ }                   │
              │ Cleanup:         │        │                     │
              │ --cleanup-only   │        │ For AJAX calls      │
              │                  │        │ from dashboard      │
              └─────────┬────────┘        └─────────┬───────────┘
                        │                          │
                        └──────────────┬───────────┘
                                       │
                                       ↓
                        ┌──────────────────────────┐
                        │  ERP DASHBOARD / UI      │
                        │                          │
                        │ Display Options:         │
                        │ ├─ Summary Cards         │
                        │ │  ├─ Suspended: 5       │
                        │ │  ├─ Restarted: 3      │
                        │ │  └─ Completed: 2      │
                        │ │                        │
                        │ ├─ Suspended Tasks List  │
                        │ │  ├─ wkf_ERP_... [2h]  │
                        │ │  ├─ wkf_SAPS4_... [1h]│
                        │ │  └─ wkf_ADF_... [3h]   │
                        │ │                        │
                        │ └─ Restart History       │
                        │    ├─ Task X rstarted    │
                        │    ├─ Completed: SUCCESS │
                        │    └─ 2h 15m ago        │
                        │                          │
                        │ Real-time refresh every │
                        │ 30 seconds              │
                        └──────────────────────────┘


PERIODIC SYNC OPTIONS
═════════════════════════════════════════════════════════════════════════

1. CRON JOB (Every 6 hours externally scheduled)
   0 */6 * * * /usr/bin/python /path/manage.py sync_informatica_erp_tasks
   
2. CELERY BEAT (Background task scheduler)
   CELERY_BEAT_SCHEDULE = {
       'sync-informatica': {
           'task': 'portal.tasks.sync_informatica_erp_tasks',
           'schedule': crontab(minute=0, hour='*/6'),
       }
   }
   
3. DJANGO APScheduler (Python-based scheduler)
   BackgroundScheduler().add_job(
       lambda: call_command('sync_informatica_erp_tasks'),
       'interval',
       hours=6
   )


DATA FLOW TIMELINE
═════════════════════════════════════════════════════════════════════════════

Day 1, 6:00 AM
├─ Sync runs: Fetches 200 tasks, filters to 45 ERP, stores 15 KB
├─ DB size: 15 KB
└─ Expires at: Day 3, 6:00 AM

Day 1, 12:00 PM
├─ Sync runs: Fetches 200 tasks, filters to 48 ERP, stores 15 KB
├─ DB size: 30 KB
└─ Expires at: Day 3, 12:00 PM

Day 1, 6:00 PM
├─ Sync runs: Fetches 200 tasks, filters to 42 ERP, stores 14 KB
├─ DB size: 44 KB
└─ Expires at: Day 3, 6:00 PM

Day 1, 12:00 AM
├─ Sync runs: Fetches 200 tasks, filters to 38 ERP, stores 13 KB
├─ DB size: 57 KB
└─ Expires at: Day 3, 12:00 AM

Day 2, 6:00 AM
├─ Sync runs: Fetches 200 tasks, filters to 50 ERP, stores 15 KB
├─ DB size: 72 KB (oldest records still valid)
└─ Expires at: Day 4, 6:00 AM

Day 2, 12:00 PM
├─ Sync runs: Fetches 200 tasks, filters to 45 ERP, stores 15 KB
├─ DB size: 87 KB
└─ Expires at: Day 4, 12:00 PM

Day 3, 6:00 AM
├─ CLEANUP RUN: Deletes records from Day 1, 6:00 AM (now expired)
├─ DB size after cleanup: 59 KB (87 - 15 = 72, but we sync so → 87 KB still)
│  Actually:
│  Before sync: 72 KB
│  Cleanup: Delete 15 KB (oldest) → 57 KB
│  After sync: Add 15 KB → 72 KB
├─ Maintains 2-day rolling window
└─ Expires at: Day 5, 6:00 AM

Result: DB size oscillates between 50-120 KB, never grows beyond 2-day window


MEMORY & DISK SAFETY GUARANTEE
═════════════════════════════════════════════════════════════════════════════

Input:    200 tasks from Informatica Cloud API per sync
Filter:   Extract only ERP-related (keywords: ERP, SAPS4, DATAHUB, etc.)
Result:   45-50 tasks kept, 150-155 discarded (75-77% filtered)
Storage:  500 bytes × 50 tasks = 25 KB per sync (estimate)
Syncs/day: 4 (every 6 hours)
Daily:     25 KB × 4 = 100 KB/day
2-day max: 100 KB × 2 = 200 KB (with buffer)
Actual:    ~120 KB (includes cleanup overlap)

CONCLUSION: Max disk space never exceeds 200 KB with 2-day retention.
            Typical range: 50-120 KB.
            NO memory issues. NO disk space problems.
"""

print(ARCHITECTURE_DIAGRAM)
