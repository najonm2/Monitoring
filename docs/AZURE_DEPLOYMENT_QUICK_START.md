# Azure Deployment Quick Start Guide

This guide provides a fast-track deployment to Azure App Service (recommended method).

## Prerequisites

- Azure subscription
- Azure CLI installed
- Project source code
- Oracle database connectivity details

## 5-Minute Deployment

### 1. Install and Login to Azure

```powershell
# Install Azure CLI (if not installed)
winget install Microsoft.AzureCLI

# Login
az login

# Set subscription
az account set --subscription "your-subscription-name"
```

### 2. Create Azure Resources

```powershell
# Set variables (customize these)
$RESOURCE_GROUP = "rg-monitorportal-prod"
$LOCATION = "eastus"
$APP_SERVICE_PLAN = "asp-monitorportal"
$WEB_APP_NAME = "monitorportal-$(Get-Random -Minimum 1000 -Maximum 9999)"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service Plan
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

Write-Host "Web App URL: https://$WEB_APP_NAME.azurewebsites.net"
```

### 3. Configure Environment Variables

```powershell
az webapp config appsettings set `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings `
        DEBUG=False `
        SECRET_KEY="$(New-Guid)" `
        ALLOWED_HOSTS="$WEB_APP_NAME.azurewebsites.net" `
        LEVEL3_DB_USER="your_db_username" `
        LEVEL3_DB_PASSWORD="your_db_password" `
        LEVEL3_DB_HOST="10.120.190.4" `
        LEVEL3_DB_PORT="1521" `
        LEVEL3_DB_SERVICE="infr01p_app" `
        MAPDQPRD_DB_USER="your_db_username" `
        MAPDQPRD_DB_PASSWORD="your_db_password" `
        MAPDQPRD_DB_HOST="RACORAP32-SCAN.CORP.INTRANET" `
        MAPDQPRD_DB_PORT="1521" `
        MAPDQPRD_DB_SERVICE="SVC_IDG01P" `
        WEBSITES_PORT="8000" `
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### 4. Prepare Project Files

Create these files in your project root:

**startup.sh**
```bash
#!/bin/bash
cd monitorportal
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 monitorportal.wsgi:application
```

**requirements.txt** (update if needed)
```txt
Django>=6.0.0,<7.0.0
python-oracledb>=2.0.0
gunicorn>=21.0.0
whitenoise>=6.0.0
```

**.deployment**
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT = true
```

### 5. Update settings.py for Azure

Add to `monitorportal/monitorportal/settings.py`:

```python
import os

# Azure App Service detection
RUNNING_IN_AZURE = os.getenv('WEBSITE_SITE_NAME') is not None

if RUNNING_IN_AZURE:
    DEBUG = False
    
    # Load environment variables
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALLOWED_HOSTS = [os.getenv('WEBSITE_HOSTNAME'), '*.azurewebsites.net']
    
    # WhiteNoise for static files
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
        MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Security settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

### 6. Deploy to Azure

**Option A: ZIP Deployment (Fastest)**
```powershell
cd c:\Users\ab64033\source\repos\infa_monitor_portal

# Create ZIP file
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy
az webapp deployment source config-zip `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --src deploy.zip

Write-Host "Deployment complete! Visit: https://$WEB_APP_NAME.azurewebsites.net"
```

**Option B: Git Deployment**
```powershell
# Enable local git
az webapp deployment source config-local-git `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP

# Get git URL
$GIT_URL = az webapp deployment list-publishing-credentials `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query "scmUri" -o tsv

# Deploy
git init
git add .
git commit -m "Initial Azure deployment"
git remote add azure $GIT_URL
git push azure main
```

### 7. Configure Database Connectivity

If Oracle databases are on-premises or in a private network:

```powershell
# Option 1: VNet Integration (for Azure VNet)
az webapp vnet-integration add `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --vnet "your-vnet-name" `
    --subnet "your-subnet-name"

# Option 2: Configure Hybrid Connection in Azure Portal
# Portal → App Service → Networking → Hybrid connections → Add
```

### 8. Enable Monitoring

```powershell
# Create Application Insights
az monitor app-insights component create `
    --app "$WEB_APP_NAME-insights" `
    --location $LOCATION `
    --resource-group $RESOURCE_GROUP `
    --application-type web

# Get instrumentation key
$INSIGHTS_KEY = az monitor app-insights component show `
    --app "$WEB_APP_NAME-insights" `
    --resource-group $RESOURCE_GROUP `
    --query "instrumentationKey" -o tsv

