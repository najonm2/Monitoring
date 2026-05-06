# Email Setup - No Admin Access Required ✅

## Overview

Since you don't have admin access to modify firewall rules, emails are saved as files that can be:
1. **Previewed in browser** (see what will be sent)
2. **Sent by someone with network access** (IT, colleague, or server)
3. **Automatically processed** via scheduled task (if server has access)

---

## 🚀 Quick Commands

### 1. Generate Email Report
```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
.\.venv\Scripts\Activate.ps1
python manage.py send_level3_bi_email
```
✅ **Creates email file in:** `sent_emails/` folder

### 2. Preview Email in Browser
```powershell
python preview_email.py
```
✅ **Opens latest email** in your default browser

### 3. Send Saved Emails (Requires Network Access)
```powershell
# Send all unsent emails
python send_saved_emails.py

# Send only latest
python send_saved_emails.py --latest

# Send specific file
python send_saved_emails.py --file sent_emails/20260410-103354-2746358358688.log
```
✅ **Sends via SMTP:** `mailrelay.corp.intranet:25`

---

## 📧 Complete Workflow

### **Step 1: Generate Email** (You - No Admin Access Needed)
```powershell
python manage.py send_level3_bi_email
```
- Creates email file in `sent_emails/` folder
- File format: `YYYYMMDD-HHMMSS-timestamp.log`

### **Step 2: Preview Email** (You - Optional)
```powershell
python preview_email.py
```
- Opens email in browser to verify content
- Shows subject, recipients, and full HTML

### **Step 3: Send Email** (Options)

#### **Option A: Copy to Network-Accessible Machine**
```powershell
# Copy these files to a server with SMTP access:
- send_saved_emails.py
- sent_emails/ folder

# On the server, run:
python send_saved_emails.py
```

#### **Option B: Ask IT/Admin to Run**
Give IT admin access to:
1. The `sent_emails/` folder
2. The `send_saved_emails.py` script
3. Instructions: `python send_saved_emails.py`

#### **Option C: Run on Scheduled Server**
If you have access to a server with network connectivity:
1. Copy project to server
2. Set up scheduled task there
3. Emails will auto-send every 3 hours

---

## 📁 File Locations

```
monitorportal/
├── sent_emails/              ← Email files saved here
│   ├── 20260410-103354.log   ← Unsent email
│   └── 20260410-113211.log.sent ← Already sent
├── send_saved_emails.py      ← SMTP sender script
├── preview_email.py          ← Browser preview script
└── manage.py
```

---

## 🎯 Recipients

**Default recipients:**
- Naresh.m@lumen.com
- Prithviraj.Nayak@lumen.com

**From email:** DWBIPASE@lumen.com  
**SMTP Server:** mailrelay.corp.intranet:25

---

## ⏰ Automated Schedule (3 Hours)

### If YOU Want to Auto-Generate Emails

Run this setup (no admin needed):
```powershell
.\setup_email_scheduler.ps1
```

This creates a task that runs every 3 hours to **generate** email files.  
Someone else (with network access) sends them later.

### If SERVER Has Network Access

Copy the entire project to a server and run:
```powershell
# On server with SMTP access
.\setup_email_scheduler.ps1 -EnableAutoSend
```

This both generates AND sends emails automatically.

---

## 📊 Email Content

Each email includes:
- ✅/🚨 Status banner (failures or all clear)
- 📈 BI Feed Status table
- 💰 CAPEX Details table
- 📊 BI Status Query (SLA metrics)
- 🏢 ERP Current Run statistics

---

## 🔧 Advanced Usage

### Change Recipients
Edit `portal/services/email_service.py`:
```python
DEFAULT_RECIPIENTS = [
    'Naresh.m@lumen.com',
    'Prithviraj.Nayak@lumen.com',
    'newperson@lumen.com',  # Add more
]
```

### Send Test Email
```powershell
python manage.py send_level3_bi_email --test
```

### View All Saved Emails
```powershell
Get-ChildItem sent_emails -File | Select-Object Name, Length, LastWriteTime
```

### Check Which Haven't Been Sent
```powershell
Get-ChildItem sent_emails\*.log -File | Where-Object {-not (Test-Path ($_.FullName + '.sent'))}
```

---

## ✅ What's Working Now

✓ **Email generation** - Works without admin access  
✓ **Email preview** - Opens in browser  
✓ **Email storage** - Saved to `sent_emails/` folder  
✓ **Send helper script** - Ready to use with network access  
✓ **Recipients configured** - Naresh & Prithviraj  
✓ **Schedule ready** - Can auto-generate every 3 hours  

---

## 🆘 Troubleshooting

### No Emails in sent_emails/ Folder
```powershell
# Check if folder exists
Test-Path sent_emails

# Generate email
python manage.py send_level3_bi_email
```

### Can't Preview Email
```powershell
# Install any missing dependencies
pip install -r requirements.txt

# Try opening file manually
explorer sent_emails
```

### Need to Send from Different Machine
1. Copy `sent_emails/` folder to network-accessible machine
2. Copy `send_saved_emails.py` to same machine
3. Run: `python send_saved_emails.py --all`

---

## 📞 Support

**For email generation issues:**
- Check: Python virtual environment activated
- Check: `sent_emails/` folder permissions

**For email sending issues:**
- Need: Network access to `mailrelay.corp.intranet:25`
- Contact: IT for SMTP relay access
- Alternative: Run `send_saved_emails.py` on server

---

**Summary:** You can generate and preview emails locally. Someone with network access (or a server) can send them.

**Last Updated:** April 10, 2026
