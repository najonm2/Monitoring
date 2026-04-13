# Azure Deployment Checklist

Use this checklist to ensure successful deployment to Azure App Service.

## Pre-Deployment

### 1. Prerequisites
- [ ] Azure subscription with appropriate permissions
- [ ] Azure CLI installed (`winget install Microsoft.AzureCLI`)
- [ ] Logged into Azure (`az login`)
- [ ] Project source code accessible
- [ ] Oracle database credentials collected
- [ ] Database firewall rules documented

### 2. Azure Resources Planning
- [ ] Decided on Azure region (e.g., eastus, westus, etc.)
- [ ] Determined App Service Plan tier (B1/B2 for dev, S1+ for prod)
- [ ] Chose unique web app name (must be globally unique)
- [ ] Resource group name selected
- [ ] Decided on networking approach (VNet/Hybrid Connection/Public)

### 3. Project Preparation
- [ ] Created `startup.sh` file
- [ ] Created `.deployment` file
- [ ] Updated `requirements.txt` with gunicorn and whitenoise
- [ ] Updated `settings.py` with Azure configuration
- [ ] Tested project locally
- [ ] All dependencies installed and tested

## Deployment Steps

### 4. Create Azure Infrastructure
- [ ] Created resource group
  ```powershell
  az group create --name <name> --location <region>
  ```
- [ ] Created App Service Plan
  ```powershell
  az appservice plan create --name <plan> --resource-group <rg> --sku B2 --is-linux
  ```
- [ ] Created Web App
  ```powershell
  az webapp create --name <app> --resource-group <rg> --plan <plan> --runtime "PYTHON:3.11"
  ```

