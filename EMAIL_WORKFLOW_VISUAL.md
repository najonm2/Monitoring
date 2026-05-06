# 📧 Email Report Feature - Visual Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                   Level3 BI Email Report System                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 1: One-Time Setup (5 minutes)                                      │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Open PowerShell as Administrator:                                        │
│                                                                           │
│  PS> cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal  │
│  PS> .\setup_email_scheduler.ps1                                         │
│                                                                           │
│  ✓ Creates Windows Scheduled Task                                        │
│  ✓ Configures 3-hour intervals                                           │
│  ✓ Sets up logging                                                        │
│  ✓ Ready to go!                                                           │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Automatic Email Schedule                                        │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Emails sent automatically every 3 hours:                                 │
│                                                                           │
│   00:00 ──► 03:00 ──► 06:00 ──► 09:00 ──► 12:00 ──► 15:00 ──► 18:00 ──► 21:00  │
│     🌙        🌙        🌅        ☀️        ☀️        ☀️        🌆        🌙   │
│                                                                           │
│   8 emails per day to:                                                    │
│   • Naresh.m@lumen.com                                                    │
│   • Prithviraj.Nayak@lumen.com                                            │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW: How It Works                                                  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. ⏰ Windows Task Scheduler triggers at scheduled time                  │
│           │                                                               │
│           ▼                                                               │
│  2. 🔧 Runs: run_email_report.ps1                                         │
│           │                                                               │
│           ▼                                                               │
│  3. 🐍 Executes: python manage.py send_level3_bi_email                   │
│           │                                                               │
│           ▼                                                               │
│  4. 📊 Fetches Data:                                                      │
│      • BI Feed Status (get_level3_bi_feed)                                │
│      • CAPEX Details (get_capex_details)                                  │
│      • BI Status Query (get_bi_status_query)                              │
│      • ERP Run History (get_erp_run_history)                              │
│           │                                                               │
│           ▼                                                               │
│  5. 🔍 Checks for failures in all data sources                            │
│           │                                                               │
│           ├──► ❌ Failures Found:                                         │
│           │    • Subject: "🚨 ALERT: X Failures Detected"                 │
│           │    • Red alert banner                                         │
│           │    • Screenshot attached (if enabled)                         │
│           │                                                               │
│           └──► ✅ All Normal:                                             │
│                • Subject: "✅ All Systems Normal"                         │
│                • Green success banner                                     │
│                                                                           │
│           ▼                                                               │
│  6. 📧 Renders HTML Email Template                                        │
│      • Professional design                                                │
│      • Color-coded status badges                                          │
│      • Data tables                                                        │
│      • Lumen branding                                                     │
│           │                                                               │
│           ▼                                                               │
│  7. 📤 Sends Email via SMTP                                               │
│      • To: Recipients                                                     │
│      • From: monitorportal@lumen.com                                      │
│      • Attachment: Screenshot (if failures)                               │
│           │                                                               │
│           ▼                                                               │
│  8. 📝 Logs Result                                                        │
│      • logs/email_report_YYYYMMDD.log                                     │
│      • Success/failure status                                             │
│      • Timestamp                                                          │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  EMAIL CONTENT: What Recipients See                                      │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  🔍 Level3 BI Monitoring Report                                 │    │
│  │  Generated: April 10, 2026 - 12:00 (IST)                        │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  🚨 FAILURES DETECTED! 5 failure(s) require attention.          │    │
│  │  (or)                                                            │    │
│  │  ✅ ALL SYSTEMS NORMAL - No failures detected                   │    │
│  │                                                                  │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  📊 Summary                                                      │    │
│  │  Failures: 5                                                     │    │
│  │  Sections: BI Feed, CAPEX, BI Status, ERP                       │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  📈 BI Feed Status                                               │    │
│  │  ┌──────────────┬──────────┬────────────┬────────────┐         │    │
│  │  │ Task Name    │ Status   │ Start Time │ End Time   │         │    │
│  │  ├──────────────┼──────────┼────────────┼────────────┤         │    │
│  │  │ BI_ETL_Job1  │ SUCCESS  │ 00:15      │ 00:45      │         │    │
│  │  │ BI_ETL_Job2  │ FAILED   │ 01:00      │ 01:30      │         │    │
│  │  └──────────────┴──────────┴────────────┴────────────┘         │    │
│  │                                                                  │    │
│  │  💰 CAPEX Details                                                │    │
│  │  (Similar table format)                                          │    │
│  │                                                                  │    │
│  │  📊 BI Status                                                    │    │
│  │  (Similar table format)                                          │    │
│  │                                                                  │    │
│  │  🏢 ERP Current Run Status                                       │    │
│  │  Completed: 45  Running: 3  Failed: 2                           │    │
│  │                                                                  │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  PASE Monitor Portal - Automated Email Report                   │    │
│  │  View dashboard: http://127.0.0.1:8000/level3-bi/               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  MANUAL COMMANDS                                                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Send email now:                                                          │
│  PS> python manage.py send_level3_bi_email                               │
│                                                                           │
│  Send with screenshot:                                                    │
│  PS> python manage.py send_level3_bi_email --screenshot                  │
│                                                                           │
│  Send test email:                                                         │
│  PS> python manage.py send_level3_bi_email --test                        │
│                                                                           │
│  Custom recipients:                                                       │
│  PS> python manage.py send_level3_bi_email --recipients "a@lumen.com"    │
│                                                                           │
│  Run scheduled task now:                                                  │
│  PS> Start-ScheduledTask -TaskName "Level3_BI_Email_Report"              │
│                                                                           │
│  View task status:                                                        │
│  PS> Get-ScheduledTask -TaskName "Level3_BI_Email_Report"                │
│                                                                           │
│  View logs:                                                               │
│  PS> Get-Content .\logs\email_report_*.log -Tail 50                      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  FILE STRUCTURE                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  monitorportal/                                                           │
│  ├── portal/                                                              │
│  │   ├── services/                                                        │
│  │   │   └── email_service.py          ← Email sending logic             │
│  │   ├── templates/portal/emails/                                         │
│  │   │   └── level3_bi_report.html     ← HTML email template             │
│  │   └── management/commands/                                             │
│  │       └── send_level3_bi_email.py   ← Django command                  │
│  ├── monitorportal/                                                       │
│  │   └── settings.py                   ← Email configuration             │
│  ├── setup_email_scheduler.ps1         ← Setup script                    │
│  ├── run_email_report.ps1              ← Auto-generated executor         │
│  └── logs/                                                                │
│      └── email_report_YYYYMMDD.log     ← Execution logs                  │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  CONFIGURATION                                                            │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Default Recipients:                                                      │
│    • Naresh.m@lumen.com                                                   │
│    • Prithviraj.Nayak@lumen.com                                           │
│                                                                           │
│  Schedule:                                                                │
│    • Every 3 hours (8 times per day)                                      │
│    • 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00              │
│                                                                           │
│  Email Backend:                                                           │
│    • Development: Console (emails printed to terminal)                    │
│    • Production: SMTP (configure in settings.py)                          │
│                                                                           │
│  Screenshot:                                                              │
│    • Optional feature (requires Selenium)                                 │
│    • Only attached when failures detected                                 │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  STATUS: ✅ READY TO USE                                                  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ✓ Email service implemented                                              │
│  ✓ HTML template created                                                  │
│  ✓ Management command available                                           │
│  ✓ Scheduler script ready                                                 │
│  ✓ Documentation complete                                                 │
│  ✓ Test email successful                                                  │
│                                                                           │
│  Next: Run .\setup_email_scheduler.ps1 to activate automatic schedule!   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Quick Start Commands

```powershell
# 1. Test the email service
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
.\.venv\Scripts\Activate.ps1
python manage.py send_level3_bi_email --test

# 2. Send a real report
python manage.py send_level3_bi_email

# 3. Set up automatic schedule (run as Administrator)
.\setup_email_scheduler.ps1
```

**Implementation Date**: April 10, 2026  
**Status**: ✅ Complete and Tested
