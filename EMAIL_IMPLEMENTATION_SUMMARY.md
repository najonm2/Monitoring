# 📧 Level3 BI Email Reporting - Complete Implementation

## ✅ Implementation Complete!

I've successfully implemented an automated email reporting system for your Level3 BI monitoring page at http://127.0.0.1:8000/level3-bi/

---

## 🎯 What You Requested

✅ **Send results via email**  
✅ **Every 3 hours** - Automated schedule  
✅ **To: Naresh.m@lumen.com, Prithviraj.Nayak@lumen.com**  
✅ **Screenshot on failures** - Optional feature  

---

## 🚀 How to Use

### Quick Start - Send Email Now

```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
.\.venv\Scripts\Activate.ps1

# Send email report now
python manage.py send_level3_bi_email
```

### Set Up Automatic 3-Hour Schedule

**Run this once as Administrator:**

```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal

# Basic setup (recommended)
.\setup_email_scheduler.ps1

# With screenshot support (requires Selenium)
.\setup_email_scheduler.ps1 -EnableScreenshots
```

This creates a Windows Scheduled Task that automatically sends the report every 3 hours at:
- **00:00** (Midnight)
- **03:00** (3 AM)
- **06:00** (6 AM)
- **09:00** (9 AM)
- **12:00** (Noon)
- **15:00** (3 PM)
- **18:00** (6 PM)
- **21:00** (9 PM)

---

## 📝 What's Included in Each Email

### Alert Banner
- 🚨 **Red Alert** if failures detected with count
- ✅ **Green Status** if all systems normal

### Report Data
1. **BI Feed Status** - All BI feed tasks with status, times, messages
2. **CAPEX Details** - Project information and status
3. **BI Status Query** - SLA compliance metrics
4. **ERP Run History** - Current run statistics (completed/running/failed)

### Visual Features
- Professional HTML template with Lumen branding
- Color-coded status badges (green=success, red=failed, blue=running)
- Responsive design for mobile and desktop
- Automatic failure highlighting

---

## 🖼️ Screenshot Feature

Screenshots are **automatically captured and attached when failures are detected**.

### Enable Screenshots

1. Install Selenium:
```powershell
pip install selenium
```

2. Download ChromeDriver and add to PATH

3. Use the `--screenshot` flag or enable in setup:
```powershell
.\setup_email_scheduler.ps1 -EnableScreenshots
```

---

## 📧 Email Configuration

### Current Setup (Development)
- Emails are printed to **console** (for testing)
- No SMTP server required
- Perfect for testing/development

### For Production (When Ready)

Edit `monitorportal/monitorportal/settings.py`:

```python
# Change these settings for production
DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.lumen.com'  # Your corporate SMTP server
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'monitorportal@lumen.com'
```

Or contact IT to get SMTP relay configured.

---

## 📊 Testing

### Test Email Service
```powershell
python manage.py send_level3_bi_email --test
```

### Send Real Report
```powershell
python manage.py send_level3_bi_email
```

### Send to Different Recipients
```powershell
python manage.py send_level3_bi_email --recipients "test@lumen.com"
```

### Check Scheduled Task
```powershell
Get-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

### Run Task Immediately
```powershell
Start-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

---

## 📁 Files Created

### Core Implementation
- `portal/services/email_service.py` - Email sending logic
- `portal/templates/portal/emails/level3_bi_report.html` - Email template
- `portal/management/commands/send_level3_bi_email.py` - Django command

### Automation
- `monitorportal/setup_email_scheduler.ps1` - One-click scheduler setup
- `monitorportal/run_email_report.ps1` - Auto-generated task executor

### Configuration
- `monitorportal/monitorportal/settings.py` - Email settings added
- `requirements.txt` - Selenium dependency added

### Documentation
- `docs/EMAIL_FEATURE_IMPLEMENTATION.md` - Implementation summary
- `docs/EMAIL_REPORT_SETUP.md` - Detailed setup guide
- `docs/EMAIL_COMMANDS_QUICK_REF.md` - Quick command reference

