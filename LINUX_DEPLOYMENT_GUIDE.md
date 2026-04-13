# Linux Production Server Deployment Guide

This guide helps you deploy and test the Informatica Monitor Portal on your Linux production server.

---

## 📋 Prerequisites

- **Linux Server** with network access to:
  - Oracle Database (for BI data)
  - Informatica PowerCenter (for workflow restart)
  - SMTP relay (for email reports)
- **Python 3.8+** installed
- **Informatica pmcmd** accessible on the server

---

## 🚀 Quick Start - Test Before Deployment

### Step 1: Test Informatica Access

Before deploying the full application, test if Informatica restart functionality works on your server:

```bash
# Copy test script to your Linux server
scp test_informatica_restart.py user@your-linux-server:/tmp/

# SSH into your server
ssh user@your-linux-server

# Edit the configuration section in the test script
vi /tmp/test_informatica_restart.py

# Update these values:
# - PMCMD_PATH: Full path to pmcmd (e.g., /prd1/app/informatica/infa_shared/server/bin/pmcmd)
# - DOMAIN: Your Informatica domain
# - REPOSITORY: Your repository name
# - INTEGRATION_SERVICE: Your integration service name
# - USERNAME: Your Informatica username
# - PASSWORD: Your Informatica password
# - TEST_FOLDER: A real folder name (e.g., 'Production')
# - TEST_WORKFLOW: A real workflow name for testing

# Run the test
python3 /tmp/test_informatica_restart.py
```

**Expected Output:**
```
================================================================================
  INFORMATICA PMCMD RESTART FUNCTIONALITY TEST
================================================================================

✓ SUCCESS: pmcmd is accessible
✓ SUCCESS: Successfully connected to Informatica repository
✓ SUCCESS: Successfully retrieved workflows from folder
✓ SUCCESS: Core functionality is working!
```

### Step 2: Test Email Sending

Create a simple email test on the server:

```bash
# Create test_email.py
cat > /tmp/test_email.py << 'EOF'
import smtplib
from email.mime.text import MIMEText

smtp_host = "mailrelay.corp.intranet"
smtp_port = 25
from_email = "naresh.m@lumen.com"
to_email = "naresh.m@lumen.com"

msg = MIMEText("Test email from Linux server")
msg["Subject"] = "Test - Monitor Portal"
msg["From"] = from_email
msg["To"] = to_email

try:
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.sendmail(from_email, [to_email], msg.as_string())
    server.quit()
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Email failed: {e}")
EOF

# Run test
python3 /tmp/test_email.py
```

---

## 📦 Full Application Deployment

### Step 1: Transfer Project to Linux Server

```bash
# On your Windows machine, create a deployment package
cd c:\Users\ab64033\source\repos\infa_monitor_portal
tar -czf monitor_portal.tar.gz monitorportal/ requirements.txt docs/

# Copy to Linux server
scp monitor_portal.tar.gz user@your-linux-server:/opt/apps/

# On Linux server
ssh user@your-linux-server
cd /opt/apps/
tar -xzf monitor_portal.tar.gz
cd monitorportal
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Install additional packages for production
pip install gunicorn
```

### Step 3: Configure Environment Variables

```bash
# Create environment file
cat > /opt/apps/monitorportal/.env << 'EOF'
# Django Settings
SECRET_KEY='your-secret-key-here'
DEBUG=False
ALLOWED_HOSTS='your-server-hostname,localhost,127.0.0.1'

# Database - Oracle
ORACLE_HOST='racorap33-scan.corp.intranet'
ORACLE_PORT=1521
ORACLE_SERVICE_NAME='qgem01p_users'
ORACLE_USERNAME='rrsv2'
ORACLE_PASSWORD='rrsv2_202430'

# Email Settings
EMAIL_BACKEND_TYPE='smtp'
EMAIL_HOST='mailrelay.corp.intranet'
EMAIL_PORT=25
DEFAULT_FROM_EMAIL='naresh.m@lumen.com'
LEVEL3_EMAIL_RECIPIENTS='naresh.m@lumen.com,Prithviraj.Nayak@lumen.com'

# Informatica PowerCenter
INFORMATICA_PMCMD_PATH='/prd1/app/informatica/infa_shared/server/bin/pmcmd'
INFORMATICA_DOMAIN='Domain_PROD'
INFORMATICA_REPOSITORY='PC_REPO_PROD'
INFORMATICA_INTEGRATION_SERVICE='IDG01P'
INFORMATICA_USERNAME='your_infa_username'
INFORMATICA_PASSWORD='your_infa_password'
EOF

# Load environment variables
source /opt/apps/monitorportal/.env
export $(cat /opt/apps/monitorportal/.env | xargs)
```

