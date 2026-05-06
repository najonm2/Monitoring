# Informatica Configuration Example
# Save this as a reference for your environment

# =============================================================================
# EXAMPLE CONFIGURATION FOR LINUX SERVER
# =============================================================================

# Path to pmcmd (check with: which pmcmd or find /opt /prd1 -name pmcmd)
INFORMATICA_PMCMD_PATH=/prd1/app/informatica/infa_shared/server/bin/pmcmd

# Domain name (check in Informatica Administrator Console)
INFORMATICA_DOMAIN=Domain_PROD

# Repository name (check in PowerCenter Repository Manager)
INFORMATICA_REPOSITORY=PC_REPO_PROD

# Integration Service name (check in Administrator Console)
INFORMATICA_INTEGRATION_SERVICE=IDG01P

# PowerCenter credentials
INFORMATICA_USERNAME=your_infa_username
INFORMATICA_PASSWORD=your_infa_password

# Default folder for workflows (usually matches subject_area from database)
INFORMATICA_DEFAULT_FOLDER=Production

# =============================================================================
# HOW TO SET THESE ON LINUX SERVER
# =============================================================================

# Option 1: Add to ~/.bashrc (for current user)
echo 'export INFORMATICA_PMCMD_PATH="/prd1/app/informatica/infa_shared/server/bin/pmcmd"' >> ~/.bashrc
echo 'export INFORMATICA_DOMAIN="Domain_PROD"' >> ~/.bashrc
echo 'export INFORMATICA_REPOSITORY="PC_REPO_PROD"' >> ~/.bashrc
echo 'export INFORMATICA_INTEGRATION_SERVICE="IDG01P"' >> ~/.bashrc
echo 'export INFORMATICA_USERNAME="your_username"' >> ~/.bashrc
echo 'export INFORMATICA_PASSWORD="your_password"' >> ~/.bashrc
echo 'export INFORMATICA_DEFAULT_FOLDER="Production"' >> ~/.bashrc
source ~/.bashrc

# Option 2: Add to /etc/environment (system-wide)
sudo nano /etc/environment
# Add the export statements above

# Option 3: Create a separate config file
sudo nano /etc/informatica/portal.conf
# Add export statements, then source it:
source /etc/informatica/portal.conf

# =============================================================================
# VERIFY CONFIGURATION
# =============================================================================

# 1. Check pmcmd is accessible
/prd1/app/informatica/infa_shared/server/bin/pmcmd -version

# 2. Test connection
pmcmd connect -r PC_REPO_PROD -d Domain_PROD -u your_username -p your_password

# 3. List workflows in a folder (to verify)
pmcmd listobjects -o workflow -f Production

# =============================================================================
# COMMON FOLDER NAMES (subject_area from Oracle)
# =============================================================================

# These are typically used as folder names in Informatica:
# - Finance
# - Sales
# - HR
# - Supply Chain
# - Customer
# - Production
# - Default

# To find your folder names, check the Oracle database:
# SELECT DISTINCT SUBJECT_AREA FROM INFA_PCREPO.REP_TASK_INST_RUN;

# =============================================================================
# START DJANGO SERVER WITH CONFIGURATION
# =============================================================================

# After setting environment variables:
cd /path/to/infa_monitor_portal/monitorportal
python manage.py runserver 0.0.0.0:8000

# =============================================================================
# QUICK TEST
# =============================================================================

# Test from Django shell:
python manage.py shell

# Run these commands:
"""
from portal.services.informatica_restart_service import InformaticaRestartService
service = InformaticaRestartService()
print("Configured:", service.is_configured())
"""
