# check_adf_table.py - Check ADF table existence
import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

def check_table(schema, table_name):
    """Check if table exists"""
    try:
        query = f"""
        SELECT COUNT(*) as cnt 
        FROM all_tables 
        WHERE owner = '{schema.upper()}' 
        AND table_name = '{table_name.upper()}'
        """
        result = fetch_all_mapdqprd(query)
        return result[0]['cnt'] if result else 0
    except Exception as e:
        print(f"Error checking {schema}.{table_name}: {e}")
        return 0

def search_tables_like(pattern):
    """Search for tables matching pattern"""
    try:
        query = f"""
        SELECT owner, table_name 
        FROM all_tables 
        WHERE table_name LIKE '%{pattern.upper()}%'
        AND owner IN ('MAPDQPRD', 'ASL', 'METADATA_FRAMEWORK')
        ORDER BY owner, table_name
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error searching tables: {e}")
        return []

def main():
    print("\n" + "="*80)
    print("🔍 SEARCHING FOR ADF INGESTION LOG TABLE")
    print("="*80)
    
    # Check various combinations
    print("\n1️⃣  Checking exact table names:")
    schemas_to_check = [
        ("MAPDQPRD", "INGESTION_LOG"),
        ("ASL", "INGESTION_LOG"),
        ("METADATA_FRAMEWORK", "INGESTION_LOG"),
    ]
    
    for schema, table in schemas_to_check:
        count = check_table(schema, table)
        if count > 0:
            print(f"   ✅ Found: {schema}.{table}")
        else:
            print(f"   ❌ Not found: {schema}.{table}")
    
    # Search for tables with 'INGESTION' in name
    print("\n2️⃣  Searching for tables containing 'INGESTION':")
    results = search_tables_like('INGESTION')
    if results:
        for row in results:
            print(f"   📋 {row['owner']}.{row['table_name']}")
    else:
        print("   ❌ No tables found")
    
    # Search for tables with 'LOG' in name
    print("\n3️⃣  Searching for tables containing 'LOG' in ASL/METADATA schemas:")
    results = search_tables_like('LOG')
    if results:
        for row in results[:10]:  # Limit to 10 results
            print(f"   📋 {row['owner']}.{row['table_name']}")
    else:
        print("   ❌ No tables found")
    
    # Try a simple count query on IICS_CDI_RUN_INFO to verify ADF data
    print("\n4️⃣  Checking IICS_CDI_RUN_INFO for ADF data:")
    try:
        query = """
        SELECT COUNT(*) as cnt
        FROM MAPDQPRD.IICS_CDI_RUN_INFO
        WHERE RESOURCE_TYPE = 'ADF'
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        """
        result = fetch_all_mapdqprd(query)
        count = result[0]['cnt'] if result else 0
        if count > 0:
            print(f"   ✅ Found {count} ADF records in IICS_CDI_RUN_INFO today")
            print("   💡 Suggestion: Use IICS_CDI_RUN_INFO with resource_type = 'ADF' filter")
        else:
            print(f"   ⚠️  No ADF records found in IICS_CDI_RUN_INFO today")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    main()
