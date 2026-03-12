"""
Sample Django Settings for Informatica Cloud API Integration

Add these settings to your main Django settings.py file
"""

# ============================================================================
# INFORMATICA CLOUD API CONFIGURATION
# ============================================================================

# Base URL for Informatica Cloud
# For US region: usw3.dm1-us.informaticacloud.com
# For other regions, consult your Informatica installation
INFORMATICA_CLOUD_URL = 'https://usw3.dm1-us.informaticacloud.com/active-bpel/services'

# API Authentication Credentials
# Username is typically your email address used in Informatica Cloud
INFORMATICA_CLOUD_USER = 'your_informatica_username@company.com'

# Password: Use API token, NOT your login password
# To generate API token:
# 1. Login to Informatica Cloud Console
# 2. Go to Administrator > Users
# 3. Select your user > Authentication
# 4. Click "Generate API Token"
# 5. Copy the token as password
INFORMATICA_CLOUD_PASSWORD = 'your_api_authentication_token'

# Optional: Sync interval in seconds (for reference/logging)
# How often you plan to sync data (6 hours = 21600 seconds)
INFORMATICA_SYNC_INTERVAL = 21600

# Optional: Request timeout (seconds)
INFORMATICA_REQUEST_TIMEOUT = 30


# ============================================================================
# OPTIONAL: CELERY BEAT CONFIGURATION (For automatic syncing)
# ============================================================================

# If using Celery for periodic tasks, add this to CELERY_BEAT_SCHEDULE:
#
# CELERY_BEAT_SCHEDULE = {
#     ...existing tasks...
#     'sync-informatica-erp-tasks': {
#         'task': 'portal.tasks.sync_informatica_erp_tasks',
#         'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
#     },
# }


# ============================================================================
# OPTIONAL: LOGGING CONFIGURATION
# ============================================================================

# Add this to your LOGGING section to see sync details:
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'informatica_file': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': 'logs/informatica_sync.log',
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 3,
#         },
#     },
#     'loggers': {
#         'portal.services.informatica_cloud_service': {
#             'handlers': ['informatica_file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     },
# }
