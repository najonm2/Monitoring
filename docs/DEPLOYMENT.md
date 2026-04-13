# Production Deployment Guide

## Overview

This guide covers deploying the PASE Monitor Portal to a production environment.

---

## Pre-Deployment Checklist

### Security
- [ ] Database credentials moved to environment variables
- [ ] `DEBUG = False` in settings.py
- [ ] `SECRET_KEY` changed and secured
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enabled
- [ ] Database user has minimal permissions
- [ ] `.env` file is in `.gitignore`

### Performance
- [ ] Static files collected
- [ ] Database connection pooling enabled
- [ ] Caching configured (Redis/Memcached)
- [ ] Gunicorn/uWSGI configured
- [ ] Nginx/Apache reverse proxy setup

### Monitoring
- [ ] Logging configured
- [ ] Error tracking setup (Sentry/similar)
- [ ] Health check endpoint created
- [ ] Backup strategy defined

---

## Method 1: Windows Server with IIS

### Step 1: Install Requirements

```powershell
# Install Python 3.11
# Download from: https://www.python.org/downloads/

# Install wfastcgi
pip install wfastcgi

# Enable IIS FastCGI
Install-WindowsFeature Web-Server, Web-CGI
```

### Step 2: Configure IIS

1. Open IIS Manager
2. Create new website:
   - Site name: PASE_Monitor_Portal
   - Physical path: `C:\inetpub\wwwroot\monitorportal`
   - Port: 80 or 443 (HTTPS)

3. Handler Mappings:
   - Request path: `*`
   - Module: FastCgiModule
   - Executable: `C:\Python311\python.exe|C:\Python311\Lib\site-packages\wfastcgi.py`
   - Name: Django

### Step 3: web.config

Create `monitorportal/web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="Django" path="*" verb="*" 
                 modules="FastCgiModule"
                 scriptProcessor="C:\Python311\python.exe|C:\Python311\Lib\site-packages\wfastcgi.py"
                 resourceType="Unspecified" 
                 requireAccess="Script" />
        </handlers>
    </system.webServer>
    <appSettings>
        <add key="WSGI_HANDLER" value="monitorportal.wsgi.application" />
        <add key="PYTHONPATH" value="C:\inetpub\wwwroot\monitorportal" />
        <add key="DJANGO_SETTINGS_MODULE" value="monitorportal.settings" />
    </appSettings>
</configuration>
```

---

## Method 2: Linux Server (Ubuntu/RHEL)

### Step 1: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# RHEL/CentOS
sudo yum install python3 python3-pip nginx
```

### Step 2: Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/monitorportal
sudo chown $USER:$USER /var/www/monitorportal

# Copy application
cp -r monitorportal /var/www/

# Create virtual environment
cd /var/www/monitorportal
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 3: Configure Gunicorn

Create `/etc/systemd/system/monitorportal.service`:

```ini
[Unit]
Description=PASE Monitor Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/monitorportal
Environment="PATH=/var/www/monitorportal/venv/bin"
ExecStart=/var/www/monitorportal/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/var/www/monitorportal/monitorportal.sock \
          monitorportal.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable monitorportal
sudo systemctl start monitorportal
sudo systemctl status monitorportal
```

### Step 4: Configure Nginx

Create `/etc/nginx/sites-available/monitorportal`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /var/www/monitorportal/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/monitorportal/monitorportal.sock;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/monitorportal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Method 3: Docker Container

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Oracle Instant Client
RUN apt-get update && \
    apt-get install -y libaio1 wget unzip && \
    wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linuxx64.zip && \
    unzip instantclient-basic-linuxx64.zip -d /opt/oracle && \
    rm instantclient-basic-linuxx64.zip

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_8:$LD_LIBRARY_PATH

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY monitorportal /app/

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "monitorportal.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DJANGO_SECRET_KEY=${SECRET_KEY}
      - ORACLE_USER=${ORACLE_USER}
      - ORACLE_PASSWORD=${ORACLE_PASSWORD}
    volumes:
      - static_volume:/app/staticfiles
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/usr/share/nginx/html/static
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
    restart: unless-stopped

volumes:
  static_volume:
```

Build and run:
```bash
docker-compose up -d
```

---

## Method 4: Azure Cloud Deployment

