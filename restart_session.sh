#!/bin/bash
#
# Informatica Interactive Restart Script
# Provides 3 restart options for workflows/sessions
#

# Configuration
PMCMD="/prd1/usr/local/informatica/CDIPC/Informatica/platform/home/server/bin/pmcmd"
DOMAIN="Domain_INFA_PRD1"
INTEGRATION_SERVICE="IS_GRID_BI"
USERNAME="ab64033"
PASSWORD="Samsungs26@123"
USER_SECURITY_DOMAIN="CTL"   # User Security Domain for CTL/Lumen users

# Session details
FOLDER="B_CDW_ASL_ICG_GRANITE"
WORKFLOW="wkf_Load_CDW_ASL_ICG_GRANITE"
SESSION="s_m_Load_SITE_INST"

echo "========================================================================"
echo "  Informatica Restart Options"
echo "========================================================================"
echo "Domain:     $DOMAIN"
echo "Service:    $INTEGRATION_SERVICE"
echo "Folder:     $FOLDER"
echo "Workflow:   $WORKFLOW"
echo "Session:    $SESSION"
echo "User:       $USERNAME"
echo "========================================================================"
echo ""
echo "Select restart option:"
echo ""
echo "  1) Restart Task Only        - Restarts only session: $SESSION"
echo "  2) Restart Workflow from Task - Restarts workflow from task: $SESSION"
echo "  3) Restart Entire Workflow  - Restarts workflow from beginning"
echo "  4) Recover Workflow         - Recovers failed workflow run"
echo ""
echo -n "Enter choice [1-4]: "
read CHOICE

# Build optional -usd argument
USD_ARGS=""
if [ -n "$USER_SECURITY_DOMAIN" ]; then
  USD_ARGS="-usd $USER_SECURITY_DOMAIN"
fi

echo ""
echo "========================================================================"

case $CHOICE in
  1)
    echo "Option 1: Restarting Task Only..."
    echo "========================================================================"
    $PMCMD starttask \
      -sv "$INTEGRATION_SERVICE" \
      -d  "$DOMAIN" \
      -u  "$USERNAME" \
      $USD_ARGS \
      -p  "$PASSWORD" \
      -f  "$FOLDER" \
      -w  "$WORKFLOW" \
      "$SESSION"
    RC=$?
    ;;
    
  2)
    echo "Option 2: Restarting Workflow from Task: $SESSION..."
    echo "========================================================================"
    $PMCMD startworkflow \
      -sv "$INTEGRATION_SERVICE" \
      -d  "$DOMAIN" \
      -u  "$USERNAME" \
      $USD_ARGS \
      -p  "$PASSWORD" \
      -f  "$FOLDER" \
      -startfrom "$SESSION" \
      "$WORKFLOW"
    RC=$?
    ;;
    
  3)
    echo "Option 3: Restarting Entire Workflow..."
    echo "========================================================================"
    $PMCMD startworkflow \
      -sv "$INTEGRATION_SERVICE" \
      -d  "$DOMAIN" \
      -u  "$USERNAME" \
      $USD_ARGS \
      -p  "$PASSWORD" \
      -f  "$FOLDER" \
      "$WORKFLOW"
    RC=$?
    ;;
    
  4)
    echo "Option 4: Recovering Workflow from Task: $SESSION..."
    echo "========================================================================"
    $PMCMD startworkflow \
      -sv "$INTEGRATION_SERVICE" \
      -d  "$DOMAIN" \
      -u  "$USERNAME" \
      $USD_ARGS \
      -p  "$PASSWORD" \
      -f  "$FOLDER" \
      -startfrom "$SESSION" \
      -recovery \
      "$WORKFLOW"
    RC=$?
    ;;
    
  *)
    echo "Invalid choice. Please enter 1, 2, 3, or 4."
    exit 1
    ;;
esac

echo ""

if [ $RC -eq 0 ]; then
    echo "✓ SUCCESS: Restart completed successfully!"
    exit 0
else
    echo "✗ ERROR: Failed to restart (exit code: $RC)"
    exit $RC
fi
