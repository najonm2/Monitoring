# Level3 BI Email Report Setup Guide

This guide explains how to configure and use the automated email reporting feature for the Level3 BI monitoring page.

## Overview

The email reporting system automatically sends Level3 BI reports to specified recipients every 3 hours. The system can:

- ✅ Send automated email reports with BI Feed, CAPEX, BI Status, and ERP data
- ✅ Detect failures and highlight them in emails
- ✅ Optionally capture screenshots when failures are detected
- ✅ Run on a schedule (every 3 hours) using Windows Task Scheduler
- ✅ Send to multiple recipients

## Default Recipients

- Naresh.m@lumen.com
- Prithviraj.Nayak@lumen.com

## Quick Setup (Windows)

### 1. Configure Email Settings

Edit `monitorportal/monitorportal/settings.py` or set environment variables:

```python
# SMTP Configuration
EMAIL_HOST = 'smtp.lumen.com'  # Your SMTP server
EMAIL_PORT = 25  # 25, 587, or 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''  # Leave empty if no auth required
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'monitorportal@lumen.com'
```

For development/testing, emails will be printed to console.

### 2. Run the Setup Script (Automated)

Open PowerShell as **Administrator** and run:

```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal

# Basic setup (no screenshots)
.\setup_email_scheduler.ps1

# With screenshot support
.\setup_email_scheduler.ps1 -EnableScreenshots

# Custom recipients
.\setup_email_scheduler.ps1 -CustomRecipients "email1@lumen.com,email2@lumen.com"
```

This script will:
- Create a scheduled task to run every 3 hours
- Set up logging
- Configure the email command

### 3. Verify Setup

Check Task Scheduler:
```powershell
# Open Task Scheduler
taskschd.msc

# Or via PowerShell
Get-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

## Manual Commands

### Send Email Report Manually

```powershell
# Activate virtual environment
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
.\.venv\Scripts\Activate.ps1

# Send email to default recipients
python manage.py send_level3_bi_email

# Send with screenshot (requires selenium)
python manage.py send_level3_bi_email --screenshot

# Send to custom recipients
python manage.py send_level3_bi_email --recipients "email1@lumen.com,email2@lumen.com"

# Send test email (verify configuration)
python manage.py send_level3_bi_email --test
```

### Run Scheduled Task Manually

```powershell
# Run immediately
Start-ScheduledTask -TaskName "Level3_BI_Email_Report"

# Check task status
Get-ScheduledTask -TaskName "Level3_BI_Email_Report" | Get-ScheduledTaskInfo
```

## Screenshot Support (Optional)

To enable screenshot capture when failures are detected:

### 1. Install Selenium

```powershell
pip install selenium
```

### 2. Install Chrome Driver

Download ChromeDriver from: https://chromedriver.chromium.org/

Or use:
```powershell
# Using chocolatey (if installed)
choco install chromedriver

# Or download manually and add to PATH
```

### 3. Enable Screenshots

```powershell
python manage.py send_level3_bi_email --screenshot
```

Screenshots will only be attached when failures are detected.

## Email Schedule

The system sends reports at these times (every 3 hours):
- 00:00 (Midnight)
- 03:00 (3 AM)
- 06:00 (6 AM)
- 09:00 (9 AM)
- 12:00 (Noon)
- 15:00 (3 PM)
- 18:00 (6 PM)
- 21:00 (9 PM)

## Log Files

Execution logs are stored in:
```
C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal\logs\email_report_YYYYMMDD.log
```

View latest log:
```powershell
Get-Content -Path ".\logs\email_report_$(Get-Date -Format 'yyyyMMdd').log" -Tail 50
```

## Email Content

The email includes:

### 1. Alert Banner
- 🚨 Red alert if failures detected
- ✅ Green confirmation if all systems normal

### 2. Summary
- Total failure count
- Report sections included

### 3. Data Tables
- **BI Feed Status**: Task names, status, times, messages
- **CAPEX Details**: Projects, status, amounts, dates
- **BI Status**: Task names, status, runtime, record counts
- **ERP Current Run**: Completed, running, failed counts

### 4. Status Badges
- Color-coded status indicators (green/red/blue/yellow)
- Easy-to-read format

## Troubleshooting

### Email Not Sending

**Check SMTP configuration:**
```powershell
python manage.py send_level3_bi_email --test
```

**Common issues:**
- SMTP server blocked by firewall
- Incorrect SMTP host/port
- Authentication required but not configured
- Email service disabled by IT

**Solution:** Contact IT to configure SMTP relay or use authenticated SMTP.

### Scheduled Task Not Running

**Check task status:**
```powershell
Get-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

**Common issues:**
- Task disabled
- User account changed password
- Incorrect path to Python/project

**Solution:** Re-run setup script or manually edit task in Task Scheduler.

### Screenshots Not Working

**Install Selenium and ChromeDriver:**
```powershell
pip install selenium
```

**Check Chrome installation:**
```powershell
# Verify Chrome is installed
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
```

**Run without screenshots:**
```powershell
python manage.py send_level3_bi_email  # No --screenshot flag
```

### Database Connection Errors

**Verify database connectivity:**
```powershell
python -c "from portal.services.level3_service import get_level3_bi_feed; print(len(get_level3_bi_feed()))"
```

**Check Oracle client installation and network access.**

## Configuration Options

### Environment Variables

Set these in `settings.py` or as environment variables:

```bash
# Email Configuration
EMAIL_HOST=smtp.lumen.com
EMAIL_PORT=25
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=monitorportal@lumen.com

# Server URL for screenshots
SERVER_URL=http://127.0.0.1:8000
```

### Custom Recipients via Code

Edit `portal/services/email_service.py`:

```python
DEFAULT_RECIPIENTS = [
    'Naresh.m@lumen.com',
    'Prithviraj.Nayak@lumen.com',
    'your.email@lumen.com',  # Add more recipients
]
```

## Management Commands

### Disable Email Reports

```powershell
# Disable scheduled task
Disable-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

### Re-enable Email Reports

```powershell
# Enable scheduled task
Enable-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

### Remove Email Reports

```powershell
# Remove scheduled task
Unregister-ScheduledTask -TaskName "Level3_BI_Email_Report" -Confirm:$false
```

### Change Schedule

Edit the task in Task Scheduler (`taskschd.msc`) or re-run setup script with different parameters.

## Testing in Development

During development, emails are printed to console instead of being sent:

```powershell
# In development (DEBUG=True), emails appear in console
python manage.py send_level3_bi_email
```

Output will show the email content in the terminal.

## Production Deployment

For production:

1. **Set DEBUG=False** in settings.py
2. **Configure SMTP** with production SMTP server
3. **Set EMAIL_BACKEND** to `django.core.mail.backends.smtp.EmailBackend`
4. **Configure firewall** to allow SMTP traffic
5. **Test email sending** before scheduling

## Support

For issues or questions:
- Check logs in `monitorportal/logs/`
- Review SMTP configuration in `settings.py`
- Test with `--test` flag to isolate email issues
- Contact IT for SMTP relay configuration

---

**Last Updated**: April 10, 2026
