# Production Deployment Checklist for Rancher

## ✅ **YES, You Can Deploy to Rancher!**

All functionality will work **IF** you complete this checklist first.

---

## 🚨 CRITICAL: Do Before Deploying

### 1. ✅ **Add Cryptography Package** (COMPLETED)
- [x] Added `cryptography>=41.0.0` to requirements.txt
- [x] Added to requirements-python310.txt
- [x] Pushed to GitHub

### 2. ⚠️ **Enable WhiteNoise for Static Files** (TODO)

**Current State:** WhiteNoise is commented out (local dev)

**Action Required:**
Edit `monitorportal/monitorportal/settings.py`:

```python
# Line 56: UNCOMMENT this line
"whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ PRODUCTION ONLY

# Line 157: UNCOMMENT this line
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

**Why:** Without WhiteNoise, CSS/JS/images won't load in production.

### 3. ⚠️ **Remove Dev Middleware** (TODO)

**Current State:** Dev middleware simulates SSO locally

**Action Required:**
Edit `monitorportal/monitorportal/settings.py`:

```python
# Line 61: COMMENT OUT OR REMOVE this line
# "portal.middleware.DevRemoteUserMiddleware",  # DEV ONLY

# Keep this line (production SSO):
"django.contrib.auth.middleware.RemoteUserMiddleware",  # SSO CUID capture
```

**Why:** Dev middleware will interfere with real SSO authentication.

---

## 📋 Environment Variables Required

Set these in Rancher ConfigMap/Secrets:

### Required Environment Variables:

| Variable | Example Value | Purpose |
|----------|---------------|---------|
| `DJANGO_SECRET_KEY` | (generate new) | Django security |
| `DJANGO_DEBUG` | `False` | Production mode |
| `DJANGO_ALLOWED_HOSTS` | `infa-monitor.yourcompany.com,rancher-prod-01` | Allowed domains |
| `INFORMATICA_PMCMD_PATH` | `/opt/informatica/client/pmcmd` | Informatica CLI path |
| `INFORMATICA_DOMAIN` | `Domain_INFA_PRD1` | Informatica domain |
| `INFORMATICA_REPOSITORY` | `PCREPO_PRD1_01` | Informatica repository |
| `INFORMATICA_INTEGRATION_SERVICE` | `IS_GRID_BI` | Integration service |
| `INFORMATICA_SECURITY_DOMAIN` | `CTL` | Security domain |
| `ORACLE_LEVEL3_HOST` | `azeus2loraipcp2.corp.intranet` | Level3 DB host |
| `ORACLE_LEVEL3_PORT` | `1521` | Level3 DB port |
| `ORACLE_LEVEL3_SERVICE` | `infr01p_app` | Level3 service name |
| `ORACLE_LEVEL3_USERNAME` | `icsm_appl` | Level3 username |
| `ORACLE_LEVEL3_PASSWORD` | (secret) | Level3 password |
| `ORACLE_MAPDQPRD_HOST` | `RACORAP32-SCAN.CORP.INTRANET` | MDM DB host |
| `ORACLE_MAPDQPRD_PORT` | `1521` | MDM DB port |
| `ORACLE_MAPDQPRD_SERVICE` | `SVC_IDG01P` | MDM service name |
| `ORACLE_MAPDQPRD_USERNAME` | `mapdqprd` | MDM username |
| `ORACLE_MAPDQPRD_PASSWORD` | (secret) | MDM password |

---

## 🔐 Generate New Django Secret Key

**DO NOT use the dev secret key in production!**

```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `DJANGO_SECRET_KEY` environment variable.

---

## 📦 Deployment Steps

### Step 1: Update Code for Production
```bash
# Make the two code changes above (WhiteNoise + Remove DevMiddleware)
git add monitorportal/monitorportal/settings.py
git commit -m "Enable WhiteNoise and remove dev middleware for production"
git push origin main
git push centurylink main
```

### Step 2: Build Docker Image
```bash
cd c:\Users\ab64033\source\repos\infa_monitor_portal
docker build -t your-registry/infa-monitor-portal:v1.0 .
docker push your-registry/infa-monitor-portal:v1.0
```

### Step 3: Create Kubernetes Secrets (in Rancher)
```bash
# Django secret
kubectl create secret generic django-secrets \
  --namespace=infa-monitor \
  --from-literal=secret-key='YOUR_GENERATED_SECRET_KEY'

# Oracle Level3 DB
kubectl create secret generic oracle-level3-secrets \
  --namespace=infa-monitor \
  --from-literal=username='icsm_appl' \
  --from-literal=password='PROD_PASSWORD_HERE'

# Oracle MAPDQPRD DB
kubectl create secret generic oracle-mapdqprd-secrets \
  --namespace=infa-monitor \
  --from-literal=username='mapdqprd' \
  --from-literal=password='PROD_PASSWORD_HERE'
```

