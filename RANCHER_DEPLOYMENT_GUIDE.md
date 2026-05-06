# Production Deployment Guide for Rancher/Kubernetes

## 🚀 Quick Start Deployment Steps

### 1. Build Docker Image

```bash
# Navigate to project root
cd c:\Users\ab64033\source\repos\infa_monitor_portal

# Build Docker image
docker build -t your-registry/infa-monitor-portal:latest .

# Push to your Docker registry (update with your registry URL)
docker push your-registry/infa-monitor-portal:latest
```

### 2. Create Kubernetes Secrets (DO THIS FIRST!)

**⚠️ CRITICAL: Update all passwords before deploying!**

```bash
# Generate new Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Create secrets in Rancher (or via kubectl)
kubectl create secret generic django-secrets \
  --namespace=infa-monitor \
  --from-literal=secret-key='YOUR_GENERATED_SECRET_KEY_HERE'

kubectl create secret generic informatica-secrets \
  --namespace=infa-monitor \
  --from-literal=username='production_service_account' \
  --from-literal=password='PRODUCTION_PASSWORD'

kubectl create secret generic oracle-level3-secrets \
  --namespace=infa-monitor \
  --from-literal=username='icsm_appl' \
  --from-literal=password='PRODUCTION_PASSWORD'

kubectl create secret generic oracle-mapdqprd-secrets \
  --namespace=infa-monitor \
  --from-literal=username='mapdqprd' \
  --from-literal=password='PRODUCTION_PASSWORD'
```

### 3. Update Configuration

Edit `kubernetes-deployment.yaml` and update:

- **Docker registry URL**: `your-registry/infa-monitor-portal:latest`
- **Domain names**: `DJANGO_ALLOWED_HOSTS` in ConfigMap
- **Ingress host**: `infa-monitor.your-domain.com`
- **Informatica pmcmd path**: Verify the path on your Rancher nodes
- **Database connection strings**: Verify they match your production environment

### 4. Deploy to Rancher

**Option A: Using Rancher UI**
1. Login to Rancher
2. Select your cluster
3. Go to "Workloads" → "Import YAML"
4. Paste contents of `kubernetes-deployment.yaml`
5. Click "Import"

**Option B: Using kubectl**
```bash
kubectl apply -f kubernetes-deployment.yaml
```

### 5. Verify Deployment

```bash
# Check pods are running
kubectl get pods -n infa-monitor

# Check logs
kubectl logs -f deployment/infa-monitor-portal -n infa-monitor

# Test health check
kubectl port-forward svc/infa-monitor-portal 8000:80 -n infa-monitor
curl http://localhost:8000/health/
```

---

## ✅ Pre-Deployment Checklist

Complete this checklist before deploying:

- [ ] **Code Changes**
  - [x] Refactored `oracle_client.py` to use environment variables
  - [x] Updated `settings.py` with production-ready defaults
  - [x] Removed hardcoded passwords
  - [x] Added health check endpoint

- [ ] **Docker & Kubernetes**
  - [x] Created Dockerfile
  - [x] Created `.dockerignore`
  - [x] Created `kubernetes-deployment.yaml`
  - [x] Created production requirements file
  - [ ] Built and tested Docker image locally
  - [ ] Pushed Docker image to registry

- [ ] **Configuration**
  - [ ] Generated new Django SECRET_KEY
  - [ ] Created all Kubernetes secrets
  - [ ] Updated ConfigMap with correct values
  - [ ] Updated Docker image URL in deployment YAML
  - [ ] Updated domain names in ALLOWED_HOSTS
  - [ ] Updated Ingress host

- [ ] **Infrastructure**
  - [ ] Verified Informatica pmcmd is accessible from Rancher nodes
  - [ ] Verified Oracle databases are accessible from Rancher cluster
  - [ ] Configured network policies/firewall rules
  - [ ] Set up persistent storage (if needed)

- [ ] **Testing**
  - [ ] Tested application locally with production settings
  - [ ] Verified database connections work
  - [ ] Tested Informatica restart functionality
  - [ ] Reviewed application logs for errors

