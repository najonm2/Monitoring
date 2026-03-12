# ERP Run Recovery Tracking System

## Overview

The Recovery Tracking System allows you to mark ERP runs that were suspended/failed but later manually recovered as "Successfully Recovered" on the dashboard. This provides accurate historical tracking of manual interventions.

## How It Works

### Database Reality
When ERP runs are suspended or fail, the IICS system records that status permanently in the `IICS_CDI_RUN_INFO` table. Even if you manually resume and complete the run, the historical record remains "CHILD_SUSPENDED" or "FAILED".

### The Solution
We've implemented a custom tracking system that:
1. **Stores recovery actions** in a Django database table (`ERPRunRecovery`)
2. **Overlays recovery status** on the dashboard
3. **Shows who recovered it** and when
4. **Displays recovery notes** for audit purposes

---

## Three Ways to Mark Runs as Recovered

### Method 1: Command-Line Script (Fastest)

**List suspended runs:**
```bash
cd monitorportal
python mark_run_recovered.py
```

**Mark a run as recovered:**
```bash
python mark_run_recovered.py <TASKFLOW_RUN_ID> <your_email> <recovery_notes>
```

**Example:**
```bash
python mark_run_recovered.py 1215720696580263936 "john.doe@lumen.com" "Manually resumed all suspended subtasks via IICS Monitor"
```

---

### Method 2: Django Admin Interface

1. **Access Django Admin:**
   - Navigate to: `http://127.0.0.1:8000/admin/`
   - Login with admin credentials

2. **Add Recovery Record:**
   - Go to **Portal** → **ERP Run Recoveries** → **Add ERP Run Recovery**
   - Fill in the form:
     - **TASKFLOW_RUN_ID**: Copy from the dashboard (e.g., `1215720696580263936`)
     - **Run Start Time**: Date/time the run originally started
     - **Original Status**: SUSPENDED or FAILED
     - **Recovered By**: Your email or name
     - **Recovery Notes**: Description of what you did
     - **Final Status**: Usually SUCCESS
     - **Is Active**: Check this box
   - Click **Save**

3. **View All Recoveries:**
   - Go to **Portal** → **ERP Run Recoveries**
   - See all marked recoveries with search and filtering

---

### Method 3: Python Script (For Automation)

Create a custom Python script:

```python
import sys
import os
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.models import ERPRunRecovery

# Create recovery record
recovery = ERPRunRecovery.objects.create(
    taskflow_run_id='1215720696580263936',
    run_start_time=datetime(2026, 3, 9, 12, 0, 0),
    original_status='SUSPENDED',
    recovered_by='automation@lumen.com',
    recovery_notes='Auto-recovered via scheduled task',
    final_status='SUCCESS',
    is_active=True
)

print(f"Recovery marked: {recovery}")
```

---

## Dashboard Display

### Before Recovery is Marked:
```
Status: SUSPENDED (12 jobs, 0 succeeded)
```

### After Recovery is Marked:
```
Status: ✓ SUCCESS (Recovered)
Recovered: 2026-03-10 14:30:15
```

**Hover over the status badge** to see:
- Who recovered it
- When it was recovered
- Recovery notes

---

## Example Workflow

### Scenario: 12:00 PM Run Suspended

1. **Run fails at 12:00 PM** - All subtasks suspended
2. **You manually resume tasks** in IICS Monitor
3. **Tasks complete successfully** by 12:48 PM
4. **Database still shows:** CHILD_SUSPENDED (permanent historical record)
5. **You mark recovery:**
   ```bash
   python mark_run_recovered.py 1215720696580263936 "jane.smith@lumen.com" "Manually resumed via IICS - all tasks completed"
   ```
6. **Dashboard now shows:** ✓ SUCCESS (Recovered)

---

## Finding TASKFLOW_RUN_IDs

### Method 1: From ERP Dashboard
- Go to: `http://127.0.0.1:8000/dashboards/erp/`
- Look at the "Last 8 Runs" table
- The TASKFLOW_RUN_ID is shown in the table (very long number)

### Method 2: From the Recovery Script
```bash
python mark_run_recovered.py
```
This lists all suspended runs with their TASKFLOW_RUN_IDs

### Method 3: From IICS Monitor
- In IICS Informatica Cloud
- Monitor → Jobs
- Click on the run
- Look for "Taskflow Run ID" in the details

---

## Managing Recovery Records

