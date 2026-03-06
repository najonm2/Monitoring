"""
Get ALL rows for latest TASKFLOW_RUN_ID without ANY filters
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

latest_id = "1214588239747346432"

print(f"Getting ALL rows for TASKFLOW_RUN_ID {latest_id} (no filters)...")

query = f"""
SELECT 
    ASSET_NAME,
    SUBTASK_ASSET_NAME,
    LOCATION,
    STATUS,
    START_TIME,
    END_TIME
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = '{latest_id}'
ORDER BY LOCATION, ASSET_NAME, SUBTASK_ASSET_NAME
"""

result = fetch_all_mapdqprd(query)
print(f"\nTotal rows (no filters): {len(result)}")

# Group by location
locations = {}
for row in result:
    loc = row['location']
    if loc not in locations:
        locations[loc] = []
    locations[loc].append(row)

print(f"\nLocations found: {len(locations)}")
for loc, rows in sorted(locations.items()):
    print(f"\n{loc}: {len(rows)} rows")
    for i, row in enumerate(rows, 1):
        asset = row['asset_name'][:40]
        subtask = str(row.get('subtask_asset_name', 'NULL'))[:40]
        status = row['status'].ljust(10)
        print(f"  {i}. {asset.ljust(40)} | {subtask.ljust(40)} | {status}")

# Check if the 9th row is outside our location filters
our_locations = [
    'CDW_DSL_ERP\\Workflows',
    'CDW_DSL_ERP\\Sessions',
    'CDW_ASL_SAPS4\\Workflows',
    'ASL_ERP_DATAHUB\\Workflows'
]

print(f"\n{'='*80}")
print("FILTERING ANALYSIS:")
print(f"{'='*80}")

filtered_count = 0
tax_filtered = 0
location_filtered = 0

for row in result:
    loc = row['location']
    asset = row['asset_name']
    
    if loc in our_locations:
        if 'TAX' not in asset.upper():
            filtered_count += 1
        else:
            tax_filtered += 1
            print(f"\nTAX filtered: {asset} | {row.get('subtask_asset_name')}")
    else:
        location_filtered += 1
        print(f"\nLocation filtered: {loc} | {asset} | {row.get('subtask_asset_name')}")

print(f"\nSummary:")
print(f"  Total rows in database: {len(result)}")
print(f"  After location filter: {filtered_count + tax_filtered}")
print(f"  After TAX filter: {filtered_count}")
print(f"  Filtered out by location: {location_filtered}")
print(f"  Filtered out by TAX: {tax_filtered}")
print(f"\nIDMC expects: 9 tasks")
print(f"We show: {filtered_count} jobs")
print(f"Missing: {9 - filtered_count} jobs")
