# Python 3.6.8 Compatibility Guide

## ⚠️ SECURITY WARNING
**Python 3.6.8** (EOL: December 2021) and **Django 3.2 LTS** (Extended support ended: April 2024) are both **end-of-life** and no longer receive security updates.

**Production environments should upgrade to:**
- Python 3.10+ (or 3.11, 3.12)
- Django 4.2 LTS (supported until April 2026)

---

## Downgrade Steps for Python 3.6.8

If you **must** run on Python 3.6.8, follow these steps:

### 1. Recreate Virtual Environment
```bash
# On Linux server with Python 3.6.8
cd /path/to/infa_monitor_portal/monitorportal

# Remove old virtual environment
rm -rf .venv

# Create new virtual environment with Python 3.6.8
python3.6 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 2. Install Downgraded Dependencies
```bash
# Install Django 3.2 LTS and compatible packages
pip install --upgrade pip
pip install -r ../requirements.txt
```

### 3. Verify Installation
```bash
# Check Python version
python --version
# Should show: Python 3.6.8

# Check Django version
python -c "import django; print(django.get_version())"
# Should show: 3.2.x

# Check database driver
python -c "import cx_Oracle; print(cx_Oracle.version)"
# Should show cx_Oracle version
```

### 4. Run Migrations
```bash
# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Start Server
```bash
# Development server
python manage.py runserver

# Or for network access
python manage.py runserver 0.0.0.0:8000
```

---

## Key Changes Made

### Dependencies (requirements.txt)
- **Django**: 6.0.2 → 3.2.25 (LTS)
- **Database driver**: python-oracledb 2.x → cx_Oracle 8.x
- **Selenium**: 4.x → 3.141.0

### Code Changes (oracle_client.py)
- Added fallback import for cx_Oracle for Python 3.6 compatibility
- Both cx_Oracle and python-oracledb use similar APIs, so minimal changes needed

---

## Compatibility Matrix

| Python Version | Django Version | Database Driver | Status |
|---------------|----------------|----------------|---------|
| 3.6.8 | 3.2 LTS | cx_Oracle 8.x | ⚠️ EOL (Use only if required) |
| 3.10+ | 4.2 LTS | python-oracledb 2.x | ✅ Recommended |
| 3.10+ | 6.0.x | python-oracledb 2.x | ✅ Latest (currently in use on Windows) |

---

## Production Deployment Notes

### For Linux Server (Python 3.6.8)

1. **Install Oracle Instant Client** (required for cx_Oracle):
```bash
# Download Oracle Instant Client RPM
wget https://download.oracle.com/otn_software/linux/instantclient/...

# Install
sudo rpm -ivh oracle-instantclient-basic-*.rpm
sudo rpm -ivh oracle-instantclient-sqlplus-*.rpm

# Set environment variables
export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib:$LD_LIBRARY_PATH
```

2. **Deploy Application**:
```bash
# Copy project to server
scp -r infa_monitor_portal user@server:/path/to/

# SSH to server
ssh user@server

# Setup virtual environment (see step 1 above)
cd /path/to/infa_monitor_portal/monitorportal
python3.6 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt

# Configure environment variables
export DJANGO_SECRET_KEY="your-secret-key"
export EMAIL_BACKEND_TYPE="smtp"
# ... other environment variables
```

3. **Setup systemd service** (for production):
```ini
# /etc/systemd/system/monitorportal.service
[Unit]
Description=Monitoring Portal Django App
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/path/to/infa_monitor_portal/monitorportal
Environment="PATH=/path/to/infa_monitor_portal/monitorportal/.venv/bin"
Environment="LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib"
ExecStart=/path/to/infa_monitor_portal/monitorportal/.venv/bin/gunicorn monitorportal.wsgi:application --bind 0.0.0.0:8000 --workers 3

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start monitorportal
sudo systemctl enable monitorportal
sudo systemctl status monitorportal
```

---

## Testing Checklist

After downgrade, test these features:

- [ ] Server starts without errors
- [ ] Home page loads
- [ ] Level3 dashboards load
- [ ] Failed jobs page displays
- [ ] Restart workflow functionality works
- [ ] Manual restart page loads
- [ ] Database queries execute successfully
- [ ] Email generation works (if configured)

---

## Future Upgrade Path

When ready to upgrade Python on the production server:

1. **Upgrade Python**: Install Python 3.10 or higher
2. **Update requirements.txt** back to:
   ```
   Django>=4.2.0,<5.0.0  # LTS version
   python-oracledb>=2.0.0
   selenium>=4.0.0
   ```
3. **Recreate virtual environment** with new Python version
4. **Test thoroughly** before deploying to production

---

## Support

For issues or questions:
- Django 3.2 docs: https://docs.djangoproject.com/en/3.2/
- cx_Oracle docs: https://cx-oracle.readthedocs.io/
- Python 3.6 docs: https://docs.python.org/3.6/

**Remember**: This is a temporary workaround. Plan to upgrade Python ASAP for security and support.
