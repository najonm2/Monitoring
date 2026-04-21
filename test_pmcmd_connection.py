"""
Quick test to verify pmcmd can connect to Informatica repository
"""

import sys
import os

# Add the Django project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from django.conf import settings
from portal.services.informatica_restart_service import InformaticaRestartService

def main():
    print("="*80)
    print("  Testing pmcmd Connection to Informatica Repository")
    print("="*80)
    
    # Show configuration
    print("\nConfiguration:")
    print(f"  pmcmd path: {settings.INFORMATICA_PMCMD_PATH}")
    print(f"  Domain: {settings.INFORMATICA_DOMAIN}")
    print(f"  Repository: {settings.INFORMATICA_REPOSITORY}")
    print(f"  Integration Service: {settings.INFORMATICA_INTEGRATION_SERVICE}")
    print(f"  Username: {settings.INFORMATICA_USERNAME}")
    print(f"  User Security Domain: {settings.INFORMATICA_USER_SECURITY_DOMAIN}")
    
    # Check if pmcmd exists
    print(f"\n✓ Checking if pmcmd exists...")
    if os.path.exists(settings.INFORMATICA_PMCMD_PATH):
        print(f"  ✓ pmcmd.exe found!")
    else:
        print(f"  ✗ pmcmd.exe NOT found!")
        return 1
    
    # Test with service
    print(f"\n✓ Testing InformaticaRestartService configuration...")
    service = InformaticaRestartService()
    
    if service.is_configured():
        print(f"  ✓ Service is properly configured!")
    else:
        print(f"  ✗ Service configuration is incomplete!")
        return 1
    
    # Try to get workflow status for a test (this will test connection)
    print(f"\n✓ Testing connection with getworkflowdetails command...")
    print(f"  (Using Default folder to test - you can change this)")
    
    # We'll use a dummy workflow name just to test if connection works
    # Even if workflow doesn't exist, we should get a connection-related error, not a path error
    test_result = service.get_workflow_status(
        workflow_name='TEST_CONNECTION',
        folder_name=settings.INFORMATICA_DEFAULT_FOLDER
    )
    
    print(f"\nConnection Test Result:")
    print(f"  Success: {test_result.get('success')}")
    print(f"  Message: {test_result.get('message', 'N/A')}")
    
    if 'error' in test_result:
        print(f"  Error: {test_result['error']}")
        
        # Check what type of error
        error_str = str(test_result['error']).lower()
        if 'not found' in error_str or 'does not exist' in error_str:
            print(f"\n✓ CONNECTION SUCCESSFUL!")
            print(f"  (The workflow doesn't exist, but connection to repository worked!)")
            return 0
        elif 'connect' in error_str or 'authenticate' in error_str:
            print(f"\n✗ CONNECTION FAILED!")
            print(f"  Check your credentials and domain/repository settings.")
            return 1
        elif 'pmcmd' in error_str:
            print(f"\n✗ PMCMD ERROR!")
            print(f"  There's an issue with the pmcmd executable.")
            return 1
    else:
        if test_result.get('success'):
            print(f"\n✓ CONNECTION SUCCESSFUL!")
            return 0
    
    print(f"\n⚠ Test completed with warnings - check output above")
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