### 5. Configure Application Settings
- [ ] Set `DEBUG=False`
- [ ] Set `SECRET_KEY` (random, secure value)
- [ ] Set `ALLOWED_HOSTS` (web app hostname)
- [ ] Set `WEBSITES_PORT=8000`
- [ ] Set `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
- [ ] Set Oracle Level3 database credentials:
  - [ ] `LEVEL3_DB_USER`
  - [ ] `LEVEL3_DB_PASSWORD`
  - [ ] `LEVEL3_DB_HOST`
  - [ ] `LEVEL3_DB_PORT`
  - [ ] `LEVEL3_DB_SERVICE`
- [ ] Set Oracle MAPDQPRD database credentials:
  - [ ] `MAPDQPRD_DB_USER`
  - [ ] `MAPDQPRD_DB_PASSWORD`
  - [ ] `MAPDQPRD_DB_HOST`
  - [ ] `MAPDQPRD_DB_PORT`
  - [ ] `MAPDQPRD_DB_SERVICE`

### 6. Deploy Application
- [ ] Created deployment package (ZIP or Git)
- [ ] Deployed to Azure
- [ ] Verified deployment successful (check logs)
- [ ] Waited for deployment to complete (~5-10 minutes)

### 7. Configure Networking (if needed)
- [ ] Configured VNet Integration (for databases in Azure VNet)
- [ ] Configured Hybrid Connection (for on-premises databases)
- [ ] Updated database firewall rules to allow Azure IPs
- [ ] Tested database connectivity from Azure

## Post-Deployment

### 8. Verification
- [ ] Web app URL accessible (https://<app-name>.azurewebsites.net)
- [ ] Homepage loads correctly
- [ ] Static files (CSS, JS) loading properly
- [ ] Dashboard pages accessible
- [ ] Database queries returning data
- [ ] No 500/404 errors in critical pages
- [ ] Application logs show no critical errors

### 9. Monitoring Setup
- [ ] Created Application Insights resource
- [ ] Configured App Service to use Application Insights
- [ ] Verified telemetry data flowing
- [ ] Set up availability tests
- [ ] Configured alert rules for errors/performance

### 10. Security Configuration
- [ ] Verified `DEBUG=False` in production
- [ ] HTTPS enforced (enabled by default)
- [ ] Secrets moved to Azure Key Vault (optional but recommended)
- [ ] Reviewed and configured CORS settings
- [ ] Configured managed identity (if using)
- [ ] Reviewed authentication settings
- [ ] Configured IP restrictions (if needed)

### 11. Performance Optimization
- [ ] Verified static files served via WhiteNoise
- [ ] Enabled response compression
- [ ] Configured caching (if applicable)
- [ ] Reviewed database connection pooling
- [ ] Tested application performance under load

### 12. Backup and Recovery
- [ ] Configured automatic backups
- [ ] Set backup schedule (daily recommended)
- [ ] Set retention period (30 days recommended)
- [ ] Created initial manual backup
- [ ] Documented backup restoration procedure
- [ ] Tested backup restoration (in staging)

## Optional Enhancements

### 13. Advanced Configuration
- [ ] Configured custom domain
- [ ] Configured SSL certificate for custom domain
- [ ] Set up deployment slots (staging, production)
- [ ] Configured auto-scaling rules
- [ ] Set up Azure Front Door (CDN/WAF)
- [ ] Configured Azure Traffic Manager (multi-region)

### 14. CI/CD Setup
- [ ] Configured CI/CD pipeline (Azure DevOps or GitHub Actions)
- [ ] Set up automated testing
- [ ] Configured deployment approval gates
- [ ] Tested automated deployment workflow

### 15. Documentation
- [ ] Documented deployment process
- [ ] Created runbook for common issues
- [ ] Documented rollback procedure
- [ ] Created architecture diagram
- [ ] Documented all environment variables
- [ ] Created troubleshooting guide

## Ongoing Maintenance

### Weekly Tasks
- [ ] Review application logs
- [ ] Check Application Insights for errors
- [ ] Monitor resource utilization
- [ ] Review security alerts

### Monthly Tasks
- [ ] Review and update dependencies
- [ ] Test backup restoration
- [ ] Review and optimize costs
- [ ] Check for Azure service updates
- [ ] Review security recommendations

### Quarterly Tasks
- [ ] Perform security audit
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Review and update documentation

## Troubleshooting Checklist

### If Application Won't Start
- [ ] Check application logs (`az webapp log tail`)
- [ ] Verify `startup.sh` exists and is executable
- [ ] Verify `WEBSITES_PORT` is set to 8000
- [ ] Check all dependencies in `requirements.txt`
- [ ] Verify Python runtime version matches

### If Static Files Not Loading
- [ ] Check WhiteNoise is in MIDDLEWARE
- [ ] Verify `STATIC_ROOT` is configured
- [ ] Run `python manage.py collectstatic` manually
- [ ] Check Application Insights for 404 errors

### If Database Connection Fails
- [ ] Verify all database credentials are correct
- [ ] Check VNet Integration or Hybrid Connection
- [ ] Verify database firewall rules
- [ ] Check NSG (Network Security Group) rules
- [ ] Test connection from Azure Portal (Cloud Shell)

### If Performance Issues
- [ ] Check Application Insights performance metrics
- [ ] Review database query performance
- [ ] Check App Service Plan resources (CPU, memory)
- [ ] Enable caching
- [ ] Consider scaling up/out

## Emergency Contacts

- **Azure Support**: Portal → Help + Support
- **Database Team**: [Insert contact]
- **Application Owner**: [Insert contact]
- **DevOps Team**: [Insert contact]

## Useful Commands Reference

```powershell
# View logs
az webapp log tail --name <app> --resource-group <rg>

# Restart app
az webapp restart --name <app> --resource-group <rg>

# SSH into container
az webapp ssh --name <app> --resource-group <rg>

# Download logs
az webapp log download --name <app> --resource-group <rg>

# View app settings
az webapp config appsettings list --name <app> --resource-group <rg>

# Deployment status
az webapp deployment list-publishing-credentials --name <app> --resource-group <rg>

# Scale up
az appservice plan update --name <plan> --resource-group <rg> --sku S1

# Scale out
az appservice plan update --name <plan> --resource-group <rg> --number-of-workers 3
```

## Rollback Procedure

If deployment fails or issues arise:

1. **Immediate rollback via deployment slot**:
   ```powershell
   az webapp deployment slot swap --name <app> --resource-group <rg> --slot staging --action swap
   ```

2. **Revert to previous version**:
   ```powershell
   # List deployment logs
   az webapp deployment list --name <app> --resource-group <rg>
   
   # Restore from backup
   az webapp config backup restore --backup-name <backup> --name <app> --resource-group <rg>
   ```

3. **Manual rollback**:
   - Deploy previous working version from Git/ZIP
   - Revert database migrations if needed
   - Clear application cache

## Success Criteria

Your deployment is successful when:
- ✅ Application accessible via Azure URL
- ✅ All pages load without errors
- ✅ Database connections working
- ✅ Static files served correctly
- ✅ No critical errors in logs
- ✅ Application Insights showing telemetry
- ✅ Monitoring alerts configured
- ✅ Backups running successfully
- ✅ Performance meets requirements
- ✅ Security best practices implemented

---

**Last Updated**: April 9, 2026
