"""
Test script to debug Informatica Recover Workflow issues
Run this to see detailed pmcmd command output
"""
import sys
import os
import subprocess

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from django.conf import settings

def test_recover_workflow():
    """
    Test the Recover Workflow option with a sample workflow
    """
    print("=" * 80)
    print("TESTING INFORMATICA RECOVER WORKFLOW")
    print("=" * 80)
    
    # Get settings
    pmcmd_path = settings.INFORMATICA_PMCMD_PATH
    domain = settings.INFORMATICA_DOMAIN
    username = settings.INFORMATICA_USERNAME
    password = settings.INFORMATICA_PASSWORD
    repository = settings.INFORMATICA_REPOSITORY_SERVICE
    integration_service = settings.INFORMATICA_INTEGRATION_SERVICE
    
    print(f"\n📋 Configuration:")
    print(f"  pmcmd path: {pmcmd_path}")
    print(f"  Domain: {domain}")
    print(f"  Repository: {repository}")
    print(f"  Integration Service: {integration_service}")
    print(f"  Username: {username}")
    
    # Check if pmcmd exists
    if not os.path.exists(pmcmd_path):
        print(f"\n❌ ERROR: pmcmd not found at: {pmcmd_path}")
        return
    
    print(f"\n✅ pmcmd found")
    
    # Get test workflow details from user
    print("\n" + "=" * 80)
    print("Enter the workflow details you want to test:")
    print("=" * 80)
    
    workflow_name = input("Workflow Name (e.g., wkf_Load_CDW_ASL_ICG_GRANITE): ").strip()
    folder_name = input("Folder Name (e.g., B_CDW_ASL_ICG_GRANITE): ").strip()
    
    if not workflow_name or not folder_name:
        print("❌ Workflow name and folder name are required!")
        return
    
    # Build command for Option 4: Recover Workflow
    cmd = [
        pmcmd_path,
        'startworkflow',
        '-sv', integration_service,
        '-d', domain,
        '-u', username,
        '-p', password,
        '-f', folder_name,
        '-recovery',
        workflow_name
    ]
    
    # Display command (hide password)
    cmd_display = cmd.copy()
    pwd_index = cmd_display.index('-p') + 1
    cmd_display[pwd_index] = '****'
    
    print(f"\n📝 Command to execute:")
    print(f"  {' '.join(cmd_display)}")
    
    # Confirm execution
    confirm = input("\n⚠️  Execute this command? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        return
    
    print("\n🚀 Executing pmcmd...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"\n📊 RESULTS:")
        print("=" * 80)
        print(f"Return Code: {result.returncode}")
        print(f"\n📤 STDOUT:\n{result.stdout}")
        print(f"\n📤 STDERR:\n{result.stderr}")
        print("=" * 80)
        
        if result.returncode == 0:
            print("\n✅ SUCCESS! Workflow recovery command executed successfully.")
        else:
            print("\n❌ FAILED! The command returned an error.")
            print("\nCommon reasons for failure:")
            print("  • Workflow is not in a recoverable state")
            print("  • Workflow doesn't exist or is not running/suspended")
            print("  • Recovery mode requires the workflow to have savepoints")
            print("  • Incorrect folder name or workflow name")
            print("  • Permission issues")
            print("  • Integration Service not running")
            
    except subprocess.TimeoutExpired:
        print("\n❌ TIMEOUT! Command took longer than 5 minutes.")
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_recover_workflow()
