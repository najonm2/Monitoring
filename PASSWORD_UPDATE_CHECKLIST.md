# Password Update Checklist for Rancher Deployment

**⚠️ CRITICAL: All passwords below must be updated before deploying to Rancher Server**

---

## 📋 Overview

This document lists ALL locations where passwords and credentials need to be updated when deploying to Rancher/Production environment.

**Security Best Practice**: 
- ❌ Never hardcode passwords in code files
- ✅ Use environment variables or Kubernetes secrets
- ✅ Remove all default/development passwords before deployment

---

## 🔐 1. Django Secret Key

### Location: `monitorportal/monitorportal/settings.py`

**Current (Line 24):**
```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me-in-prod")
```

**Action Required:**
- Set environment variable `DJANGO_SECRET_KEY` with a new random 50+ character key
- Generate new key using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- ❌ **NEVER use the default value in production!**

**Rancher Configuration:**
```yaml
env:
  - name: DJANGO_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: django-secrets
        key: secret-key
```

---

## 🔐 2. Informatica PowerCenter Credentials

### Location: `monitorportal/monitorportal/settings.py`

**Current (Lines 239-240):**
```python
INFORMATICA_USERNAME = os.getenv('INFORMATICA_USERNAME', 'ab64033')
INFORMATICA_PASSWORD = os.getenv('INFORMATICA_PASSWORD', 'Samsungs26@123')
```

**Action Required:**
- Set `INFORMATICA_USERNAME` with production service account
- Set `INFORMATICA_PASSWORD` with production password
- ❌ Remove hardcoded username/password from settings.py

**Rancher Configuration:**
```yaml
env:
  - name: INFORMATICA_USERNAME
    valueFrom:
      secretKeyRef:
        name: informatica-secrets
        key: username
  - name: INFORMATICA_PASSWORD
    valueFrom:
      secretKeyRef:
        name: informatica-secrets
        key: password
  - name: INFORMATICA_USER_SECURITY_DOMAIN
    value: "CTL"
```

**Additional Informatica Settings to Configure:**
- `INFORMATICA_PMCMD_PATH` - Path to pmcmd on Linux: `/opt/informatica/server/bin/pmcmd`
- `INFORMATICA_HOST` - Production host
- `INFORMATICA_DOMAIN` - Domain_INFA_PRD1
- `INFORMATICA_REPOSITORY_SERVICE` - PCREPO_PRD1_01
- `INFORMATICA_INTEGRATION_SERVICE` - IS_GRID_BI

---

## 🔐 3. Oracle Database: Level3 (ICSM_APPL)

### Location: `monitorportal/portal/db/oracle_client.py`

**Current (Lines 14-21):**
```python
DB_CONFIG = {
    "host": "azeus2loraipcp2.corp.intranet",
    "port": 1521,
    "service": "infr01p_app",
    "user": "icsm_appl",
    "password": "Infprd3_appl"  # ⚠️ HARDCODED PASSWORD!
}
```

**Action Required:**
- ❌ **REMOVE hardcoded password from `oracle_client.py`**
- ✅ Refactor to read from environment variables
- Set environment variables for production

**Rancher Configuration:**
```yaml
env:
  - name: LEVEL3_DB_HOST
    value: "azeus2loraipcp2.corp.intranet"
  - name: LEVEL3_DB_PORT
    value: "1521"
  - name: LEVEL3_DB_SERVICE
    value: "infr01p_app"
  - name: LEVEL3_DB_USER
    valueFrom:
      secretKeyRef:
        name: oracle-level3-secrets
        key: username
  - name: LEVEL3_DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: oracle-level3-secrets
        key: password
```

---

## 🔐 4. Oracle Database: MAPDQPRD (ERP/MDM/ADF)

### Location: `monitorportal/portal/db/oracle_client.py`

**Current (Lines 24-31):**
```python
MAPDQPRD_DB_CONFIG = {
    "host": "RACORAP32-SCAN.CORP.INTRANET",
    "port": 1521,
    "service": "SVC_IDG01P",
    "user": "mapdqprd",
    "password": "2026NewIDMC"  # ⚠️ HARDCODED PASSWORD!
}
```

**Action Required:**
- ❌ **REMOVE hardcoded password from `oracle_client.py`**
- ✅ Refactor to read from environment variables
- Set environment variables for production

**Rancher Configuration:**
```yaml
env:
  - name: MAPDQPRD_DB_HOST
    value: "RACORAP32-SCAN.CORP.INTRANET"
  - name: MAPDQPRD_DB_PORT
    value: "1521"
  - name: MAPDQPRD_DB_SERVICE
    value: "SVC_IDG01P"
  - name: MAPDQPRD_DB_USER
    valueFrom:
      secretKeyRef:
        name: oracle-mapdqprd-secrets
        key: username
  - name: MAPDQPRD_DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: oracle-mapdqprd-secrets
        key: password
```

---

## 🔐 5. Email SMTP Configuration (Optional)

### Location: `monitorportal/monitorportal/settings.py`

**Current (Lines 207-212):**
```python
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mailrelay.corp.intranet')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'naresh.m@lumen.com')
```

**Action Required (if using SMTP):**
- Set `EMAIL_HOST` to production mail relay
- Set `EMAIL_HOST_USER` if authentication required
- Set `EMAIL_HOST_PASSWORD` if authentication required
- Set `DEFAULT_FROM_EMAIL` to production sender email

