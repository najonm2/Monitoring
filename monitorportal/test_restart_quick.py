"""Quick test of Informatica restart service"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.informatica_restart_service import InformaticaRestartService

# Test the service
print("Testing Informatica Restart Service...")
print("-" * 50)

service = InformaticaRestartService()

print(f"Is configured: {service.is_configured()}")
print(f"pmcmd_path: {service.pmcmd_path}")
print(f"domain: {service.domain}")
print(f"repository: {service.repository}")
print(f"integration_service: {service.integration_service}")
print(f"username: {service.username}")
print(f"user_security_domain: {service.user_security_domain}")
print("-" * 50)

# Try a test restart
print("\nTesting restart_with_options...")
result = service.restart_with_options(
    workflow_name='test_workflow',
    folder_name='Default',
    restart_option=3,
    session_name=None
)

print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")
if 'error' in result:
    print(f"Error: {result.get('error')}")
if 'output' in result:
    print(f"Output: {result.get('output')}")