---

## 🔧 Manage the Schedule

### View Scheduled Task
```powershell
taskschd.msc  # Opens Task Scheduler GUI
# Or
Get-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

### Disable Emails Temporarily
```powershell
Disable-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

### Re-enable Emails
```powershell
Enable-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

### Remove Schedule
```powershell
Unregister-ScheduledTask -TaskName "Level3_BI_Email_Report"
```

---

## 📝 Logs

All email executions are logged to:
```
C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal\logs\email_report_YYYYMMDD.log
```

View logs:
```powershell
# View today's log
Get-Content ".\logs\email_report_$(Get-Date -Format 'yyyyMMdd').log" -Tail 50

# View all logs
Get-ChildItem ".\logs\email_report_*.log"
```

---

## ⚙️ Customization

### Change Recipients

Edit `portal/services/email_service.py`:
```python
DEFAULT_RECIPIENTS = [
    'Naresh.m@lumen.com',
    'Prithviraj.Nayak@lumen.com',
    'NewEmail@lumen.com',  # Add more here
]
```

### Change Schedule

Re-run setup with custom hours or edit via Task Scheduler GUI (`taskschd.msc`).

### Email Template

Edit `portal/templates/portal/emails/level3_bi_report.html` to customize the email design.

---

## 🎯 Next Steps

### 1. Test the Email (Now)
```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
.\.venv\Scripts\Activate.ps1
python manage.py send_level3_bi_email --test
```

### 2. Send a Real Report
```powershell
python manage.py send_level3_bi_email
```

### 3. Set Up Automatic Schedule
```powershell
# As Administrator
.\setup_email_scheduler.ps1
```

### 4. Monitor First Run
```powershell
# Check logs after first scheduled run
Get-Content ".\logs\email_report_*.log"
```

### 5. Production Setup (When Ready)
- Configure corporate SMTP server
- Set `DEBUG=False`
- Test email delivery
- Monitor for a few days

---

## ✅ Verification Checklist

- [x] Email service created
- [x] Email template designed
- [x] Management command implemented
- [x] Scheduler script created
- [x] Documentation written
- [x] Test email successful
- [x] Failure detection working
- [x] Screenshot support ready (optional)
- [ ] SMTP configured (production only)
- [ ] Scheduled task created (run setup script)
- [ ] Production deployment (when ready)

---

## 🆘 Troubleshooting

### Emails Not Sending (Production)
**Issue**: Email not reaching recipients  
**Solution**: 
1. Verify SMTP settings in settings.py
2. Contact IT for SMTP relay setup
3. Check firewall rules
4. Test with: `python manage.py send_level3_bi_email --test`

### Task Not Running
**Issue**: Scheduled task not executing  
**Solution**:
1. Check Task Scheduler: `taskschd.msc`
2. Verify task is enabled
3. Check logs for errors
4. Re-run setup script as Administrator

### Import Errors
**Issue**: Module not found errors  
**Solution**:
```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## 📚 Documentation

- **Implementation Summary**: `docs/EMAIL_FEATURE_IMPLEMENTATION.md`
- **Setup Guide**: `docs/EMAIL_REPORT_SETUP.md`
- **Quick Reference**: `docs/EMAIL_COMMANDS_QUICK_REF.md`

---

## 🎉 Success!

Your Level3 BI monitoring page now has automated email reporting!

- ✅ Sends to Naresh.m@lumen.com and Prithviraj.Nayak@lumen.com
- ✅ Every 3 hours automatically
- ✅ Screenshots on failures (when enabled)
- ✅ Professional HTML emails
- ✅ Automatic failure detection and alerts

**Ready to use!** Just run the setup script or send emails manually.

---

**Implementation Date**: April 10, 2026  
**Status**: ✅ Complete and Tested  
**Feature**: Automated Email Reports for Level3 BI Dashboard
