# Documentation Index

Welcome to the PASE Monitor Portal documentation. This index helps you find the right documentation for your needs.

## 📖 Documentation Overview

### Getting Started
- **[README.md](../README.md)** - Main project documentation, features, and quick start
- **[QUICK_START.md](../QUICK_START.md)** - Quick installation and setup guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level project overview

### Architecture & Design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design decisions
- **[AI_SYSTEM_README.md](AI_SYSTEM_README.md)** - AI/ML features and capabilities

### Deployment

#### Azure Deployment (Recommended for Production)
| Document | Purpose | Time Required |
|----------|---------|---------------|
| **[AZURE_DEPLOYMENT_SUMMARY.md](AZURE_DEPLOYMENT_SUMMARY.md)** | Complete overview of all Azure options | 5 min read |
| **[AZURE_DEPLOYMENT_QUICK_START.md](AZURE_DEPLOYMENT_QUICK_START.md)** | Fast 5-minute deployment guide | 5-15 min |
| **[AZURE_DEPLOYMENT_CHECKLIST.md](AZURE_DEPLOYMENT_CHECKLIST.md)** | Production deployment checklist | 30-60 min |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** (Method 4) | Comprehensive Azure deployment guide | Reference |

**Quick Start for Azure:**
```powershell
# Use the automated script
.\deploy_to_azure.ps1 -Level3DbUser "user" -Level3DbPassword "pass" -MapdqprdDbUser "user" -MapdqprdDbPassword "pass"
```

#### Other Deployment Methods
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide for all platforms:
  - Method 1: Windows Server with IIS
  - Method 2: Linux Server (Ubuntu/RHEL)
  - Method 3: Docker Container
  - Method 4: Azure Cloud (multiple options)

### Configuration & Setup
- **[INFORMATICA_SETTINGS_EXAMPLE.sh](INFORMATICA_SETTINGS_EXAMPLE.sh)** - Informatica configuration example
- **[DATABRICKS_DSN_SETTINGS.md](../monitorportal/monitorportal/DATABRICKS_DSN_SETTINGS.md)** - Databricks ODBC configuration

### Operations & Maintenance
- **[WORKFLOW_RESTART_GUIDE.md](WORKFLOW_RESTART_GUIDE.md)** - Informatica workflow restart procedures
- **[CLEANUP_PLAN.md](../CLEANUP_PLAN.md)** - Code cleanup and maintenance plan
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

## 🚀 Quick Navigation by Role

### For Developers
1. Start with [README.md](../README.md)
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Check [QUICK_START.md](../QUICK_START.md) for local setup
4. See [AI_SYSTEM_README.md](AI_SYSTEM_README.md) for AI features

### For DevOps Engineers
1. Start with [AZURE_DEPLOYMENT_SUMMARY.md](AZURE_DEPLOYMENT_SUMMARY.md)
2. Use [AZURE_DEPLOYMENT_QUICK_START.md](AZURE_DEPLOYMENT_QUICK_START.md) or [../deploy_to_azure.ps1](../deploy_to_azure.ps1)
3. Follow [AZURE_DEPLOYMENT_CHECKLIST.md](AZURE_DEPLOYMENT_CHECKLIST.md) for production
4. Reference [DEPLOYMENT.md](DEPLOYMENT.md) for detailed configuration

### For System Administrators
1. Review [DEPLOYMENT.md](DEPLOYMENT.md) for your platform
2. Follow platform-specific instructions (Windows/Linux)
3. Configure monitoring and logging
4. Set up backup procedures

### For Operations Team
1. Reference [WORKFLOW_RESTART_GUIDE.md](WORKFLOW_RESTART_GUIDE.md)
2. Monitor application health
3. Review logs and alerts
4. Follow runbook procedures

## 📋 Deployment Decision Tree