### Option 4A: Azure App Service (PaaS) - Recommended

Azure App Service is the easiest and most managed option for deploying Django applications.

#### Prerequisites

```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Set your subscription
az account set --subscription "your-subscription-name"
```

#### Step 1: Create Azure Resources

```powershell
# Set variables
$RESOURCE_GROUP="rg-monitorportal-prod"
$LOCATION="eastus"  # or your preferred region
$APP_SERVICE_PLAN="asp-monitorportal"
$WEB_APP_NAME="monitorportal-app"  # Must be globally unique

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service Plan (Linux, Python 3.11)
az appservice plan create `
    --name $APP_SERVICE_PLAN `
    --resource-group $RESOURCE_GROUP `
    --sku B2 `
    --is-linux

# Create Web App
az webapp create `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --plan $APP_SERVICE_PLAN `
    --runtime "PYTHON:3.11"
```

#### Step 2: Configure Application Settings

```powershell
# Set environment variables in Azure
az webapp config appsettings set `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings `
        DEBUG=False `
        SECRET_KEY="your-secure-secret-key-here" `
        ALLOWED_HOSTS="$WEB_APP_NAME.azurewebsites.net" `
        LEVEL3_DB_USER="your-db-user" `
        LEVEL3_DB_PASSWORD="your-db-password" `
        LEVEL3_DB_HOST="10.120.190.4" `
        LEVEL3_DB_PORT="1521" `
        LEVEL3_DB_SERVICE="infr01p_app" `
        MAPDQPRD_DB_USER="your-db-user" `
        MAPDQPRD_DB_PASSWORD="your-db-password" `
        MAPDQPRD_DB_HOST="RACORAP32-SCAN.CORP.INTRANET" `
        MAPDQPRD_DB_PORT="1521" `
        MAPDQPRD_DB_SERVICE="SVC_IDG01P" `
        WEBSITES_PORT="8000" `
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

#### Step 3: Prepare Deployment Files

Create `.deployment` in project root:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT = true
```

Create `startup.sh` in project root:
```bash
#!/bin/bash
cd monitorportal

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate --noinput

# Start Gunicorn
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile '-' --error-logfile '-' monitorportal.wsgi:application
```

Create `requirements-azure.txt`:
```txt
Django>=6.0.0,<7.0.0
python-oracledb>=2.0.0
gunicorn>=21.0.0
whitenoise>=6.0.0
```

#### Step 4: Update settings.py for Azure

Add to `monitorportal/settings.py`:
```python
import os

# Azure App Service detection
RUNNING_IN_AZURE = os.getenv('WEBSITE_SITE_NAME') is not None

if RUNNING_IN_AZURE:
    DEBUG = False
    
    # WhiteNoise for static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Configure ALLOWED_HOSTS from environment
    ALLOWED_HOSTS = [
        os.getenv('WEBSITE_HOSTNAME'),
        os.getenv('WEBSITE_SITE_NAME') + '.azurewebsites.net'
    ]
    
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

#### Step 5: Deploy to Azure

**Option 5A: Using Azure CLI (Local Git)**
```powershell
# Configure local Git deployment
az webapp deployment source config-local-git `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP

# Get deployment credentials
$GIT_URL = az webapp deployment source show `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query "repoUrl" -o tsv

# Add Azure remote and push
cd c:\Users\ab64033\source\repos\infa_monitor_portal
git init  # if not already a git repo
git add .
git commit -m "Initial deployment to Azure"
git remote add azure $GIT_URL
git push azure main  # or master
```

**Option 5B: Using ZIP Deployment**
```powershell
# Create deployment package
cd c:\Users\ab64033\source\repos\infa_monitor_portal
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy
az webapp deployment source config-zip `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --src deploy.zip
```

**Option 5C: Using VS Code Azure Extension**
1. Install "Azure App Service" extension in VS Code
2. Right-click project folder → "Deploy to Web App"
3. Select subscription and web app
4. Confirm deployment

#### Step 6: Configure Networking for Oracle Databases

If your Oracle databases are on-premises or in a VNet:

