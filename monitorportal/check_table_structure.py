# check_table_structure.py - Check IICS_CDI_RUN_INFO structure
import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

def check_table_columns():
    """Get column information for IICS_CDI_RUN_INFO"""
    try:
        query = """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'MAPDQPRD'
        AND table_name = 'IICS_CDI_RUN_INFO'
        ORDER BY column_id
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error: {e}")
        return []

def check_location_values():
    """Check unique LOCATION values to identify ADF"""
    try:
        query = """
        SELECT DISTINCT LOCATION
        FROM MAPDQPRD.IICS_CDI_RUN_INFO
        WHERE ROWNUM <= 50
        ORDER BY LOCATION
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error: {e}")
        return []

def sample_records():
    """Get sample records"""
    try:
        query = """
        SELECT *
        FROM MAPDQPRD.IICS_CDI_RUN_INFO
        WHERE ROWNUM <= 5
        ORDER BY START_TIME DESC
        """
        return fetch_all_mapdqprd(query)
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    print("\n" + "="*80)
    print("🔍 ANALYZING IICS_CDI_RUN_INFO TABLE STRUCTURE")
    print("="*80)
    
    # Check columns
    print("\n1️⃣  Table Columns:")
    columns = check_table_columns()
    if columns:
        for col in columns:
            print(f"   📋 {col['column_name']:<30} {col['data_type']}({col['data_length']})")
    else:
        print("   ❌ Could not retrieve columns")
    
    # Check locations
    print("\n2️⃣  Unique LOCATION values (sample):")
    locations = check_location_values()
    if locations:
        for loc in locations[:20]:
            print(f"   📍 {loc['location']}")
    else:
        print("   ❌ Could not retrieve locations")
    
    # Sample records
    print("\n3️⃣  Sample Records (first 2):")
    records = sample_records()
    if records:
        for i, rec in enumerate(records[:2], 1):
            print(f"\n   Record {i}:")
            for key, value in rec.items():
                print(f"      {key}: {value}")
    else:
        print("   ❌ Could not retrieve sample records")
    
    print("\n" + "="*80)
    print("💡 Based on the columns, we can identify ADF jobs by LOCATION pattern")
    print("="*80)

if __name__ == "__main__":
    main()
