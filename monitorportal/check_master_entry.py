"""
Check for master workflow entry (where SUBTASK_ASSET_NAME might be NULL or equal to ASSET_NAME)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd

# Get latest TASKFLOW_RUN_ID
latest_id = "1214588239747346432"

print(f"Checking for master workflow entry in TASKFLOW_RUN_ID {latest_id}...")

# Check for rows where SUBTASK_ASSET_NAME is NULL
query1 = f"""
SELECT 
    ASSET_NAME,
    SUBTASK_ASSET_NAME,
    LOCATION,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = '{latest_id}'
AND SUBTASK_ASSET_NAME IS NULL
"""

result1 = fetch_all_mapdqprd(query1)
print(f"\nRows with SUBTASK_ASSET_NAME IS NULL: {len(result1)}")
for row in result1:
    print(f"  {row}")

# Check for rows where SUBTASK_ASSET_NAME = ASSET_NAME
query2 = f"""
SELECT 
    ASSET_NAME,
    SUBTASK_ASSET_NAME,
    LOCATION,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = '{latest_id}'
AND SUBTASK_ASSET_NAME = ASSET_NAME
"""

result2 = fetch_all_mapdqprd(query2)
print(f"\nRows with SUBTASK_ASSET_NAME = ASSET_NAME: {len(result2)}")
for row in result2:
    print(f"  {row}")

# Get ALL rows including other locations
query3 = f"""
SELECT 
    ASSET_NAME,
    SUBTASK_ASSET_NAME,
    LOCATION,
    STATUS
FROM MAPDQPRD.IICS_CDI_RUN_INFO
WHERE TASKFLOW_RUN_ID = '{latest_id}'
AND ASSET_NAME NOT LIKE '%TAX%'
ORDER BY LOCATION, ASSET_NAME, SUBTASK_ASSET_NAME
"""

result3 = fetch_all_mapdqprd(query3)
print(f"\nALL rows for this TASKFLOW_RUN_ID (excluding TAX): {len(result3)}")
print("\nGrouped by location:")
locations = {}
for row in result3:
    loc = row['location']
    if loc not in locations:
        locations[loc] = []
    locations[loc].append(row)

for loc, rows in sorted(locations.items()):
    print(f"\n{loc}: {len(rows)} rows")
    for i, row in enumerate(rows, 1):
        asset = row['asset_name'][:35]
        subtask = str(row.get('subtask_asset_name', 'NULL'))[:35]
        status = row['status']
        print(f"  {i}. {asset.ljust(35)} | {subtask.ljust(35)} | {status}")