```powershell
# Option 1: VNet Integration (for databases in Azure VNet)
az webapp vnet-integration add `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --vnet "your-vnet-name" `
    --subnet "your-subnet-name"

# Option 2: Hybrid Connection (for on-premises databases)
# Configure in Azure Portal → App Service → Networking → Hybrid connections
```

#### Step 7: Enable Application Insights (Monitoring)

```powershell
# Create Application Insights
az extension add --name application-insights
az monitor app-insights component create `
    --app monitorportal-insights `
    --location $LOCATION `
    --resource-group $RESOURCE_GROUP `
    --application-type web

# Get instrumentation key
$INSIGHTS_KEY = az monitor app-insights component show `
    --app monitorportal-insights `
    --resource-group $RESOURCE_GROUP `
    --query "instrumentationKey" -o tsv

# Configure App Service to use Application Insights
az webapp config appsettings set `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY
```

#### Step 8: Configure Custom Domain (Optional)

```powershell
# Add custom domain
az webapp config hostname add `
    --webapp-name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --hostname "monitorportal.yourdomain.com"

# Enable HTTPS
az webapp config ssl bind `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --certificate-thumbprint "your-cert-thumbprint" `
    --ssl-type SNI
```

#### Scaling Configuration

```powershell
# Auto-scaling rules
az monitor autoscale create `
    --name "monitorportal-autoscale" `
    --resource-group $RESOURCE_GROUP `
    --resource $APP_SERVICE_PLAN `
    --resource-type Microsoft.Web/serverfarms `
    --min-count 2 `
    --max-count 5 `
    --count 2

# Scale up based on CPU
az monitor autoscale rule create `
    --autoscale-name "monitorportal-autoscale" `
    --resource-group $RESOURCE_GROUP `
    --condition "Percentage CPU > 70 avg 5m" `
    --scale out 1
```

---

### Option 4B: Azure Container Instances (ACI)

For containerized deployment with less management overhead than AKS.

#### Step 1: Build and Push Docker Image

```powershell
# Create Azure Container Registry
$ACR_NAME="monitorportalacr"  # Must be globally unique
az acr create `
    --name $ACR_NAME `
    --resource-group $RESOURCE_GROUP `
    --sku Basic `
    --admin-enabled true

# Login to ACR
az acr login --name $ACR_NAME

# Build and push image
cd c:\Users\ab64033\source\repos\infa_monitor_portal
docker build -t monitorportal:latest -f Dockerfile .
docker tag monitorportal:latest "$ACR_NAME.azurecr.io/monitorportal:latest"
docker push "$ACR_NAME.azurecr.io/monitorportal:latest"
```

#### Step 2: Create Container Instance

```powershell
# Get ACR credentials
$ACR_PASSWORD = az acr credential show `
    --name $ACR_NAME `
    --query "passwords[0].value" -o tsv

# Create container instance
az container create `
    --name monitorportal-container `
    --resource-group $RESOURCE_GROUP `
    --image "$ACR_NAME.azurecr.io/monitorportal:latest" `
    --registry-login-server "$ACR_NAME.azurecr.io" `
    --registry-username $ACR_NAME `
    --registry-password $ACR_PASSWORD `
    --dns-name-label monitorportal `
    --ports 8000 `
    --cpu 2 `
    --memory 4 `
    --environment-variables `
        DEBUG=False `
        SECRET_KEY="your-secret-key" `
        LEVEL3_DB_USER="user" `
        LEVEL3_DB_PASSWORD="password"

# Get the FQDN
az container show `
    --name monitorportal-container `
    --resource-group $RESOURCE_GROUP `
    --query "ipAddress.fqdn"
```

---

### Option 4C: Azure Virtual Machine (IaaS)

For full control, deploy on a Windows or Linux VM.

#### Windows VM Deployment

```powershell
# Create Windows VM
az vm create `
    --name monitorportal-vm `
    --resource-group $RESOURCE_GROUP `
    --image Win2022Datacenter `
    --size Standard_D2s_v3 `
    --admin-username azureuser `
    --admin-password "YourSecurePassword123!"

# Open port 80 and 443
az vm open-port --port 80 --resource-group $RESOURCE_GROUP --name monitorportal-vm
az vm open-port --port 443 --resource-group $RESOURCE_GROUP --name monitorportal-vm

# Connect via RDP and follow "Method 1: Windows Server with IIS" steps above
```

