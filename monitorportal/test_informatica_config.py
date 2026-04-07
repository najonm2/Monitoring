"""
Quick test script to verify Informatica connection
Run this to check if your credentials work before testing in the portal
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
import django
django.setup()

from portal.services.informatica_restart_service import InformaticaRestartService
from django.conf import settings

def test_configuration():
    """Test Informatica configuration"""
    print("="*70)
    print("INFORMATICA POWERCENTER CONFIGURATION TEST")
    print("="*70)
    
    service = InformaticaRestartService()
    
    print("\n📋 Configuration Details:")
    print(f"   Host: {settings.INFORMATICA_HOST}")
    print(f"   Port: {settings.INFORMATICA_PORT}")
    print(f"   Domain: {settings.INFORMATICA_DOMAIN}")
    print(f"   Repository: {settings.INFORMATICA_REPOSITORY}")
    print(f"   Integration Service: {settings.INFORMATICA_INTEGRATION_SERVICE}")
    print(f"   Username: {settings.INFORMATICA_USERNAME}")
    print(f"   Password: {'*' * len(settings.INFORMATICA_PASSWORD)}")
    print(f"   Default Folder: {settings.INFORMATICA_DEFAULT_FOLDER}")
    print(f"   pmcmd Path: {settings.INFORMATICA_PMCMD_PATH}")
    
    print("\n✅ Configuration Status:")
    if service.is_configured():
        print("   ✓ All required fields are configured")
    else:
        print("   ✗ Missing required configuration")
        return False
    
    print("\n" + "="*70)
    print("Configuration test completed!")
    print("="*70)
    
    print("\n📌 IMPORTANT NOTE:")
    print("   The Integration Service name is set to 'IDG01P' by default.")
    print("   If this is not correct for your environment, please update it in settings.py")
    print("   or provide the correct service name.")
    print("\n   To find your Integration Service name:")
    print("   1. Check Informatica Administrator Console")
    print("   2. Or run: pmcmd getservicedetails -d Domain_INFA_PRD1")
    
    print("\n🚀 Next Steps:")
    print("   1. Deploy code to Linux server (azeus2lipcp01)")
    print("   2. Ensure pmcmd is available on the server")
    print("   3. Test from the portal: http://localhost:8000/dashboards/level3/")
    print("   4. Click the '🔄 Restart' button on any failed workflow")
    
    return True

if __name__ == "__main__":
    try:
        test_configuration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
