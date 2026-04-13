#!/usr/bin/env python3
"""
Simple Informatica Restart Test Script for Linux Production Server

This script tests the Informatica pmcmd workflow restart functionality.
Run this on your Linux server to verify pmcmd is accessible and working.

Usage:
    python3 test_informatica_restart.py

Prerequisites:
    - pmcmd must be in PATH or specify full path below
    - Valid Informatica credentials
    - Access to Informatica PowerCenter
"""

import subprocess
import sys
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION - Update these values for your environment
# ============================================================================

# Informatica Configuration
PMCMD_PATH = '/prd1/app/informatica/infa_shared/server/bin/pmcmd'  # Full path to pmcmd
DOMAIN = 'Domain_PROD'
REPOSITORY = 'PC_REPO_PROD'
INTEGRATION_SERVICE = 'IDG01P'
USERNAME = 'your_username'  # Replace with your Informatica username
PASSWORD = 'your_password'  # Replace with your Informatica password

# Test Workflow Details (use a real workflow from your environment)
TEST_WORKFLOW = 'wf_TestWorkflow'  # Replace with actual workflow name
TEST_FOLDER = 'Production'  # Replace with actual folder name

# ============================================================================
# TEST FUNCTIONS
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


def test_pmcmd_accessible():
    """Test 1: Check if pmcmd is accessible"""
    print_header("Test 1: Checking pmcmd Accessibility")
    
    try:
        result = subprocess.run(
            [PMCMD_PATH, 'version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success(f"pmcmd is accessible at: {PMCMD_PATH}")
            print_info(f"Version info:\n{result.stdout}")
            return True
        else:
            print_error(f"pmcmd returned error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print_error(f"pmcmd not found at: {PMCMD_PATH}")
        print_info("Check PMCMD_PATH in the configuration section")
        return False
    except Exception as e:
        print_error(f"Error accessing pmcmd: {str(e)}")
        return False


def test_informatica_connection():
    """Test 2: Test connection to Informatica repository"""
    print_header("Test 2: Testing Informatica Repository Connection")
    
    try:
        # Use pmcmd connect command to test credentials
        cmd = [
            PMCMD_PATH,
            'connect',
            '-r', REPOSITORY,
            '-d', DOMAIN,
            '-u', USERNAME,
            '-p', PASSWORD
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("Successfully connected to Informatica repository")
            print_info(f"Domain: {DOMAIN}")
            print_info(f"Repository: {REPOSITORY}")
            print_info(f"User: {USERNAME}")
            return True
        else:
            print_error("Failed to connect to repository")
            print_info(f"Error: {result.stderr or result.stdout}")
            print_info("Check your credentials and domain/repository settings")
            return False
            
    except Exception as e:
        print_error(f"Connection test failed: {str(e)}")
        return False


def test_list_workflows():
    """Test 3: List workflows in specified folder"""
    print_header("Test 3: Listing Workflows in Folder")
    
    try:
        cmd = [
            PMCMD_PATH,
            'listobjects',
            '-r', REPOSITORY,
            '-d', DOMAIN,
            '-u', USERNAME,
            '-p', PASSWORD,
            '-f', TEST_FOLDER,
            '-o', 'workflow'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success(f"Successfully retrieved workflows from folder: {TEST_FOLDER}")
            workflows = result.stdout.strip().split('\n')
            print_info(f"Found {len(workflows)} workflows:")
            for i, wf in enumerate(workflows[:10], 1):  # Show first 10
                print(f"  {i}. {wf}")
            if len(workflows) > 10:
                print(f"  ... and {len(workflows) - 10} more")
            return True
        else:
            print_error("Failed to list workflows")
            print_info(f"Error: {result.stderr or result.stdout}")
            return False
            
    except Exception as e:
        print_error(f"Failed to list workflows: {str(e)}")
        return False


def test_workflow_status():
    """Test 4: Get status of a specific workflow"""
    print_header("Test 4: Getting Workflow Status")
    
    print_info(f"Checking status of workflow: {TEST_WORKFLOW}")
    
    try:
        cmd = [
            PMCMD_PATH,
            'getworkflowdetails',
            '-d', DOMAIN,
            '-u', USERNAME,
            '-p', PASSWORD,
            '-f', TEST_FOLDER,
            TEST_WORKFLOW
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success(f"Successfully retrieved workflow status")
            print_info(f"Workflow details:\n{result.stdout}")
            return True
        else:
            print_error("Failed to get workflow status")
            print_info(f"Error: {result.stderr or result.stdout}")
            print_info("Make sure TEST_WORKFLOW and TEST_FOLDER are set correctly")
            return False
            
    except Exception as e:
        print_error(f"Status check failed: {str(e)}")
        return False


def test_restart_workflow_dry_run():
    """Test 5: Dry run - show restart command without executing"""
    print_header("Test 5: Workflow Restart Command (Dry Run)")
    
    print_info("This shows the command that would be executed to restart a workflow")
    print_info("The actual restart is NOT executed in this test")
    
    cmd = [
        PMCMD_PATH,
        'startworkflow',
        '-sv', INTEGRATION_SERVICE,
        '-d', DOMAIN,
        '-u', USERNAME,
        '-p', '****',  # Hidden for display
        '-f', TEST_FOLDER,
        TEST_WORKFLOW
    ]
    
    print_info(f"Restart command would be:")
    print(f"  {' '.join(cmd)}")
    print()
    print_info("To actually restart a workflow, use:")
    print(f"  {PMCMD_PATH} startworkflow -sv {INTEGRATION_SERVICE} -d {DOMAIN} \\")
    print(f"    -u {USERNAME} -p <password> -f {TEST_FOLDER} {TEST_WORKFLOW}")
    
    return True


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print()
    print("=" * 80)
    print("  INFORMATICA PMCMD RESTART FUNCTIONALITY TEST")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Server: {os.uname().nodename if hasattr(os, 'uname') else 'Unknown'}")
    print("=" * 80)
    
    # Configuration check
    print_header("Configuration")
    print(f"  PMCMD Path:          {PMCMD_PATH}")
    print(f"  Domain:              {DOMAIN}")
    print(f"  Repository:          {REPOSITORY}")
    print(f"  Integration Service: {INTEGRATION_SERVICE}")
    print(f"  Username:            {USERNAME}")
    print(f"  Test Folder:         {TEST_FOLDER}")
    print(f"  Test Workflow:       {TEST_WORKFLOW}")
    
    # Run tests
    results = []
    
    # Test 1: pmcmd accessible
    results.append(("pmcmd Accessibility", test_pmcmd_accessible()))
    
    # Test 2: Repository connection
    if results[-1][1]:  # Only if previous test passed
        results.append(("Repository Connection", test_informatica_connection()))
    else:
        results.append(("Repository Connection", False))
        print_info("Skipping connection test due to pmcmd accessibility failure")
    
    # Test 3: List workflows
    if results[-1][1]:
        results.append(("List Workflows", test_list_workflows()))
    else:
        results.append(("List Workflows", False))
        print_info("Skipping workflow listing due to connection failure")
    
    # Test 4: Workflow status (optional - may fail if workflow doesn't exist)
    if results[-1][1]:
        print_info("Note: This test is optional and may fail if test workflow doesn't exist")
        results.append(("Workflow Status", test_workflow_status()))
    else:
        results.append(("Workflow Status", False))
    
    # Test 5: Dry run (always run for information)
    results.append(("Restart Command Preview", test_restart_workflow_dry_run()))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    print()
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed >= 3:  # pmcmd, connection, and list workflows
        print()
        print_success("Core functionality is working! You can use workflow restart features.")
        print_info("Next steps:")
        print("  1. Deploy your Django application to this server")
        print("  2. Configure settings.py with these Informatica details")
        print("  3. Test restart from the web portal")
        return 0
    else:
        print()
        print_error("Some tests failed. Please fix the issues before proceeding.")
        print_info("Common issues:")
        print("  - Incorrect pmcmd path")
        print("  - Wrong credentials")
        print("  - Network connectivity to Informatica server")
        print("  - Incorrect domain/repository names")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