#### Linux VM Deployment

```powershell
# Create Linux VM
az vm create `
    --name monitorportal-vm `
    --resource-group $RESOURCE_GROUP `
    --image Ubuntu2204 `
    --size Standard_D2s_v3 `
    --admin-username azureuser `
    --generate-ssh-keys

# Open ports
az vm open-port --port 80 --resource-group $RESOURCE_GROUP --name monitorportal-vm
az vm open-port --port 443 --resource-group $RESOURCE_GROUP --name monitorportal-vm

# SSH into VM and follow "Method 2: Linux Server" steps above
```

---

### Azure Deployment Best Practices

#### 1. Use Azure Key Vault for Secrets

```powershell
# Create Key Vault
az keyvault create `
    --name "monitorportal-kv" `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION

# Store secrets
az keyvault secret set `
    --vault-name "monitorportal-kv" `
    --name "django-secret-key" `
    --value "your-secret-key"

az keyvault secret set `
    --vault-name "monitorportal-kv" `
    --name "level3-db-password" `
    --value "your-db-password"

# Grant App Service access to Key Vault
$APP_IDENTITY = az webapp identity assign `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query "principalId" -o tsv

az keyvault set-policy `
    --name "monitorportal-kv" `
    --object-id $APP_IDENTITY `
    --secret-permissions get list

# Reference secrets in App Settings
az webapp config appsettings set `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings `
        SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://monitorportal-kv.vault.azure.net/secrets/django-secret-key/)" `
        LEVEL3_DB_PASSWORD="@Microsoft.KeyVault(SecretUri=https://monitorportal-kv.vault.azure.net/secrets/level3-db-password/)"
```

#### 2. Enable Diagnostic Logging

```powershell
# Create Log Analytics Workspace
az monitor log-analytics workspace create `
    --resource-group $RESOURCE_GROUP `
    --workspace-name monitorportal-logs

# Enable diagnostic settings
az monitor diagnostic-settings create `
    --name monitorportal-diagnostics `
    --resource "/subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" `
    --logs '[{"category": "AppServiceHTTPLogs", "enabled": true}, {"category": "AppServiceConsoleLogs", "enabled": true}]' `
    --metrics '[{"category": "AllMetrics", "enabled": true}]' `
    --workspace monitorportal-logs
```

#### 3. Set Up Azure Front Door (CDN + WAF)

```powershell
# Create Front Door
az extension add --name front-door
az network front-door create `
    --name monitorportal-fd `
    --resource-group $RESOURCE_GROUP `
    --backend-address "$WEB_APP_NAME.azurewebsites.net" `
    --accepted-protocols Http Https
```

#### 4. Backup Strategy

```powershell
# Enable automatic backups
az webapp config backup create `
    --resource-group $RESOURCE_GROUP `
    --webapp-name $WEB_APP_NAME `
    --container-url "https://yourstorageaccount.blob.core.windows.net/backups?{SAS-token}" `
    --backup-name initial-backup

# Schedule automatic backups
az webapp config backup update `
    --resource-group $RESOURCE_GROUP `
    --webapp-name $WEB_APP_NAME `
    --container-url "https://yourstorageaccount.blob.core.windows.net/backups?{SAS-token}" `
    --frequency 1d `
    --retain-one true `
    --retention 30
```

#### 5. Cost Optimization

```powershell
# Use deployment slots for staging
az webapp deployment slot create `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --slot staging

# Deploy to staging first
az webapp deployment source config-zip `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --slot staging `
    --src deploy.zip

# Swap to production after testing
az webapp deployment slot swap `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --slot staging
```

---

### Azure Troubleshooting

#### View Application Logs
```powershell
# Stream logs in real-time
az webapp log tail `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP

# Download logs
az webapp log download `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --log-file webapp_logs.zip
```