# Configure App Service
az webapp config appsettings set `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY
```

## Post-Deployment

### View Logs
```powershell
# Stream logs
az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP

# Download logs
az webapp log download --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

### Test Deployment
```powershell
# Get URL
$APP_URL = "https://$WEB_APP_NAME.azurewebsites.net"
Write-Host "Testing: $APP_URL"

# Open in browser
Start-Process $APP_URL
```

### SSH into Container (for debugging)
```powershell
az webapp ssh --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

## Scaling

### Manual Scaling
```powershell
# Scale up (change plan)
az appservice plan update `
    --name $APP_SERVICE_PLAN `
    --resource-group $RESOURCE_GROUP `
    --sku S1

# Scale out (add instances)
az appservice plan update `
    --name $APP_SERVICE_PLAN `
    --resource-group $RESOURCE_GROUP `
    --number-of-workers 3
```

### Auto-Scaling
```powershell
az monitor autoscale create `
    --name "$APP_SERVICE_PLAN-autoscale" `
    --resource-group $RESOURCE_GROUP `
    --resource $APP_SERVICE_PLAN `
    --resource-type Microsoft.Web/serverfarms `
    --min-count 2 `
    --max-count 5 `
    --count 2

az monitor autoscale rule create `
    --autoscale-name "$APP_SERVICE_PLAN-autoscale" `
    --resource-group $RESOURCE_GROUP `
    --condition "Percentage CPU > 70 avg 5m" `
    --scale out 1
```

## Common Issues & Solutions

### 1. Application Not Starting
**Check logs:**
```powershell
az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

**Common causes:**
- Missing `startup.sh` file
- Incorrect `WEBSITES_PORT` setting
- Missing dependencies in `requirements.txt`

### 2. Static Files Not Loading
**Solution:**
```bash
# SSH into container
az webapp ssh --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP

# Manually collect static files
cd /home/site/wwwroot/monitorportal
python manage.py collectstatic --noinput
```

### 3. Database Connection Issues
**Verify network connectivity:**
- Configure VNet Integration
- Check firewall rules on Oracle database
- Verify credentials in app settings

### 4. 500 Internal Server Error
**Enable detailed errors temporarily:**
```powershell
az webapp config appsettings set `
    --name $WEB_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings DEBUG=True

# Remember to set DEBUG=False after troubleshooting!
```

## Cost Estimation

**Basic Setup (B2 Plan):**
- App Service Plan B2: ~$75/month
- Application Insights: ~$5/month (100GB free)
- Total: ~$80/month

**Production Setup (S1 Plan with auto-scale):**
- App Service Plan S1 (2-5 instances): ~$150-375/month
- Application Insights: ~$10-20/month
- Azure Key Vault: ~$3/month
- Total: ~$163-398/month depending on load

## Security Checklist

- [ ] Update `SECRET_KEY` with a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use Azure Key Vault for sensitive credentials
- [ ] Enable HTTPS only (configured by default in App Service)
- [ ] Configure VNet/Hybrid Connection for database access
- [ ] Enable Application Insights for monitoring
- [ ] Set up automatic backups
- [ ] Configure custom domain with SSL certificate
- [ ] Review and configure CORS settings if using APIs

## Next Steps

1. **Custom Domain**: Configure your own domain name
   ```powershell
   az webapp config hostname add `
       --webapp-name $WEB_APP_NAME `
       --resource-group $RESOURCE_GROUP `
       --hostname "monitorportal.yourdomain.com"
   ```

2. **Deployment Slots**: Set up staging environment
   ```powershell
   az webapp deployment slot create `
       --name $WEB_APP_NAME `
       --resource-group $RESOURCE_GROUP `
       --slot staging
   ```

3. **CI/CD**: Configure Azure DevOps or GitHub Actions
   - See Azure Portal → Deployment Center

4. **Backup Strategy**: Enable automatic backups
   - See DEPLOYMENT.md for detailed instructions

## Resources

- [Full Deployment Guide](./DEPLOYMENT.md#method-4-azure-cloud-deployment)
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Django on Azure Tutorial](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

---

**Last Updated**: April 9, 2026
