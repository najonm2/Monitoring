"""
Quick test to find the correct column name for unique job identifier
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

print("\n🔍 Testing IICS_CDI_RUN_INFO table schema...")

query = """
SELECT COLUMN_NAME 
FROM ALL_TAB_COLUMNS 
WHERE TABLE_NAME = 'IICS_CDI_RUN_INFO' 
AND OWNER = 'MAPDQPRD'
ORDER BY COLUMN_ID
"""

try:
    columns = fetch_all_mapdqprd(query)
    print(f"\n✅ Found {len(columns)} columns:")
    for col in columns:
        print(f"   - {col.get('column_name', col.get('COLUMN_NAME', 'Unknown'))}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    
    # Try alternate approach - query actual data to see columns
    print("\n🔄 Trying to fetch sample record...")
    query2 = """
    SELECT *
    FROM MAPDQPRD.IICS_CDI_RUN_INFO
    WHERE ROWNUM = 1
    """
    try:
        sample = fetch_all_mapdqprd(query2)
        if sample and len(sample) > 0:
            print("\n✅ Sample record columns:")
            for key in sample[0].keys():
                print(f"   - {key}")
    except Exception as e2:
        print(f"❌ Error: {e2}")
