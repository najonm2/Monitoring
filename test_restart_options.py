"""
Test Script for Informatica Restart Options

This script tests all 4 restart options available in the InformaticaRestartService:
    Option 1: Restart Task Only
    Option 2: Restart Workflow from Task
    Option 3: Restart Entire Workflow
    Option 4: Recover Workflow from Task

Usage:
    python test_restart_options.py

Prerequisites:
    - Django environment properly configured
    - Valid Informatica credentials in settings
    - Access to Informatica PowerCenter
"""

import sys
import os
from datetime import datetime

# Add the Django project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from django.conf import settings
from portal.services.informatica_restart_service import InformaticaRestartService

# ============================================================================
# CONFIGURATION - Update these values for your environment
# ============================================================================

# Test Workflow Details (use a real workflow from your environment)
TEST_WORKFLOW = 'YOUR_WORKFLOW_NAME'  # Replace with actual workflow name
TEST_FOLDER = 'YOUR_FOLDER_NAME'      # Replace with actual folder name
TEST_SESSION = 'YOUR_SESSION_NAME'    # Replace with actual session/task name
TEST_INTEGRATION_SERVICE = None       # Optional: Override default integration service

# Which tests to run (set to False to skip)
RUN_OPTION_1 = True  # Restart Task Only
RUN_OPTION_2 = True  # Restart Workflow from Task
RUN_OPTION_3 = True  # Restart Entire Workflow
RUN_OPTION_4 = True  # Recover Workflow from Task

# Dry run mode - if True, will show commands but not execute
DRY_RUN = True  # Set to False to actually execute commands

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80)


def print_success(message):
    """Print success message"""
    print(f"✓ SUCCESS: {message}")


def print_error(message):
    """Print error message"""
    print(f"✗ ERROR: {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ INFO: {message}")


def print_warning(message):
    """Print warning message"""
    print(f"⚠ WARNING: {message}")


