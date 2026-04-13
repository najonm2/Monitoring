# Quick Reference - Email Report Commands

## Send Email Report

```powershell
# Navigate to project
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Send email to default recipients (Naresh.m@lumen.com, Prithviraj.Nayak@lumen.com)
python manage.py send_level3_bi_email

# Send with screenshot (requires selenium)
python manage.py send_level3_bi_email --screenshot

# Send to custom recipients
python manage.py send_level3_bi_email --recipients "email1@lumen.com,email2@lumen.com"

# Send test email (verify configuration)
python manage.py send_level3_bi_email --test
```

## Scheduled Task Management

```powershell
# View scheduled task
Get-ScheduledTask -TaskName "Level3_BI_Email_Report"

# Run task immediately
Start-ScheduledTask -TaskName "Level3_BI_Email_Report"

# Check last run result
Get-ScheduledTask -TaskName "Level3_BI_Email_Report" | Get-ScheduledTaskInfo

# Disable task
Disable-ScheduledTask -TaskName "Level3_BI_Email_Report"

# Enable task
Enable-ScheduledTask -TaskName "Level3_BI_Email_Report"

# Remove task
Unregister-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

## View Logs

```powershell
# View today's log
Get-Content -Path ".\logs\email_report_$(Get-Date -Format 'yyyyMMdd').log" -Tail 50

# View all logs
Get-ChildItem -Path ".\logs\email_report_*.log" | Sort-Object LastWriteTime -Descending
```

## Setup

```powershell
# Run as Administrator
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal

# Basic setup
.\setup_email_scheduler.ps1

# With screenshots
.\setup_email_scheduler.ps1 -EnableScreenshots

# Custom recipients
.\setup_email_scheduler.ps1 -CustomRecipients "email1@lumen.com,email2@lumen.com"
```

## Email Schedule (Every 3 Hours)

- 00:00 - 03:00 - 06:00 - 09:00
- 12:00 - 15:00 - 18:00 - 21:00