#### SSH into App Service Container
```powershell
az webapp ssh `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP
```

#### Common Issues

**Issue**: Oracle connection timeout
- **Solution**: Configure VNet Integration or Hybrid Connection
- Verify firewall rules allow Azure IP ranges
- Check NSG (Network Security Group) rules

**Issue**: Static files not loading
- **Solution**: Run `python manage.py collectstatic`
- Add `whitenoise` to middleware
- Verify `STATIC_ROOT` is configured

**Issue**: 500 Internal Server Error
- **Solution**: Check Application Insights logs
- Enable detailed error pages temporarily
- Verify all environment variables are set

---

## Environment Variables Configuration

### Create .env file

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Level3 Database
LEVEL3_DB_USER=username
LEVEL3_DB_PASSWORD=password
LEVEL3_DB_HOST=10.120.190.4
LEVEL3_DB_PORT=1521
LEVEL3_DB_SERVICE=infr01p_app

# MAPDQPRD Database
MAPDQPRD_DB_USER=username
MAPDQPRD_DB_PASSWORD=password
MAPDQPRD_DB_HOST=RACORAP32-SCAN.CORP.INTRANET
MAPDQPRD_DB_PORT=1521
MAPDQPRD_DB_SERVICE=SVC_IDG01P
```

### Update oracle_client.py

```python
import os

DB_CONFIG = {
    'user': os.getenv('LEVEL3_DB_USER'),
    'password': os.getenv('LEVEL3_DB_PASSWORD'),
    'host': os.getenv('LEVEL3_DB_HOST'),
    'port': int(os.getenv('LEVEL3_DB_PORT', 1521)),
    'service_name': os.getenv('LEVEL3_DB_SERVICE')
}

MAPDQPRD_DB_CONFIG = {
    'user': os.getenv('MAPDQPRD_DB_USER'),
    'password': os.getenv('MAPDQPRD_DB_PASSWORD'),
    'host': os.getenv('MAPDQPRD_DB_HOST'),
    'port': int(os.getenv('MAPDQPRD_DB_PORT', 1521)),
    'service_name': os.getenv('MAPDQPRD_DB_SERVICE')
}
```

---

## Production settings.py Updates

```python
import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database (use PostgreSQL in production if needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/monitorportal/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

## SSL/HTTPS Configuration

### Using Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

### Nginx HTTPS Config

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location /static/ {
        alias /var/www/monitorportal/staticfiles/;
    }

    location / {
        proxy_pass http://unix:/var/www/monitorportal/monitorportal.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Database Connection Pooling

### Install cx_Oracle_async (for connection pooling)

```bash
pip install cx_Oracle_async
```

### Update oracle_client.py

```python
import oracledb

# Create connection pool
pool = oracledb.create_pool(
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    dsn=f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['service_name']}",
    min=2,
    max=10,
    increment=1
)

def fetch_all(query, params=None):
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or {})
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

---

## Monitoring & Logging

### Setup Sentry for Error Tracking

```bash
pip install sentry-sdk
```

In `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

### Health Check Endpoint

In `portal/views.py`:
```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'PASE Monitor Portal',
        'version': '1.0.0'
    })
```

In `urls.py`:
```python
path('health/', health_check, name='health'),
```

---

## Backup Strategy

### Database Backup (SQLite)

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/var/backups/monitorportal"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /var/www/monitorportal/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +30 -delete
```

### Cron Job

```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup.sh
```

---

## Performance Optimization

### Enable Static File Compression

```nginx
# In nginx config
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### Django Caching

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### View Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def api_view(request, app_id, report_id):
    # Your view code
    pass
```

---

## Rollback Plan

Always maintain ability to rollback:

1. Keep previous version accessible
2. Document database schema changes
3. Test rollback procedure in staging
4. Have backup restoration procedure ready

---

## Post-Deployment Verification

- [ ] Homepage loads correctly
- [ ] All dashboards display data
- [ ] API endpoints respond
- [ ] Static files load (CSS, JS)
- [ ] Database connections work
- [ ] HTTPS works correctly
- [ ] Logs are being written
- [ ] Error tracking is working
- [ ] Health check endpoint responds

---

## Maintenance Tasks

### Weekly
- Check error logs
- Review application performance
- Verify backups completed

### Monthly
- Update dependencies (`pip list --outdated`)
- Review and rotate credentials
- Check disk space usage

### Quarterly
- Security audit
- Performance optimization review
- Backup restoration test

---

## Support Contacts

- **Technical Issues**: IT Support Team
- **Database Access**: DBA Team
- **Application Owner**: PASE Team

---

**Last Updated**: April 9, 2026