```
Need to deploy?
│
├─ Quick test/demo → Use AZURE_DEPLOYMENT_QUICK_START.md + automated script
│
├─ Production deployment
│   │
│   ├─ Cloud (Recommended) → Azure
│   │   ├─ Simple PaaS → AZURE_DEPLOYMENT_QUICK_START.md (App Service)
│   │   ├─ Containers → DEPLOYMENT.md (Method 4B - Container Instances)
│   │   └─ Full control → DEPLOYMENT.md (Method 4C - Virtual Machines)
│   │
│   ├─ On-Premises
│   │   ├─ Windows → DEPLOYMENT.md (Method 1 - IIS)
│   │   └─ Linux → DEPLOYMENT.md (Method 2 - Ubuntu/RHEL)
│   │
│   └─ Containers → DEPLOYMENT.md (Method 3 - Docker)
│
└─ Local development → QUICK_START.md
```

## 🎯 Common Tasks

### First-Time Setup (Local Development)
1. [README.md](../README.md) - Prerequisites and installation
2. [QUICK_START.md](../QUICK_START.md) - Quick local setup
3. Configure database connections
4. Run development server

### Deploy to Azure (First Time)
1. [AZURE_DEPLOYMENT_SUMMARY.md](AZURE_DEPLOYMENT_SUMMARY.md) - Understand options
2. [AZURE_DEPLOYMENT_QUICK_START.md](AZURE_DEPLOYMENT_QUICK_START.md) - Follow steps
3. Or run [deploy_to_azure.ps1](../deploy_to_azure.ps1) - Automated deployment
4. [AZURE_DEPLOYMENT_CHECKLIST.md](AZURE_DEPLOYMENT_CHECKLIST.md) - Verify deployment

### Deploy to Production (Azure)
1. [AZURE_DEPLOYMENT_CHECKLIST.md](AZURE_DEPLOYMENT_CHECKLIST.md) - Complete checklist
2. [DEPLOYMENT.md](DEPLOYMENT.md#method-4-azure-cloud-deployment) - Detailed guide
3. Configure security (Key Vault, VNet)
4. Set up monitoring and backups
5. Verify all checklist items

### Troubleshooting Deployment
1. Check platform-specific section in [DEPLOYMENT.md](DEPLOYMENT.md)
2. For Azure: See [AZURE_DEPLOYMENT_QUICK_START.md](AZURE_DEPLOYMENT_QUICK_START.md#common-issues--solutions)
3. Review application logs
4. Check [CHANGELOG.md](CHANGELOG.md) for known issues

### Configure Informatica Integration
1. [INFORMATICA_SETTINGS_EXAMPLE.sh](INFORMATICA_SETTINGS_EXAMPLE.sh) - Configuration template
2. [WORKFLOW_RESTART_GUIDE.md](WORKFLOW_RESTART_GUIDE.md) - Workflow operations
3. Update database connection settings

### Work with AI Features
1. [AI_SYSTEM_README.md](AI_SYSTEM_README.md) - AI system overview
2. Configure AI agents
3. Train models
4. Monitor AI predictions

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md | ✅ Current | April 9, 2026 |
| DEPLOYMENT.md | ✅ Current | April 9, 2026 |
| AZURE_DEPLOYMENT_SUMMARY.md | ✅ Current | April 9, 2026 |
| AZURE_DEPLOYMENT_QUICK_START.md | ✅ Current | April 9, 2026 |
| AZURE_DEPLOYMENT_CHECKLIST.md | ✅ Current | April 9, 2026 |
| ARCHITECTURE.md | ✅ Current | Recent |
| PROJECT_SUMMARY.md | ✅ Current | Recent |
| WORKFLOW_RESTART_GUIDE.md | ✅ Current | Recent |

## 🤝 Contributing to Documentation

When updating documentation:
1. Keep the documentation index up to date
2. Update "Last Updated" dates
3. Maintain consistent formatting
4. Add cross-references where helpful
5. Update the decision tree if adding new deployment methods

## 📞 Support

- **Technical Issues**: IT Support Team
- **Database Access**: DBA Team
- **Application Owner**: PASE Team
- **Azure Support**: Azure Portal → Help + Support

## 🔗 External Resources

### Azure Documentation
- [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)
- [Azure Monitor](https://docs.microsoft.com/en-us/azure/azure-monitor/)

### Django Documentation
- [Django Project](https://www.djangoproject.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

### Python Documentation
- [Python oracledb](https://python-oracledb.readthedocs.io/)
- [Gunicorn](https://docs.gunicorn.org/)

---

**Last Updated**: April 9, 2026

For questions or suggestions about documentation, contact the PASE Team.