def print_result(result):
    """Print the result dictionary in a formatted way"""
    print("\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def verify_configuration():
    """Verify that the test configuration is set up"""
    print_header("Verifying Configuration")
    
    # Check Django settings
    print_info("Checking Django Settings:")
    print(f"  Domain: {settings.INFORMATICA_DOMAIN}")
    print(f"  Repository: {settings.INFORMATICA_REPOSITORY}")
    print(f"  Integration Service: {settings.INFORMATICA_INTEGRATION_SERVICE}")
    print(f"  Username: {settings.INFORMATICA_USERNAME}")
    print(f"  Password: {'*' * len(settings.INFORMATICA_PASSWORD) if settings.INFORMATICA_PASSWORD else 'NOT SET'}")
    print(f"  User Security Domain: {settings.INFORMATICA_USER_SECURITY_DOMAIN}")
    
    # Check test configuration
    print_info("\nTest Configuration:")
    print(f"  Workflow: {TEST_WORKFLOW}")
    print(f"  Folder: {TEST_FOLDER}")
    print(f"  Session/Task: {TEST_SESSION}")
    print(f"  Integration Service Override: {TEST_INTEGRATION_SERVICE or 'None (using default)'}")
    
    # Check if service is properly configured
    service = InformaticaRestartService()
    if not service.is_configured():
        print_error("Informatica service is not fully configured")
        print_info("Check your Django settings for missing configuration")
        return False
    
    # Check if test values are set
    if TEST_WORKFLOW == 'YOUR_WORKFLOW_NAME':
        print_warning("TEST_WORKFLOW is not configured - update the script configuration")
        return False
    
    if TEST_FOLDER == 'YOUR_FOLDER_NAME':
        print_warning("TEST_FOLDER is not configured - update the script configuration")
        return False
    
    if TEST_SESSION == 'YOUR_SESSION_NAME' and (RUN_OPTION_1 or RUN_OPTION_2 or RUN_OPTION_4):
        print_warning("TEST_SESSION is not configured but required for options 1, 2, and 4")
        return False
    
    print_success("Configuration verified")
    
    if DRY_RUN:
        print_warning("DRY RUN MODE - Commands will be displayed but not executed")
        print_info("Set DRY_RUN = False to actually run the commands")
    
    return True


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_option_1_restart_task():
    """
    Test Option 1: Restart Task Only
    Restarts only the specified task/session without affecting other tasks
    """
    print_header("Test Option 1: Restart Task Only")
    
    print_info(f"This will restart ONLY the task: {TEST_SESSION}")
    print_info(f"Workflow: {TEST_WORKFLOW}")
    print_info(f"Folder: {TEST_FOLDER}")
    
    if DRY_RUN:
        print_warning("DRY RUN - Command would be executed here")
        print_info("Expected pmcmd command:")
        print(f"  pmcmd starttask -sv {settings.INFORMATICA_INTEGRATION_SERVICE} \\")
        print(f"    -d {settings.INFORMATICA_DOMAIN} -u {settings.INFORMATICA_USERNAME} \\")
        print(f"    -p **** -f {TEST_FOLDER} -w {TEST_WORKFLOW} {TEST_SESSION}")
        return {"success": True, "message": "DRY RUN - not executed"}
    
    service = InformaticaRestartService()
    result = service.restart_with_options(
        workflow_name=TEST_WORKFLOW,
        folder_name=TEST_FOLDER,
        restart_option=1,
        session_name=TEST_SESSION,
        integration_service=TEST_INTEGRATION_SERVICE
    )
    
    print_result(result)
    
    if result['success']:
        print_success("Option 1 test completed successfully")
    else:
        print_error(f"Option 1 test failed: {result.get('message', 'Unknown error')}")
    
    return result


def test_option_2_restart_from_task():
    """
    Test Option 2: Restart Workflow from Task
    Restarts the workflow starting from the specified task
    """
    print_header("Test Option 2: Restart Workflow from Task")
    
    print_info(f"This will restart the workflow FROM task: {TEST_SESSION}")
    print_info(f"Workflow: {TEST_WORKFLOW}")
    print_info(f"Folder: {TEST_FOLDER}")
    print_info("All tasks from this point forward will be executed")
    
    if DRY_RUN:
        print_warning("DRY RUN - Command would be executed here")
        print_info("Expected pmcmd command:")
        print(f"  pmcmd startworkflow -sv {settings.INFORMATICA_INTEGRATION_SERVICE} \\")
        print(f"    -d {settings.INFORMATICA_DOMAIN} -u {settings.INFORMATICA_USERNAME} \\")
        print(f"    -p **** -f {TEST_FOLDER} -startfrom {TEST_SESSION} {TEST_WORKFLOW}")
        return {"success": True, "message": "DRY RUN - not executed"}
    
    service = InformaticaRestartService()
    result = service.restart_with_options(
        workflow_name=TEST_WORKFLOW,
        folder_name=TEST_FOLDER,
        restart_option=2,
        session_name=TEST_SESSION,
        integration_service=TEST_INTEGRATION_SERVICE
    )
    
    print_result(result)
    
    if result['success']:
        print_success("Option 2 test completed successfully")
    else:
        print_error(f"Option 2 test failed: {result.get('message', 'Unknown error')}")
    
    return result


def test_option_3_restart_workflow():
    """
    Test Option 3: Restart Entire Workflow
    Restarts the entire workflow from the beginning
    """
    print_header("Test Option 3: Restart Entire Workflow")
    
    print_info(f"This will restart the ENTIRE workflow: {TEST_WORKFLOW}")
    print_info(f"Folder: {TEST_FOLDER}")
    print_info("All tasks in the workflow will be executed from the beginning")
    
    if DRY_RUN:
        print_warning("DRY RUN - Command would be executed here")
        print_info("Expected pmcmd command:")
        print(f"  pmcmd startworkflow -sv {settings.INFORMATICA_INTEGRATION_SERVICE} \\")
        print(f"    -d {settings.INFORMATICA_DOMAIN} -u {settings.INFORMATICA_USERNAME} \\")
        print(f"    -p **** -f {TEST_FOLDER} {TEST_WORKFLOW}")
        return {"success": True, "message": "DRY RUN - not executed"}
    
    service = InformaticaRestartService()
    result = service.restart_with_options(
        workflow_name=TEST_WORKFLOW,
        folder_name=TEST_FOLDER,
        restart_option=3,
        integration_service=TEST_INTEGRATION_SERVICE
    )
    
    print_result(result)
    
    if result['success']:
        print_success("Option 3 test completed successfully")
    else:
        print_error(f"Option 3 test failed: {result.get('message', 'Unknown error')}")
    
    return result


def test_option_4_recover_workflow():
    """
    Test Option 4: Recover Workflow from Task
    Recovers the workflow from the specified task using recovery mode
    """
    print_header("Test Option 4: Recover Workflow from Task")
    
    print_info(f"This will RECOVER the workflow FROM task: {TEST_SESSION}")
    print_info(f"Workflow: {TEST_WORKFLOW}")
    print_info(f"Folder: {TEST_FOLDER}")
    print_info("Recovery mode will be used to resume from failure point")
    
    if DRY_RUN:
        print_warning("DRY RUN - Command would be executed here")
        print_info("Expected pmcmd command:")
        print(f"  pmcmd startworkflow -sv {settings.INFORMATICA_INTEGRATION_SERVICE} \\")
        print(f"    -d {settings.INFORMATICA_DOMAIN} -u {settings.INFORMATICA_USERNAME} \\")
        print(f"    -p **** -f {TEST_FOLDER} -startfrom {TEST_SESSION} \\")
        print(f"    -recovery {TEST_WORKFLOW}")
        return {"success": True, "message": "DRY RUN - not executed"}
    
    service = InformaticaRestartService()
    result = service.restart_with_options(
        workflow_name=TEST_WORKFLOW,
        folder_name=TEST_FOLDER,
        restart_option=4,
        session_name=TEST_SESSION,
        integration_service=TEST_INTEGRATION_SERVICE
    )
    
    print_result(result)
    
    if result['success']:
        print_success("Option 4 test completed successfully")
    else:
        print_error(f"Option 4 test failed: {result.get('message', 'Unknown error')}")
    
    return result


def test_invalid_option():
    """Test that invalid options are properly rejected"""
    print_header("Test Invalid Option Handling")
    
    print_info("Testing with invalid option number (5)")
    
    service = InformaticaRestartService()
    result = service.restart_with_options(
        workflow_name=TEST_WORKFLOW,
        folder_name=TEST_FOLDER,
        restart_option=5  # Invalid option
    )
    
    print_result(result)
    
    if not result['success'] and 'Invalid restart option' in result.get('message', ''):
        print_success("Invalid option properly rejected")
    else:
        print_error("Invalid option was not properly handled")
    
    return result


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all enabled tests"""
    print_header("Informatica Restart Options Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify configuration first
    if not verify_configuration():
        print_error("Configuration verification failed - aborting tests")
        return 1
    
    results = []
    
    # Run Option 1 test
    if RUN_OPTION_1:
        result = test_option_1_restart_task()
        results.append(("Option 1", result))
        input("\nPress Enter to continue to next test...")
    
    # Run Option 2 test
    if RUN_OPTION_2:
        result = test_option_2_restart_from_task()
        results.append(("Option 2", result))
        input("\nPress Enter to continue to next test...")
    
    # Run Option 3 test
    if RUN_OPTION_3:
        result = test_option_3_restart_workflow()
        results.append(("Option 3", result))
        input("\nPress Enter to continue to next test...")
    
    # Run Option 4 test
    if RUN_OPTION_4:
        result = test_option_4_recover_workflow()
        results.append(("Option 4", result))
        input("\nPress Enter to continue to next test...")
    
    # Test invalid option handling
    result = test_invalid_option()
    results.append(("Invalid Option", result))
    
    # Print summary
    print_header("Test Summary")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    passed = sum(1 for _, r in results if r.get('success', False))
    total = len(results)
    
    print(f"\nTests run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✓ PASS" if result.get('success', False) else "✗ FAIL"
        message = result.get('message', 'No message')
        print(f"  {status} - {test_name}: {message}")
    
    if DRY_RUN:
        print_warning("\nThis was a DRY RUN - no actual commands were executed")
        print_info("Set DRY_RUN = False in the configuration to run actual tests")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