---

## 🔧 What Was Fixed for Production

### 1. **Security Fixes** ✅
- ❌ **Before**: Hardcoded passwords in `oracle_client.py`
- ✅ **After**: Environment variables with Kubernetes secrets

### 2. **Django Configuration** ✅
- ❌ **Before**: `DEBUG = True` (security risk)
- ✅ **After**: `DEBUG = False` from environment variable

- ❌ **Before**: `ALLOWED_HOSTS = ['*']` (accepts all domains)
- ✅ **After**: Specific domains from environment variable

### 3. **Static Files** ✅
- ❌ **Before**: No production static file configuration
- ✅ **After**: WhiteNoise for efficient static file serving

### 4. **Application Server** ✅
- ❌ **Before**: Django development server only
- ✅ **After**: Gunicorn WSGI server with 4 workers

### 5. **Health Checks** ✅
- ❌ **Before**: No health check endpoint
- ✅ **After**: `/health/` endpoint for Kubernetes probes

### 6. **Database SQLite Issue** ⚠️ **Note**
- Your current `settings.py` uses SQLite for Django's database
- SQLite **does not work** in Kubernetes (data lost on pod restart)
- **However**: Your app primarily uses Oracle databases directly via `oracle_client.py`
- SQLite is only used for Django admin, sessions, and internal models
- **Recommendation**: If you use Django models, switch to PostgreSQL or Oracle

---

## 📁 New Files Created

1. **`Dockerfile`** - Container image definition
2. **`requirements-production.txt`** - Production Python dependencies
3. **`.dockerignore`** - Excludes unnecessary files from Docker build
4. **`kubernetes-deployment.yaml`** - Complete K8s deployment configuration
5. **`portal/health.py`** - Health check endpoint
6. **`RANCHER_DEPLOYMENT_GUIDE.md`** - This file

---

## 🐛 Troubleshooting

### Application won't start
- Check pod logs: `kubectl logs deployment/infa-monitor-portal -n infa-monitor`
- Verify all environment variables are set
- Check if secrets exist: `kubectl get secrets -n infa-monitor`

### Database connection fails
- Verify network connectivity from pod to Oracle databases
- Check firewall rules allow traffic from Rancher cluster
- Test connection: `kubectl exec -it pod/infa-monitor-portal-xxx -n infa-monitor -- python -c "from portal.db.oracle_client import get_conn; get_conn()"`

### Static files not loading
- Run collectstatic: `kubectl exec -it pod/infa-monitor-portal-xxx -n infa-monitor -- python manage.py collectstatic --noinput`
- Check WhiteNoise is in MIDDLEWARE
- Verify STATIC_ROOT is configured

### Informatica restart not working
- Verify pmcmd is mounted/accessible in container
- Check INFORMATICA_PMCMD_PATH is correct
- Verify credentials in informatica-secrets

---

## 📞 Support

If you encounter issues:

1. Check pod logs: `kubectl logs -f deployment/infa-monitor-portal -n infa-monitor`
2. Check events: `kubectl get events -n infa-monitor --sort-by='.lastTimestamp'`
3. Describe pod: `kubectl describe pod/infa-monitor-portal-xxx -n infa-monitor`
4. Review the pre-deployment checklist above

---

## 🔄 Updates and Rollbacks

### Deploy new version
```bash
# Build and push new image with version tag
docker build -t your-registry/infa-monitor-portal:v1.1 .
docker push your-registry/infa-monitor-portal:v1.1

# Update deployment
kubectl set image deployment/infa-monitor-portal \
  infa-monitor-portal=your-registry/infa-monitor-portal:v1.1 \
  -n infa-monitor
```

### Rollback to previous version
```bash
kubectl rollout undo deployment/infa-monitor-portal -n infa-monitor
```

### Check rollout status
```bash
kubectl rollout status deployment/infa-monitor-portal -n infa-monitor
```

---

**Your code is now Rancher-ready! 🎉**
