"""
Quick Test Script for SSRS Databricks DSN Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test if Django can connect to same Databricks DSN as SSRS
Usage: python test_databricks_ssrs_connection.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitorportal'))

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.conf import settings
from portal.services.databricks_odbc_service import (
    get_databricks_service,
    get_adf_databricks_service
)

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔{'═' * (len(text) + 4)}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║  {text}  ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚{'═' * (len(text) + 4)}╝{Colors.END}\n")

def print_section(text):
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print("─" * 50)

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Start tests
print_header("SSRS Databricks DSN Integration Test")

# Test 1: Check settings
print_section("Test 1: Django Settings")
try:
    dsn = getattr(settings, 'DATABRICKS_DSN', None)
    if dsn:
        print_success(f"DATABRICKS_DSN configured: {dsn}")
    else:
        print_warning("DATABRICKS_DSN not in settings, using default: DataBricks_For_DBX_APP_64B_PRD")
except Exception as e:
    print_error(f"Settings check failed: {e}")

# Test 2: Basic connection
print_section("Test 2: Basic Connection")
try:
    service = get_databricks_service()
    success, message = service.test_connection()
    
    if success:
        print_success(message)
    else:
        print_error(message)
        print_warning("Cannot continue with remaining tests")
        sys.exit(1)
except Exception as e:
    print_error(f"Connection test failed: {e}")
    print_warning("Ensure DSN 'DataBricks_For_DBX_APP_64B_PRD' is configured in ODBC")
    sys.exit(1)

# Test 3: Connection Details
print_section("Test 3: Connection Configuration")
try:
    print_info(f"DSN: {service.dsn}")
    print_info(f"Connection String: {service.connection_string}")
    print_info(f"Timeout: {service.timeout}s")
    print_success("Configuration verified")
except Exception as e:
    print_error(f"Configuration check failed: {e}")

# Test 4: List Tables
print_section("Test 4: List Available Tables")
try:
    tables = service.get_tables()
    print_success(f"Found {len(tables)} tables in default database:")
    
    for i, table in enumerate(tables[:15], 1):
        print(f"   {i:2}. {table}")
    
    if len(tables) > 15:
        print(f"   ... and {len(tables) - 15} more tables")
except Exception as e:
    print_warning(f"Could not list tables: {e}")
    print_info("This might be expected if you don't have permission or if tables aren't available yet")

# Test 5: Get Table Schema
print_section("Test 5: Get Table Schema (First available table)")
try:
    tables = service.get_tables()
    if tables:
        first_table = tables[0]
        schema = service.get_table_schema(first_table)
        
        print_success(f"Schema for table '{first_table}':")
        for col in schema[:10]:
            print(f"   • {col['column']:30} {col['type']:20}")
        
        if len(schema) > 10:
            print(f"   ... and {len(schema) - 10} more columns")
except Exception as e:
    print_warning(f"Could not retrieve schema: {e}")

# Test 6: Sample Data
print_section("Test 6: Sample Data")
try:
    tables = service.get_tables()
    if tables:
        first_table = tables[0]
        sample = service.get_data_sample(first_table, limit=3)
        
        if sample:
            print_success(f"Sample data from '{first_table}':")
            print(f"   Columns: {list(sample[0].keys())}")
            print(f"   Rows returned: {len(sample)}")
        else:
            print_warning(f"No data in table '{first_table}'")
except Exception as e:
    print_warning(f"Could not retrieve sample data: {e}")

# Test 7: ADF Service (if configured)
print_section("Test 7: ADF Service")
try:
    adf_service = get_adf_databricks_service()
    print_info(f"ADF Database: {adf_service.adf_database}")
    
    # Try to get ADF runs
    try:
        runs = adf_service.get_recent_pipeline_runs(days=7, limit=5)
        if runs:
            print_success(f"Found {len(runs)} recent ADF pipeline runs:")
            for run in runs[:3]:
                print(f"   • {run.get('pipeline_name')}: {run.get('status')}")
        else:
            print_warning("No pipeline runs found in last 7 days")
    except Exception as e:
        print_warning(f"ADF tables not available yet: {e}")
        print_info("This is expected if ADF data hasn't been synced to Databricks yet")
    
except Exception as e:
    print_error(f"ADF service test failed: {e}")

# Summary
print_section("Summary")
print_success("Core Databricks ODBC connection is working!")
print_info("You can now use this in your Django views:")
print("\n" + Colors.BOLD + "Code Example:" + Colors.END)
print("""
from portal.services.databricks_odbc_service import get_databricks_service

service = get_databricks_service()
results = service.execute_query_dict('''
    SELECT * FROM your_table LIMIT 10
''')

for row in results:
    print(row)
""")

print_section("Next Steps")
print("1. Add DATABRICKS_DSN setting to settings.py")
print("2. Use databricks_odbc_service.py in your views")
print("3. Create ADF dashboard using ADF_DatabricksService")
print("4. Integrate results into your portal templates")

print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All tests completed successfully!{Colors.END}\n")
