# Project Cleanup Plan

## Files to DELETE (Temporary/Test/Redundant)

### Test Scripts (not needed in production)
- check_databricks_setup.ps1
- check_data_source.bat
- check_master_workflow.py
- check_subtask_structure.py
- check_timezone_issue.py
- compare_data.py
- compare_with_ssrs.py
- debug_erp_subtasks.py
- debug_subtask_issue.py
- find_recovered_run.py
- generate_architecture_diagram.py
- test_databricks_connection.py
- test_databricks_ssrs_connection.py
- test_erp_complete.py
- test_erp_runs_fixed.py
- test_erp_status.py
- test_erp_with_status.py
- test_fix.py
- test_folders_display.py
- test_informatica_integration.py
- test_oracle.py
- test_pending_query.py
- test_updated_queries.py

### Temporary/Dev Scripts
- allow_port_8000.ps1
- create_adf_dsn.ps1
- pre_demo_check.ps1

### Temporary Files
- temp_api_response.json
- monitorportal.zip (old archive)
- YOUR_DATABRICKS_CONFIG.txt
- QUERY_UPDATES.txt

### Redundant Documentation (consolidate/remove)
- ADF_DSN_SETUP_GUIDE.md
- AI_IMPLEMENTATION_SUMMARY.md (keep AI_SYSTEM_README.md)
- AI_QUICK_START.md (keep AI_SYSTEM_README.md)
- API_IMPLEMENTATION.md (info in ARCHITECTURE.md)
- AZURE_DEV_TUNNELS_GUIDE.md
- DATABRICKS_SETUP_GUIDE.md
- DATABRICKS_SSRS_INTEGRATION_GUIDE.md
- DATA_SOURCE_GUIDE.md
- DEMO_CHECKLIST.txt
- DST_AUTOMATION_GUIDE.md
- ERP_RECOVERY_TRACKING_GUIDE.md
- FILES_CREATED_INVENTORY.md
- FIXES_APPLIED_MARCH_3.md
- IMPLEMENTATION_GUIDE.md (covered in README)
- INFORMATICA_CLOUD_API_GUIDE.md (keep shorter version)
- INFORMATICA_CLOUD_API_IMPLEMENTATION.md
- INFORMATICA_CLOUD_ARCHITECTURE_DIAGRAM.md
- INFORMATICA_CLOUD_SOLUTION_SUMMARY.md
- INFORMATICA_INTEGRATION_CHECKLIST.md
- INFORMATICA_QUICK_START.md (keep WORKFLOW_RESTART_GUIDE.md)
- INFORMATICA_SETTINGS_EXAMPLE.py
- INTERNAL_SHARING_GUIDE.md
- LVL3_FAILED_JOBS_OPTIMIZATION.md
- PASE_Monitor_Portal_4Page_PPT_Content.md
- PASE_Monitor_Portal_Executive_Proposal.html
- PASE_Monitor_Portal_Executive_Proposal.md
- PASSWORD_UPDATE_GUIDE.md
- PERFORMANCE_IMPROVEMENTS.md
- PERFORMANCE_OPTIMIZATION_GUIDE.md
- PERFORMANCE_QUICK_REFERENCE.md
- PERFORMANCE_TEST_CHECKLIST.md
- PRESENTATION_CHEAT_SHEET.md
- PRESENTATION_QA_GUIDE.md
- PROJECT_DOCUMENTATION.md (keep PROJECT_SUMMARY.md)
- PROJECT_DOCUMENTATION_WORD_FORMAT.md
- QUICK_START.txt (keep QUICK_START.md)
- SETUP_DSN_STEP_BY_STEP.md
- SHARING_INSTRUCTIONS.md
- Technical_Documentation_PASE_Monitor_Portal.html
- TEMPORARY_ACCESS_GUIDE.md

## Files to KEEP (Essential)

### Core Application
- monitorportal/ (entire Django project)
- requirements.txt
- .git/, .gitignore, .gitattributes
- .vscode/ (editor settings)

### Key Documentation
- README.md (main documentation)
- PROJECT_SUMMARY.md (overview)
- ARCHITECTURE.md (system design)
- DEPLOYMENT.md (deployment guide)
- QUICK_START.md (getting started)
- CHANGELOG.md (version history)
- WORKFLOW_RESTART_GUIDE.md (restart feature)
- INFORMATICA_SETTINGS_EXAMPLE.sh (config reference)
- AI_SYSTEM_README.md (AI features)
- PASE_Monitor_Portal_Architecture.jpg (diagram)

## Recommended Action

Would you like me to:
1. Delete all the temporary/test files listed above?
2. Create a consolidated documentation folder (docs/) and move essential docs there?
3. Update README.md with links to key documentation?
