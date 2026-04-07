# Informatica Workflow Restart Feature - Setup Guide

## Overview

This feature allows you to restart failed Informatica PowerCenter workflows directly from the portal with a single click.

## Features

✅ **One-Click Restart** - Restart workflows directly from the failed jobs page
✅ **Secure Authentication** - Uses your Informatica credentials configured in settings
✅ **Real-time Feedback** - Shows success/failure messages immediately
✅ **Safe Operation** - Requires confirmation before restarting
✅ **Error Handling** - Provides detailed error messages if restart fails

---

## Setup Instructions

### Step 1: Configure Informatica Connection

You need to set up your Informatica PowerCenter connection details. You can do this in two ways:

#### Option A: Environment Variables (Recommended for Production)

Set these environment variables on your Linux server:

```bash
export INFORMATICA_PMCMD_PATH="/prd1/app/informatica/infa_shared/server/bin/pmcmd"
export INFORMATICA_DOMAIN="Domain_PROD"
export INFORMATICA_REPOSITORY="PC_REPO_PROD"
export INFORMATICA_INTEGRATION_SERVICE="IDG01P"
export INFORMATICA_USERNAME="your_username"
export INFORMATICA_PASSWORD="your_password"
export INFORMATICA_DEFAULT_FOLDER="Production"
```

#### Option B: Edit Settings File (For Testing)

Edit `monitorportal/monitorportal/settings.py` and update these values:

```python
# -----------------------------------------------------------------------------
# INFORMATICA POWERCENTER CONFIGURATION (for workflow restart)
# -----------------------------------------------------------------------------
INFORMATICA_PMCMD_PATH = '/prd1/app/informatica/infa_shared/server/bin/pmcmd'
INFORMATICA_DOMAIN = 'Domain_PROD'
INFORMATICA_REPOSITORY = 'PC_REPO_PROD'
INFORMATICA_INTEGRATION_SERVICE = 'IDG01P'
INFORMATICA_USERNAME = 'your_username'
INFORMATICA_PASSWORD = 'your_password'
INFORMATICA_DEFAULT_FOLDER = 'Production'
```

### Step 2: Verify pmcmd is Available

On your Linux server, verify pmcmd is accessible:

```bash
# Check if pmcmd exists
which pmcmd
# OR check specific path
/prd1/app/informatica/infa_shared/server/bin/pmcmd -version

# Expected output: PowerCenter version information
```

### Step 3: Test Configuration (Optional but Recommended)

Test the configuration from Django shell:

```python
cd /path/to/monitorportal
python manage.py shell

# In Python shell:
from portal.services.informatica_restart_service import InformaticaRestartService

service = InformaticaRestartService()
print("Configuration valid:", service.is_configured())

# Test a workflow status check (doesn't restart):
result = service.get_workflow_status('YOUR_WORKFLOW_NAME', 'YOUR_FOLDER_NAME')
print(result)
```

### Step 4: Restart Django Server

```bash
# Stop current server (if running)
pkill -f "python manage.py runserver"

# Start server
cd /path/to/monitorportal
python manage.py runserver 0.0.0.0:8000
```

---

## How to Use

### From the Portal UI

1. **Navigate to Failed Jobs**
   - Go to: `http://your-server:8000/dashboards/level3/`
   - Click on any Level3 failed jobs report

2. **Find the Failed Workflow**
   - Look at the failed jobs table
   - Find the workflow you want to restart

3. **Click the Restart Button**
   - Click the green "🔄 Restart" button for that workflow
   - Confirm the action in the popup dialog

4. **Wait for Result**
   - The button will show "⏳ Restarting..." while processing
   - You'll see a success or error message

---

## API Usage (For Automation)

You can also restart workflows via API:

### Restart Workflow

```bash
curl -X POST http://your-server:8000/api/informatica/restart-workflow/ \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "WF_DailyLoad_Customer",
    "folder_name": "Production"
  }'
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Workflow \"WF_DailyLoad_Customer\" restarted successfully",
  "workflow": "WF_DailyLoad_Customer",
  "folder": "Production",
  "output": "...pmcmd output..."
}
```

**Response (Failure):**
```json
{
  "success": false,
  "message": "Failed to restart workflow \"WF_DailyLoad_Customer\"",
  "error": "...error details...",
  "workflow": "WF_DailyLoad_Customer",
  "folder": "Production"
}
```

### Check Workflow Status

```bash
curl -X POST http://your-server:8000/api/informatica/check-workflow-status/ \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "WF_DailyLoad_Customer",
    "folder_name": "Production"
  }'
```

---

