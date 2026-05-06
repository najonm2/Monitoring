"""
Test script to verify local Informatica configuration
This will test the connection from your local Windows installation to the production repository
"""

import subprocess
import sys
import os

# Add the Django project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')

import django
django.setup()

from django.conf import settings
from portal.services.informatica_restart_service import InformaticaRestartService

def print_header(msg):
    print("\n" + "="*80)
    print(f"  {msg}")
    print("="*80)

def test_pmcmd_available():
    """Test if pmcmd is accessible"""
    print_header("Test 1: Check pmcmd Accessibility")
    
    pmcmd_path = settings.INFORMATICA_PMCMD_PATH
    print(f"pmcmd path: {pmcmd_path}")
    
    if not os.path.exists(pmcmd_path):
        print(f"❌ ERROR: pmcmd not found at {pmcmd_path}")
        return False
    
    print(f"✅ pmcmd.exe found at {pmcmd_path}")
    
    # Try to get version
    try:
        result = subprocess.run(
            [pmcmd_path, 'version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"Version output:\n{result.stdout}")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  WARNING: pmcmd version command timed out (this may be normal)")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_configuration():
    """Test Informatica configuration"""
    print_header("Test 2: Check Configuration")
    
    print(f"Domain: {settings.INFORMATICA_DOMAIN}")
    print(f"Repository: {settings.INFORMATICA_REPOSITORY}")
    print(f"Integration Service: {settings.INFORMATICA_INTEGRATION_SERVICE}")
    print(f"Username: {settings.INFORMATICA_USERNAME}")
    print(f"User Security Domain: {settings.INFORMATICA_USER_SECURITY_DOMAIN}")
    print(f"Default Folder: {settings.INFORMATICA_DEFAULT_FOLDER}")
    
    service = InformaticaRestartService()
    if service.is_configured():
        print("✅ All required configuration is present")
        return True
    else:
        print("❌ Configuration is incomplete")
        return False

def test_connection():
    """Test connection to Informatica repository"""
    print_header("Test 3: Test Repository Connection")
    
    pmcmd_path = settings.INFORMATICA_PMCMD_PATH
    
    cmd = [
        pmcmd_path,
        'connect',
        '-r', settings.INFORMATICA_REPOSITORY,
        '-d', settings.INFORMATICA_DOMAIN,
        '-u', settings.INFORMATICA_USERNAME,
        '-p', settings.INFORMATICA_PASSWORD
    ]
    
    # Add user security domain if configured
    if settings.INFORMATICA_USER_SECURITY_DOMAIN:
        cmd.extend(['-s', settings.INFORMATICA_USER_SECURITY_DOMAIN])
    
    print("Attempting to connect to repository...")
    print(f"Repository: {settings.INFORMATICA_REPOSITORY}")
    print(f"Domain: {settings.INFORMATICA_DOMAIN}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Successfully connected to Informatica repository!")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Connection failed")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("Informatica Local Installation Test")
    print("Testing connection from Windows client to production repository")
    
    results = []
    
    # Test 1: pmcmd accessibility
    results.append(("pmcmd Accessibility", test_pmcmd_available()))
    
    # Test 2: Configuration
    results.append(("Configuration", test_configuration()))
    
    # Test 3: Connection (only if previous tests passed)
    if all(r[1] for r in results):
        results.append(("Repository Connection", test_connection()))
    else:
        print("\n⚠️  Skipping connection test due to previous failures")
    
    # Summary
    print_header("Test Summary")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n🎉 All tests passed! Your local Informatica setup is ready.")
        print("\nYou can now:")
        print("1. Run the Django server: python monitorportal/manage.py runserver")
        print("2. Navigate to the failed jobs page")
        print("3. Click restart buttons to restart workflows")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