### Step 4: Deploy to Rancher
1. Login to Rancher UI
2. Select your cluster and namespace
3. Go to **Workloads** → **Import YAML**
4. Upload `kubernetes-deployment.yaml`
5. Click **Import**

### Step 5: Verify Deployment
```bash
# Check pods
kubectl get pods -n infa-monitor

# Check logs
kubectl logs -f deployment/infa-monitor-portal -n infa-monitor

# Test the app
kubectl port-forward svc/infa-monitor-portal 8080:80 -n infa-monitor
# Open browser: http://localhost:8080/
```

---

## ✅ Will All Functionality Work?

### **YES, if you complete the checklist!**

| Feature | Status | Notes |
|---------|--------|-------|
| **Login System** | ✅ Ready | Mandatory CUID + password login |
| **Permission-Based Access** | ✅ Ready | Full/Read-only based on Informatica auth |
| **Password Encryption** | ✅ Ready | Cryptography package added |
| **Informatica Restart** | ✅ Ready | Uses user credentials from session |
| **Informatica Stop** | ✅ Ready | Protected by access level check |
| **Informatica Schedule** | ✅ Ready | Protected by access level check |
| **Oracle Dashboards** | ✅ Ready | Environment variables configured |
| **Static Files (CSS/JS)** | ⚠️ **TODO** | Enable WhiteNoise first |
| **SSO Authentication** | ⚠️ **TODO** | Remove dev middleware first |
| **Session Management** | ✅ Ready | Django sessions work in production |

---

## 🚧 Two Code Changes Needed

Before deploying, make these changes:

### Change 1: Enable WhiteNoise
**File:** `monitorportal/monitorportal/settings.py`

**Line 56:** Uncomment WhiteNoise middleware
```python
# FROM:
# "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ PRODUCTION ONLY

# TO:
"whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ PRODUCTION
```

**Line 157:** Uncomment static files storage
```python
# FROM:
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# TO:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

### Change 2: Remove Dev Middleware
**File:** `monitorportal/monitorportal/settings.py`

**Line 61:** Comment out dev middleware
```python
# FROM:
"portal.middleware.DevRemoteUserMiddleware",  # DEV ONLY

# TO:
# "portal.middleware.DevRemoteUserMiddleware",  # DEV ONLY - Disabled for production
```

---

## 📊 Testing After Deployment

1. **Login Test:**
   - Open portal URL
   - Enter your CUID + LDAP password
   - Verify username shows in header

2. **Full Access Test** (Prod Support):
   - Login with Informatica permissions
   - Verify green "Full Access" badge
   - Try restarting a workflow
   - Verify success

3. **Read-Only Test** (Developer):
   - Login with non-Informatica user
   - Verify blue "Read-Only" badge
   - Try accessing Informatica features
   - Should see "Access Required" message

4. **Dashboard Test:**
   - View Level3 dashboard
   - View MDM dashboard
   - View ERP dashboard
   - Verify data loads correctly

---

## 🔍 Troubleshooting

### Issue: "DisallowedHost" Error
**Solution:** Add your domain to `DJANGO_ALLOWED_HOSTS` environment variable

### Issue: CSS/JS not loading
**Solution:** Enable WhiteNoise (see Change 1 above), run `collectstatic`

### Issue: Login loops back to login page
**Solution:** Check SSO middleware is configured, verify REMOTE_USER header

### Issue: Informatica actions fail
**Solution:** Verify `INFORMATICA_PMCMD_PATH` environment variable points to correct path

### Issue: Database connection fails
**Solution:** Verify Oracle credentials in secrets, check network connectivity

---

## 📝 Summary

**Current Status:**
- ✅ Code is production-ready
- ✅ Authentication system complete
- ✅ Cryptography dependency added
- ⚠️ 2 code changes needed (WhiteNoise + Dev middleware)
- ⚠️ Environment variables need to be set in Rancher

**What Works:**
- Login with CUID + password ✅
- Permission-based access (Full/Read-only) ✅
- Informatica workflow management ✅
- Oracle database dashboards ✅
- Session security ✅

**Action Required:**
1. Make 2 code changes in settings.py
2. Set environment variables in Rancher
3. Generate new Django secret key
4. Deploy!

**Estimated Time:** 30-60 minutes

---

See also:
- [RANCHER_DEPLOYMENT_GUIDE.md](RANCHER_DEPLOYMENT_GUIDE.md) - Full deployment guide
- [LOGIN_FIRST_AUTHENTICATION.md](LOGIN_FIRST_AUTHENTICATION.md) - Authentication flow
- [kubernetes-deployment.yaml](kubernetes-deployment.yaml) - K8s configuration
