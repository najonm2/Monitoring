# Informatica Workflow Schedule Troubleshooting Guide

## Overview
This guide helps you debug scheduling failures and view scheduled workflows.

## ✅ New Features Implemented

### 1. **Enhanced Error Display**
- Schedule failures now show **detailed pmcmd output** in the UI
- Error messages include the exact command output from Informatica

### 2. **Scheduled Workflows List**
- View all currently scheduled workflows
- Shows: Folder Name, Workflow Name, Schedule Name, Status
- Accessible from the Schedule Workflow page

## 🔍 Debugging Schedule Failures

### Step 1: Check the Error Details
When scheduling fails, the UI now displays:
- ❌ Error message
- **Details:** section with pmcmd command output

Common error messages:
- `[ICMD_10056] Workflow [workflow_name] is already scheduled`
- `[ICMD_10004] Workflow [workflow_name] is disabled`
- `[PCSF_46007] No gateway connectivity`
- `[ICMD_10005] Workflow [workflow_name] does not exist`

### Step 2: Verify Prerequisites
```powershell
# Check if workflow exists in folder
# Run from PowerShell in your monitorportal directory

python manage.py shell
```

Then in Python shell:
```python
from portal.services.informatica_restart_service import InformaticaRestartService
service = InformaticaRestartService()

# Test connection
result = service.establish_connection()
print(result)

# Test schedule command
result = service.schedule_workflow(
    workflow_name="YOUR_WORKFLOW_NAME",
    folder_name="YOUR_FOLDER_NAME",
    integration_service="IS_GRID_BI"  # or appropriate grid
)
print(result)
```

### Step 3: Common Solutions

#### Error: "Workflow is already scheduled"
**Solution:** Unschedule first, then schedule again
1. Select **Unschedule** option in the form
2. Submit to unschedule
3. Then select **Schedule** option
4. Submit to schedule

#### Error: "Workflow is disabled"
**Solution:** Enable the workflow in Workflow Manager first
```bash
# Or use pmcmd to enable it (requires additional permissions)
pmcmd enableworkflow -sv IS_GRID_BI -d Domain_INFA_PRD1 -u username -p password -f folder_name workflow_name
```

#### Error: "No gateway connectivity"
**Solution:** Check the connection
- Verify pmrep connection is established
- Check domains.infa file path
- Verify network connectivity to Informatica server

#### Error: "Workflow does not exist"
**Solution:** 
- Verify exact workflow name (case-sensitive)
- Verify folder name is correct
- Check if workflow exists using Workflow Status Checker

## 📋 View Scheduled Workflows

### From UI:
1. Navigate to: http://127.0.0.1:8000/informatica/schedule-workflow/
2. Scroll down to "Currently Scheduled Workflows" section
3. Click **🔄 Refresh List** button

### From API:
```bash
# GET request
curl http://127.0.0.1:8000/api/informatica/scheduled-workflows/
```

### Response Format:
```json
{
  "success": true,
  "workflows": [
    {
      "workflow_name": "wkf_Load_Data",
      "folder_name": "ETL_Folder",
      "schedule_name": "Daily_8AM",
      "is_enabled": 1
    }
  ],
  "count": 1
}
```

## 🛠️ Manual Testing with pmcmd

### Test Schedule Command Directly:
```powershell
cd "C:\Informatica\CDIPC_Client\clients\PowerCenterClient\CommandLineUtilities\PC\server\bin"

# First connect to repository
.\PmRep.exe connect -r PCREPO_PRD1_01 -d Domain_INFA_PRD1 -n ab64033 -s CTL -x YOUR_PASSWORD -h azeus2lipcp01 -o 6005

# Then schedule workflow
.\PmCmd.exe scheduleworkflow -sv IS_GRID_BI -d Domain_INFA_PRD1 -u ab64033 -p YOUR_PASSWORD -f YOUR_FOLDER workflow_name
```

### Test Unschedule Command:
```powershell
.\PmCmd.exe unscheduleworkflow -sv IS_GRID_BI -d Domain_INFA_PRD1 -u ab64033 -p YOUR_PASSWORD -f YOUR_FOLDER workflow_name
```

### Check Command Output:
- **Return code 0** = Success
- **Non-zero return code** = Failure (check stderr for details)

## 📊 Database Query for Scheduled Workflows

If the API doesn't work, you can query the repository directly:

```sql
-- Query 1: Using OPB_SCHED_WORKFLOW table
SELECT 
    WORKFLOW_NAME,
    SUBJECT_AREA AS FOLDER_NAME,
    SCHEDULER_NAME AS SCHEDULE_NAME,
    IS_ENABLED,
    START_TIME,
    END_TIME
FROM INFA_PCREPO.OPB_SCHED_WORKFLOW
WHERE IS_ENABLED = 1
ORDER BY SUBJECT_AREA, WORKFLOW_NAME;

-- Query 2: Alternative using REP_SCHEDULER table
SELECT 
    WORKFLOW_NAME,
    FOLDER_NAME,
    SCHEDULE_NAME,
    IS_SCHEDULED
FROM INFA_PCREPO.REP_SCHEDULER
WHERE IS_SCHEDULED = 'Y'
ORDER BY FOLDER_NAME, WORKFLOW_NAME;
```

## 🔐 Permissions Required

To schedule/unschedule workflows, you need:
- **Read permission** on the folder
- **Write permission** on the workflow
- **Execute permission** on the workflow
- **Schedule permission** on the Integration Service

Contact your Informatica administrator if you lack permissions.

## 📝 Logging

Schedule operations are logged in:
- Django console output
- Python logging (if configured)
- pmcmd writes to: `$INFA_HOME/server/infa_shared/Logs/`

## 🆘 Still Having Issues?

1. **Check pmcmd path** is correct in settings.py:
   ```python
   INFORMATICA_PMCMD_PATH = r"C:\Informatica\CDIPC_Client\clients\PowerCenterClient\CommandLineUtilities\PC\server\bin\PmCmd.exe"
   ```

2. **Verify domains.infa file** location:
   ```python
   INFORMATICA_DOMAINS_FILE = r"C:\Informatica\CDIPC_Client\clients\PowerCenterClient\CommandLineUtilities\PC\domains.infa"
   ```

3. **Test basic connectivity**:
   - Can you restart workflows? (If yes, connection is OK)
   - Can you view workflow status? (If yes, repository access is OK)

4. **Review error details** carefully - the detailed error output usually contains the exact reason for failure

## 📧 Support

If you continue to have issues:
- Capture the **full error message** from the UI
- Copy the **Details** section (pmcmd output)
- Note the **workflow name**, **folder name**, and **integration service** you're using
- Check if the workflow is currently running (can't schedule running workflows)