### Step 4: Initialize Database

```bash
cd /opt/apps/monitorportal

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
```

### Step 5: Test Application

```bash
# Test email functionality
python manage.py send_level3_bi_email --test

# If successful, send actual report
python manage.py send_level3_bi_email
```

---

## ⏰ Set Up Automated Email Reports (Every 3 Hours)

### Option 1: Using Cron (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line to send emails every 3 hours at 0:00, 3:00, 6:00, etc.
0 */3 * * * cd /opt/apps/monitorportal && /opt/apps/monitorportal/venv/bin/python manage.py send_level3_bi_email >> /var/log/level3_email.log 2>&1

# Or for specific times (0:00, 3:00, 6:00, 9:00, 12:00, 15:00, 18:00, 21:00):
0 0,3,6,9,12,15,18,21 * * * cd /opt/apps/monitorportal && /opt/apps/monitorportal/venv/bin/python manage.py send_level3_bi_email >> /var/log/level3_email.log 2>&1
```

### Option 2: Using Systemd Timer

Create service file:
```bash
sudo vi /etc/systemd/system/level3-email.service
```

```ini
[Unit]
Description=Level3 BI Email Report
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/opt/apps/monitorportal
Environment="PATH=/opt/apps/monitorportal/venv/bin"
ExecStart=/opt/apps/monitorportal/venv/bin/python manage.py send_level3_bi_email
```

Create timer file:
```bash
sudo vi /etc/systemd/system/level3-email.timer
```

```ini
[Unit]
Description=Run Level3 BI Email every 3 hours

[Timer]
OnCalendar=*-*-* 0,3,6,9,12,15,18,21:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable level3-email.timer
sudo systemctl start level3-email.timer

# Check status
sudo systemctl status level3-email.timer
```

---

## 🌐 Run Web Server

### Development Mode (Testing)

```bash
cd /opt/apps/monitorportal
python manage.py runserver 0.0.0.0:8000
```

### Production Mode (Using Gunicorn)

```bash
# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 monitorportal.wsgi:application

# Or create a systemd service
sudo vi /etc/systemd/system/monitor-portal.service
```

```ini
[Unit]
Description=Monitor Portal Django Application
After=network.target

[Service]
Type=notify
User=your-username
Group=your-group
WorkingDirectory=/opt/apps/monitorportal
Environment="PATH=/opt/apps/monitorportal/venv/bin"
ExecStart=/opt/apps/monitorportal/venv/bin/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    monitorportal.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor-portal
sudo systemctl start monitor-portal
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] `python3 test_informatica_restart.py` passes all tests
- [ ] `python manage.py send_level3_bi_email --test` sends test email
- [ ] `python manage.py send_level3_bi_email` sends actual report
- [ ] Email received in inbox (check both recipients)
- [ ] Web portal accessible: http://your-server:8000
- [ ] Restart button works on failed jobs page
- [ ] Cron job or timer is active: `crontab -l` or `systemctl status level3-email.timer`

---

## 🔧 Troubleshooting

### Email Not Sending
```bash
# Check SMTP connectivity
telnet mailrelay.corp.intranet 25

# Check email logs
tail -f /var/log/level3_email.log

# Test basic SMTP
python3 /tmp/test_email.py
```

### Informatica Restart Not Working
```bash
# Run test script
python3 test_informatica_restart.py

# Check pmcmd manually
/prd1/app/informatica/infa_shared/server/bin/pmcmd version

# Test connection
/prd1/app/informatica/infa_shared/server/bin/pmcmd connect -r PC_REPO_PROD -d Domain_PROD -u username -p password
```

### Database Connection Issues
```bash
# Test Oracle connectivity
python -c "import oracledb; conn = oracledb.connect(user='rrsv2', password='rrsv2_202430', dsn='racorap33-scan.corp.intranet:1521/qgem01p_users'); print('Connected!'); conn.close()"
```

---

## 📞 Support

For issues or questions:
- Check logs: `/var/log/level3_email.log`
- Application logs: `monitorportal/portal/ai/logs/`
- Django logs: Run with `DEBUG=True` temporarily

---

## 🔐 Security Notes

- **Never commit .env file** with credentials to git
- Use environment variables for all sensitive data
- Restrict file permissions: `chmod 600 /opt/apps/monitorportal/.env`
- Use a strong SECRET_KEY for Django
- Keep DEBUG=False in production
