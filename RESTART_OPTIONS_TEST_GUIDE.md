# Informatica Restart Options Test Guide

## Quick Start

The `test_restart_options.py` script tests all 4 restart options available in the Informatica Restart Service.

### Prerequisites

1. Django environment configured
2. Virtual environment activated
3. Informatica credentials set in Django settings
4. Access to Informatica PowerCenter environment

### Configuration Steps

1. **Open the test script:**
   ```bash
   test_restart_options.py
   ```

2. **Update the configuration section (lines 21-30):**
   ```python
   TEST_WORKFLOW = 'YOUR_WORKFLOW_NAME'  # Replace with actual workflow
   TEST_FOLDER = 'YOUR_FOLDER_NAME'      # Replace with actual folder
   TEST_SESSION = 'YOUR_SESSION_NAME'    # Replace with actual session/task
   ```

3. **Choose which tests to run:**
   ```python
   RUN_OPTION_1 = True  # Restart Task Only
   RUN_OPTION_2 = True  # Restart Workflow from Task
   RUN_OPTION_3 = True  # Restart Entire Workflow
   RUN_OPTION_4 = True  # Recover Workflow from Task
   ```

4. **Set dry run mode:**
   ```python
   DRY_RUN = True   # Shows commands without executing
   DRY_RUN = False  # Actually executes the commands
   ```

### Running the Tests

#### Dry Run (Safe - No Execution)
```bash
# Activate virtual environment first
.venv\Scripts\activate

# Run in dry run mode (default)
python test_restart_options.py
```

This will:
- ✓ Verify configuration
- ✓ Show what commands would be executed
- ✓ Not actually restart anything
- ✓ Safe to run anytime

#### Actual Execution
```bash
# First, update DRY_RUN = False in the script
# Then run:
python test_restart_options.py
```

⚠️ **WARNING:** This will actually restart workflows!

### The 4 Restart Options Explained

#### Option 1: Restart Task Only
```python
restart_option=1
```
- **What it does:** Restarts ONLY the specified task/session
- **Use when:** You want to re-run a single failed task
- **Requires:** `session_name` parameter
- **Command:** `pmcmd starttask -w {workflow} {session}`

#### Option 2: Restart Workflow from Task
```python
restart_option=2
```
- **What it does:** Restarts the workflow starting FROM the specified task
- **Use when:** You want to restart from a specific point forward
- **Requires:** `session_name` parameter
- **Command:** `pmcmd startworkflow -startfrom {session} {workflow}`

#### Option 3: Restart Entire Workflow
```python
restart_option=3
```
- **What it does:** Restarts the entire workflow from the beginning
- **Use when:** You want a complete fresh run
- **Requires:** No session name needed
- **Command:** `pmcmd startworkflow {workflow}`

#### Option 4: Recover Workflow from Task
```python
restart_option=4
```
- **What it does:** Recovers the workflow using recovery mode from specified task
- **Use when:** Workflow failed and you want to resume from failure point
- **Requires:** `session_name` parameter
- **Command:** `pmcmd startworkflow -startfrom {session} -recovery {workflow}`

### Example Test Output

```
================================================================================
  Verifying Configuration
================================================================================
ℹ INFO: Checking Django Settings:
  Domain: Domain_PROD
  Repository: PC_REPO_PROD
  Integration Service: IDG01P
  Username: informatica_user
  Password: ********
  ...

================================================================================
  Test Option 1: Restart Task Only
================================================================================
ℹ INFO: This will restart ONLY the task: s_Load_Customer_Data
ℹ INFO: Workflow: wf_Customer_ETL
ℹ INFO: Folder: Production
⚠ WARNING: DRY RUN - Command would be executed here
ℹ INFO: Expected pmcmd command:
  pmcmd starttask -sv IDG01P \
    -d Domain_PROD -u informatica_user \
    -p **** -f Production -w wf_Customer_ETL s_Load_Customer_Data

Result:
  success: True
  message: DRY RUN - not executed
✓ SUCCESS: Option 1 test completed successfully
```

### Using in Production Code

Once tested, you can use the service in your Django views:

```python
from portal.services.informatica_restart_service import InformaticaRestartService

# Initialize service
service = InformaticaRestartService()

# Option 1: Restart a specific task
result = service.restart_with_options(
    workflow_name='wf_Customer_ETL',
    folder_name='Production',
    restart_option=1,
    session_name='s_Load_Customer_Data'
)

# Option 3: Restart entire workflow
result = service.restart_with_options(
    workflow_name='wf_Customer_ETL',
    folder_name='Production',
    restart_option=3
)

# Check result
if result['success']:
    print(f"Success: {result['message']}")
else:
    print(f"Failed: {result['error']}")
```

### Troubleshooting

#### Configuration Not Found
```
✗ ERROR: Informatica service is not fully configured
```
**Solution:** Check your Django settings file for all required Informatica settings:
- `INFORMATICA_PMCMD_PATH`
- `INFORMATICA_DOMAIN`
- `INFORMATICA_REPOSITORY`
- `INFORMATICA_INTEGRATION_SERVICE`
- `INFORMATICA_USERNAME`
- `INFORMATICA_PASSWORD`

#### Workflow/Session Not Found
```
✗ ERROR: Failed to restart workflow
```
**Solution:** 
- Verify workflow name is correct (case-sensitive)
- Verify folder name is correct
- Verify session name exists in the workflow
- Check you have permissions to the folder

#### pmcmd Not Found
```
✗ ERROR: pmcmd not found
```
**Solution:** Update `INFORMATICA_PMCMD_PATH` in Django settings to point to correct pmcmd.exe location

#### Timeout Error
```
✗ ERROR: Workflow restart timed out after 5 minutes
```
**Solution:** This is normal for long-running workflows. The workflow is still running in the background.

### Django Settings Example

Add to your `settings.py`:

```python
# Informatica PowerCenter Configuration
INFORMATICA_PMCMD_PATH = r'C:\Program Files\Informatica\10.5.0\clients\PowerCenterClient\client\bin\pmcmd.exe'
INFORMATICA_DOMAIN = 'Domain_PROD'
INFORMATICA_REPOSITORY = 'PC_REPO_PROD'
INFORMATICA_INTEGRATION_SERVICE = 'IDG01P'
INFORMATICA_USERNAME = 'your_username'
INFORMATICA_PASSWORD = 'your_password'
INFORMATICA_USER_SECURITY_DOMAIN = ''  # Optional
INFORMATICA_DEFAULT_FOLDER = 'Production'  # Optional
```

### Best Practices

1. **Always test in DRY_RUN mode first**
   - Verify configuration is correct
   - See what commands will be executed
   - Ensure workflow/session names are correct

2. **Use appropriate restart option**
   - Option 1 for single task failures
   - Option 2 to continue from a specific point
   - Option 3 for complete reruns
   - Option 4 for recovery after failures

3. **Monitor after restart**
   - Check Informatica Workflow Monitor
   - Review logs for errors
   - Verify data consistency

4. **Error handling**
   - Always check the `success` flag in results
   - Log the `error` message for debugging
   - Handle timeouts gracefully (workflow may still run)

### Related Files

- `informatica_restart_service.py` - Main service implementation
- `test_restart_options.py` - This test script
- `test_informatica_restart.py` - Basic connection tests
- `INFORMATICA_RESTART_INTEGRATION.md` - Integration documentation