**Rancher Configuration:**
```yaml
env:
  - name: EMAIL_BACKEND_TYPE
    value: "smtp"  # or "file" or "console"
  - name: EMAIL_HOST
    value: "mailrelay.corp.intranet"
  - name: EMAIL_PORT
    value: "25"
  - name: EMAIL_HOST_USER
    value: ""  # If required
  - name: EMAIL_HOST_PASSWORD
    valueFrom:
      secretKeyRef:
        name: email-secrets
        key: password  # If required
  - name: DEFAULT_FROM_EMAIL
    value: "monitoring@lumen.com"
```

---

## 📝 Code Refactoring Required

### ⚠️ CRITICAL: Refactor `oracle_client.py` to use environment variables

**Current Implementation:**
```python
# ❌ BAD: Hardcoded passwords
DB_CONFIG = {
    "password": "Infprd3_appl"
}
```

**Required Implementation:**
```python
# ✅ GOOD: Read from environment variables
import os

DB_CONFIG = {
    "host": os.getenv("LEVEL3_DB_HOST", "azeus2loraipcp2.corp.intranet"),
    "port": int(os.getenv("LEVEL3_DB_PORT", "1521")),
    "service": os.getenv("LEVEL3_DB_SERVICE", "infr01p_app"),
    "user": os.getenv("LEVEL3_DB_USER", "icsm_appl"),
    "password": os.getenv("LEVEL3_DB_PASSWORD")  # No default in production!
}

MAPDQPRD_DB_CONFIG = {
    "host": os.getenv("MAPDQPRD_DB_HOST", "RACORAP32-SCAN.CORP.INTRANET"),
    "port": int(os.getenv("MAPDQPRD_DB_PORT", "1521")),
    "service": os.getenv("MAPDQPRD_DB_SERVICE", "SVC_IDG01P"),
    "user": os.getenv("MAPDQPRD_DB_USER", "mapdqprd"),
    "password": os.getenv("MAPDQPRD_DB_PASSWORD")  # No default in production!
}
```

---

## 🔧 Additional Production Settings

### Location: `monitorportal/monitorportal/settings.py`

**Update these settings for production:**

```python
# Debug Mode
DEBUG = False  # ⚠️ MUST be False in production!

# Allowed Hosts
ALLOWED_HOSTS = [
    'your-rancher-domain.com',
    'your-app.cluster.local',
    # Add your production domains
]

# Static/Media Files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📦 Kubernetes Secret Creation Commands

### Create Secrets in Rancher/Kubernetes:

```bash
# 1. Django Secret Key
kubectl create secret generic django-secrets \
  --from-literal=secret-key='YOUR_GENERATED_SECRET_KEY_HERE'

# 2. Informatica Credentials
kubectl create secret generic informatica-secrets \
  --from-literal=username='production_username' \
  --from-literal=password='production_password'

# 3. Oracle Level3 Database
kubectl create secret generic oracle-level3-secrets \
  --from-literal=username='icsm_appl' \
  --from-literal=password='PRODUCTION_PASSWORD_HERE'

# 4. Oracle MAPDQPRD Database
kubectl create secret generic oracle-mapdqprd-secrets \
  --from-literal=username='mapdqprd' \
  --from-literal=password='PRODUCTION_PASSWORD_HERE'

# 5. Email Credentials (if needed)
kubectl create secret generic email-secrets \
  --from-literal=password='EMAIL_PASSWORD_HERE'
```

---

## ✅ Pre-Deployment Checklist

- [ ] Generated new Django SECRET_KEY
- [ ] Removed all hardcoded passwords from code
- [ ] Refactored `oracle_client.py` to use environment variables
- [ ] Created Kubernetes secrets in Rancher
- [ ] Set `DEBUG = False` in settings.py
- [ ] Updated `ALLOWED_HOSTS` with production domains
- [ ] Verified Informatica pmcmd path for Linux
- [ ] Tested database connectivity from Rancher cluster
- [ ] Configured production SMTP settings
- [ ] Updated Oracle connection strings for production
- [ ] Removed development credentials from all files
- [ ] Added `.env` to `.gitignore` (if using .env files)
- [ ] Reviewed all `os.getenv()` calls for sensitive data
- [ ] Documented all environment variables needed
- [ ] Set up monitoring and logging
- [ ] Created backup of current production passwords (in secure vault)

---

## 🚨 Security Reminders

1. **Never commit passwords to Git**
   - Check `.gitignore` includes sensitive files
   - Remove any committed passwords from Git history

2. **Use Kubernetes Secrets**
   - Store all passwords in Kubernetes secrets
   - Mount secrets as environment variables
   - Never log secrets to console

3. **Rotate Credentials Regularly**
   - Change passwords every 90 days
   - Use strong, unique passwords for each service
   - Document credential rotation procedures

4. **Principle of Least Privilege**
   - Use service accounts with minimal permissions
   - Don't use admin/root accounts for application connections
   - Separate dev/test/prod credentials

5. **Audit and Monitor**
   - Log authentication attempts
   - Monitor for unauthorized access
   - Set up alerts for security events

---

## 📞 Support Contacts

- **Rancher Support**: [Your Team Contact]
- **Database Admin**: [DBA Team Contact]
- **Security Team**: [Security Contact]
- **DevOps Team**: [DevOps Contact]

---

## 📚 Related Documentation

- [AZURE_DEPLOYMENT_CHECKLIST.md](docs/AZURE_DEPLOYMENT_CHECKLIST.md)
- [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [INFORMATICA_SETTINGS_EXAMPLE.sh](docs/INFORMATICA_SETTINGS_EXAMPLE.sh)

---

**Last Updated**: May 4, 2026
**Document Owner**: DevOps Team
**Review Frequency**: Monthly or before each deployment
