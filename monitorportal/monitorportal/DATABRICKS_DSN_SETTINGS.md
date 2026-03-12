# Django Settings Configuration for Databricks ODBC DSN
# ═══════════════════════════════════════════════════════════════════

"""
SSRS Databricks Data Source Configuration
This mirrors your SSRS data source: ADF_DATASOURCE
Connection Type: ODBC
DSN: DataBricks_For_DBX_APP_64B_PRD
"""

# Add these settings to your Django settings.py

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABRICKS ODBC DSN CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Option 1: Using DSN (Recommended - Same as SSRS)
# ───────────────────────────────────────────────
DATABRICKS_DSN = 'DataBricks_For_DBX_APP_64B_PRD'  # Same DSN as SSRS

# Simple way to use it
DATABASES_DATABRICKS = {
    'dsn': 'DataBricks_For_DBX_APP_64B_PRD',
}

# Option 2: Connection details (if you prefer not to use DSN)
# ──────────────────────────────────────────────────────────
# DATABASES_DATABRICKS = {
#     'host': 'dbc-XXXXXXXX-XXXX.cloud.databricks.com',
#     'port': 443,
#     'http_path': '/sql/1.0/warehouses/xxxxxxxxxxxxx',
#     'username': 'token',
#     'password': 'dapi......',  # Personal Access Token
#     'database': 'default',
#     'driver': 'Simba Spark ODBC Driver',
# }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA SOURCE ALIASES (For easy reference)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA_SOURCES = {
    'ADF_DATASOURCE': {
        'type': 'ODBC',
        'dsn': 'DataBricks_For_DBX_APP_64B_PRD',
        'description': 'DBX Connection (same as SSRS)',
        'credentials': 'None',  # DSN handles auth
    },
    'MAPDQPRD': {
        'type': 'Oracle',
        'dsn': 'MAPDQPRD',
        'description': 'Oracle ERP Database',
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INTEGRATION WITH EXISTING CONNECTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Your existing Oracle connection (for ERP data)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # Oracle MAPDQPRD (existing)
    'mapdqprd': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'MAPDQPRD',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'your_host',
        'PORT': '1521',
    },
    # Databricks via ODBC (new)
    # Note: Django doesn't directly support ODBC in ORM
    # Use pyodbc directly instead (see service layer)
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLES OF USAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
In your code, use like this:

from django.conf import settings

# Get the DSN name
dsn = settings.DATABRICKS_DSN
# dsn = 'DataBricks_For_DBX_APP_64B_PRD'

# Use in pyodbc
import pyodbc
conn = pyodbc.connect(f'DSN={dsn}')
cursor = conn.cursor()
cursor.execute('SELECT * FROM my_table')
results = cursor.fetchall()
"""
