import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd
import json

# Get sample ERP data
query = """
SELECT 
    ASSET_NAME, 
    TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') as start_time_raw,
    TO_CHAR(START_TIME, 'HH24') as hour_only,
    STATUS,
    LOCATION
FROM MAPDQPRD.IICS_CDI_RUN_INFO 
WHERE LOCATION IN (
    'CDW_DSL_ERP\\Workflows', 
    'CDW_DSL_ERP\\Sessions',
    'CDW_ASL_SAPS4\\Workflows',
    'ASL_ERP_DATAHUB\\Workflows'
)
AND START_TIME >= SYSDATE - 1
ORDER BY START_TIME DESC 
FETCH FIRST 15 ROWS ONLY
"""

result = fetch_all_mapdqprd(query)
print("ERP Data Sample (Last 15 jobs):")
print(json.dumps(result, indent=2, default=str))

# Check hour distribution
hours = {}
for row in result:
    hour = row.get('hour_only')
    hours[hour] = hours.get(hour, 0) + 1

print("\n\nHour Distribution:")
for hour in sorted(hours.keys()):
    print(f"  Hour {hour}: {hours[hour]} jobs")
