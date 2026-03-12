# Azure Dev Tunnels Setup Guide

## Installation

```powershell
# Install Azure CLI (if not already installed)
winget install Microsoft.AzureCLI

# Install dev tunnels extension
az extension add --name dev-tunnels
```

## Usage

### Start Django Server
```powershell
cd monitorportal
python manage.py runserver 8000
```

### Create Tunnel (in another terminal)
```powershell
# Login to Azure (first time only)
az login

# Create tunnel
az dev-tunnels create --name pase-portal
az dev-tunnels add-port --tunnel-name pase-portal --port 8000
az dev-tunnels connect --tunnel-name pase-portal

# Get public URL
az dev-tunnels show --tunnel-name pase-portal
```

### Share URL
The output will show a public URL like:
```
https://pase-portal-xyz.devtunnels.ms
```

Share this URL with stakeholders.

## Advantages
- ✅ Microsoft-owned (likely whitelisted by Lumen)
- ✅ Enterprise-grade security
- ✅ Free with Azure account
- ✅ Persistent tunnel names
- ✅ Better integration with Microsoft ecosystem

## Cleanup
```powershell
# Stop tunnel
Press Ctrl+C

# Delete tunnel (optional)
az dev-tunnels delete --tunnel-name pase-portal
```