### View All Recoveries:
```bash
# Via Django Admin
http://127.0.0.1:8000/admin/portal/erprunrecovery/
```

### Deactivate a Recovery (Hide from Dashboard):
1. Go to Django Admin → ERP Run Recoveries
2. Find the record
3. Uncheck "Is Active"
4. Save

### Update Recovery Notes:
1. Go to Django Admin → ERP Run Recoveries
2. Find the record
3. Edit "Recovery Notes"
4. Save

---

## Database Schema

### ERPRunRecovery Model

| Field | Type | Description |
|-------|------|-------------|
| taskflow_run_id | VARCHAR(100) | IICS Taskflow Run ID (unique) |
| run_start_time | DATETIME | Original run start time (MST) |
| original_status | VARCHAR(50) | Status before recovery (SUSPENDED, FAILED) |
| recovered_at | DATETIME | When marked as recovered (auto) |
| recovered_by | VARCHAR(200) | Person who recovered (email/name) |
| recovery_notes | TEXT | Details about recovery action |
| final_status | VARCHAR(50) | Status after recovery (SUCCESS) |
| is_active | BOOLEAN | Show on dashboard (True/False) |

---

## Best Practices

### ✅ DO:
- Mark recoveries promptly after manual intervention
- Include detailed notes about what was done
- Use your email address for accountability
- Check the dashboard after marking to verify display

### ❌ DON'T:
- Mark runs that genuinely failed as recovered
- Use recovery tracking for successful runs
- Leave recovery notes empty
- Mark the same run multiple times (script prevents this)

---

## Troubleshooting

### Recovery Doesn't Show on Dashboard
**Check:**
1. Is `is_active=True`?
2. Did you refresh the dashboard (wait 30 seconds for cache)?
3. Is the TASKFLOW_RUN_ID correct and an exact match?

### Can't Find TASKFLOW_RUN_ID
**Solution:**
```bash
python mark_run_recovered.py
```
This lists all recent suspended runs with IDs

### Admin Interface Not Working
**Check:**
1. Is Django server running?
2. Are you logged in as admin?
3. Was the migration applied? (`python manage.py migrate portal`)

---

## Example Commands

**List suspended runs to recover:**
```bash
cd monitorportal
python mark_run_recovered.py
```

**Mark the 12:00 PM run as recovered:**
```bash
python mark_run_recovered.py 1215720696580263936 "your.email@lumen.com" "Manually resumed all 12 suspended subtasks"
```

**Mark the 8:00 PM run as recovered:**
```bash
python mark_run_recovered.py 1215479110705471488 "your.email@lumen.com" "Restarted failed workflows, completed successfully"
```

**Mark with partial completion:**
```bash
python mark_run_recovered.py 1215358312988663810 "admin@lumen.com" "Recovered 10 of 12 tasks, 2 skipped" PARTIAL
```

---

## Technical Details

### What Changed:
1. **New Django Model:** `ERPRunRecovery` in `portal/models.py`
2. **Database Migration:** `portal/migrations/0003_erprunrecovery.py`
3. **Dashboard Logic:** Modified `portal/erp_mdm_insights.py` to check recoveries
4. **Template Update:** Modified `portal/templates/portal/erp_job_status.html` to display recovery status
5. **Admin Interface:** Added to `portal/admin.py`
6. **Helper Script:** Created `mark_run_recovered.py`

### Recovery Lookup Process:
1. Dashboard fetches last 8 runs from IICS
2. Extracts all TASKFLOW_RUN_IDs
3. Queries `ERPRunRecovery` table for matching active records
4. Overlays recovery status on runs with matches
5. Displays "SUCCESS (Recovered)" with recovery metadata

---

## Support

**Issues:** Check Django logs for errors
**Questions:** Review this guide or Django Admin documentation
**Testing:** Mark a test recovery and verify on dashboard

---

## Summary

✅ **Suspended runs now trackable** - Mark manual recoveries  
✅ **Three marking methods** - Script, Admin UI, or Python code  
✅ **Dashboard displays recovery** - Shows who/when/why  
✅ **Audit trail maintained** - All recoveries logged with notes  
✅ **Simple to use** - One command to mark a recovery  

**Next Steps:**
1. Identify suspended runs that you manually recovered
2. Use `mark_run_recovered.py` to mark them
3. Refresh the dashboard to see the updated status
4. Share this guide with your team