## Configuration Details

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `INFORMATICA_PMCMD_PATH` | Full path to pmcmd executable | `/prd1/app/informatica/infa_shared/server/bin/pmcmd` |
| `INFORMATICA_DOMAIN` | PowerCenter domain name | `Domain_PROD` |
| `INFORMATICA_REPOSITORY` | Repository name | `PC_REPO_PROD` |
| `INFORMATICA_INTEGRATION_SERVICE` | Integration service name | `IDG01P` |
| `INFORMATICA_USERNAME` | PowerCenter login username | `infaadmin` |
| `INFORMATICA_PASSWORD` | PowerCenter login password | `********` |
| `INFORMATICA_DEFAULT_FOLDER` | Default folder for workflows | `Production` |

### Finding Your Configuration Values

If you're not sure about these values, ask your Informatica administrator or check:

1. **Domain Name**: Check Informatica Administrator Console
2. **Repository Name**: Shown in PowerCenter Repository Manager
3. **Integration Service**: Shown in Administrator Console under Services
4. **Folder Name**: Usually matches "subject_area" from your database (e.g., Finance, HR, Sales)

---

## Troubleshooting

### Error: "pmcmd not found"

**Solution:**
- Verify `INFORMATICA_PMCMD_PATH` is correct
- Check that pmcmd is executable: `chmod +x /path/to/pmcmd`
- Ensure you're using the correct path for your environment

### Error: "Invalid credentials"

**Solution:**
- Verify `INFORMATICA_USERNAME` and `INFORMATICA_PASSWORD` are correct
- Test login manually: `pmcmd connect -r REPO -d DOMAIN -u USERNAME -p PASSWORD`

### Error: "Workflow not found"

**Solution:**
- Verify the folder name is correct (case-sensitive)
- Check that the workflow exists in that folder
- Use PowerCenter Repository Manager to confirm

### Error: "Connection to Integration Service failed"

**Solution:**
- Verify `INFORMATICA_INTEGRATION_SERVICE` name is correct
- Check that the Integration Service is running
- Ensure network connectivity from portal server to Informatica server

### Portal Shows: "Informatica PowerCenter is not configured"

**Solution:**
- Check that all required environment variables are set
- Verify settings.py has the correct values
- Restart Django server after changing configuration

---

## Security Considerations

1. **Credentials Storage**
   - Use environment variables in production (not hardcoded in settings.py)
   - Ensure settings.py has restricted file permissions: `chmod 600 settings.py`
   - Never commit credentials to version control

2. **Access Control**
   - Only trusted users should have access to the portal
   - Consider adding authentication checks before allowing restarts
   - Monitor restart activity in Informatica logs

3. **Audit Trail**
   - All restarts are logged in Django logs
   - Informatica also logs workflow restarts in its audit logs
   - Review logs regularly for unauthorized access

---

## Advanced Usage

### Restart from Specific Task

If you want to restart from a specific task (not from the beginning), you can modify the API call:

```bash
curl -X POST http://your-server:8000/api/informatica/restart-workflow/ \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "WF_DailyLoad_Customer",
    "folder_name": "Production",
    "restart_from_task": "TASK_NAME_HERE"
  }'
```

### Automated Restart Scripts

You can create a bash script to restart multiple workflows:

```bash
#!/bin/bash
# restart_failed_workflows.sh

WORKFLOWS=("WF_Daily_Load" "WF_Monthly_Agg" "WF_Data_Quality")
FOLDER="Production"

for workflow in "${WORKFLOWS[@]}"; do
    echo "Restarting: $workflow"
    curl -X POST http://localhost:8000/api/informatica/restart-workflow/ \
      -H "Content-Type: application/json" \
      -d "{\"workflow_name\":\"$workflow\",\"folder_name\":\"$FOLDER\"}"
    echo ""
    sleep 5
done
```

---

## Files Modified/Created

### New Files:
- `portal/services/informatica_restart_service.py` - Restart service implementation
- `WORKFLOW_RESTART_GUIDE.md` - This documentation

### Modified Files:
- `monitorportal/settings.py` - Added Informatica configuration
- `portal/api_views.py` - Added restart and status check endpoints
- `portal/urls.py` - Added URL routes for new endpoints
- `portal/templates/portal/level3_failed_jobs_status.html` - Added restart button

---

## Support

If you encounter issues:

1. Check Django logs for detailed error messages
2. Test pmcmd manually from command line
3. Verify all configuration parameters are correct
4. Check Informatica server logs
5. Contact your Informatica administrator if needed

---

## Next Steps

After setup:
1. Test with a non-critical workflow first
2. Monitor the first few restarts to ensure they work correctly
3. Train your team on how to use the feature
4. Set up alerts for failed restart attempts
5. Consider adding more advanced features (scheduled restarts, bulk restarts, etc.)
