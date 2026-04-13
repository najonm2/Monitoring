# Azure Deployment Script for PASE Monitor Portal
# This script automates the deployment to Azure App Service

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "rg-monitorportal-prod",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$AppServicePlan = "asp-monitorportal",
    
    [Parameter(Mandatory=$false)]
    [string]$WebAppName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Sku = "B2",
    
    [Parameter(Mandatory=$true)]
    [string]$Level3DbUser,
    
    [Parameter(Mandatory=$true)]
    [string]$Level3DbPassword,
    
    [Parameter(Mandatory=$true)]
    [string]$MapdqprdDbUser,
    
    [Parameter(Mandatory=$true)]
    [string]$MapdqprdDbPassword
)

# Color output functions
function Write-Step {
    param([string]$Message)
    Write-Host "`n===== $Message =====" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

# Generate unique app name if not provided
if ([string]::IsNullOrEmpty($WebAppName)) {
    $RandomSuffix = Get-Random -Minimum 1000 -Maximum 9999
    $WebAppName = "monitorportal-$RandomSuffix"
}

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        PASE Monitor Portal - Azure Deployment Script        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  Resource Group:    $ResourceGroup
  Location:          $Location
  App Service Plan:  $AppServicePlan
  Web App Name:      $WebAppName
  SKU:               $Sku

"@ -ForegroundColor Cyan

# Check prerequisites
Write-Step "Checking Prerequisites"

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    Write-Success "Azure CLI installed: $($azVersion.'azure-cli')"
} catch {
    Write-Error-Message "Azure CLI not found. Installing..."
    winget install Microsoft.AzureCLI
    Write-Success "Azure CLI installed. Please restart your terminal and run this script again."
    exit 1
}

# Check if logged in
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Info "Not logged into Azure. Initiating login..."
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Azure login failed. Exiting."
        exit 1
    }
}

$accountInfo = $account | ConvertFrom-Json
Write-Success "Logged in as: $($accountInfo.user.name)"
Write-Info "Subscription: $($accountInfo.name)"

# Confirm deployment
Write-Host "`nReady to deploy to Azure. This will:" -ForegroundColor Yellow
Write-Host "  1. Create resource group (if not exists)" -ForegroundColor Yellow
Write-Host "  2. Create App Service Plan" -ForegroundColor Yellow
Write-Host "  3. Create Web App" -ForegroundColor Yellow
Write-Host "  4. Configure environment variables" -ForegroundColor Yellow
Write-Host "  5. Deploy application" -ForegroundColor Yellow
Write-Host "`nEstimated cost: ~$75-150/month depending on SKU" -ForegroundColor Yellow

$confirmation = Read-Host "`nDo you want to continue? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Info "Deployment cancelled."
    exit 0
}

# Create Resource Group
Write-Step "Step 1: Creating Resource Group"
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "true") {
    Write-Info "Resource group '$ResourceGroup' already exists"
} else {
    az group create --name $ResourceGroup --location $Location --output none
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Resource group created"
    } else {
        Write-Error-Message "Failed to create resource group"
        exit 1
    }
}

# Create App Service Plan
Write-Step "Step 2: Creating App Service Plan"
$planExists = az appservice plan show --name $AppServicePlan --resource-group $ResourceGroup 2>$null
if ($planExists) {
    Write-Info "App Service Plan '$AppServicePlan' already exists"
} else {
    az appservice plan create `
        --name $AppServicePlan `
        --resource-group $ResourceGroup `
        --sku $Sku `
        --is-linux `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "App Service Plan created"
    } else {
        Write-Error-Message "Failed to create App Service Plan"
        exit 1
    }
}

# Create Web App
Write-Step "Step 3: Creating Web App"
$webAppExists = az webapp show --name $WebAppName --resource-group $ResourceGroup 2>$null
if ($webAppExists) {
    Write-Info "Web App '$WebAppName' already exists"
} else {
    az webapp create `
        --name $WebAppName `
        --resource-group $ResourceGroup `
        --plan $AppServicePlan `
        --runtime "PYTHON:3.11" `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Web App created"
    } else {
        Write-Error-Message "Failed to create Web App"
        exit 1
    }
}

# Configure Application Settings
Write-Step "Step 4: Configuring Application Settings"

# Generate secure secret key
$secretKey = [System.Guid]::NewGuid().ToString() + [System.Guid]::NewGuid().ToString()

az webapp config appsettings set `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --settings `
        DEBUG=False `
        SECRET_KEY="$secretKey" `
        ALLOWED_HOSTS="$WebAppName.azurewebsites.net" `
        LEVEL3_DB_USER="$Level3DbUser" `
        LEVEL3_DB_PASSWORD="$Level3DbPassword" `
        LEVEL3_DB_HOST="10.120.190.4" `
        LEVEL3_DB_PORT="1521" `
        LEVEL3_DB_SERVICE="infr01p_app" `
        MAPDQPRD_DB_USER="$MapdqprdDbUser" `
        MAPDQPRD_DB_PASSWORD="$MapdqprdDbPassword" `
        MAPDQPRD_DB_HOST="RACORAP32-SCAN.CORP.INTRANET" `
        MAPDQPRD_DB_PORT="1521" `
        MAPDQPRD_DB_SERVICE="SVC_IDG01P" `
        WEBSITES_PORT="8000" `
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Success "Application settings configured"
} else {
    Write-Error-Message "Failed to configure application settings"
    exit 1
}

# Deploy Application
Write-Step "Step 5: Deploying Application"

Write-Info "Creating deployment package..."
$projectRoot = Get-Location
$deployZip = Join-Path $projectRoot "deploy.zip"

# Remove old zip if exists
if (Test-Path $deployZip) {
    Remove-Item $deployZip -Force
}

# Create ZIP file
Compress-Archive -Path "$projectRoot\*" -DestinationPath $deployZip -Force

if (Test-Path $deployZip) {
    Write-Success "Deployment package created"
    
    Write-Info "Uploading and deploying to Azure (this may take 5-10 minutes)..."
    az webapp deployment source config-zip `
        --name $WebAppName `
        --resource-group $ResourceGroup `
        --src $deployZip `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Application deployed successfully"
        
        # Clean up
        Remove-Item $deployZip -Force
    } else {
        Write-Error-Message "Deployment failed"
        exit 1
    }
} else {
    Write-Error-Message "Failed to create deployment package"
    exit 1
}

# Create Application Insights (optional)
Write-Step "Step 6: Setting Up Monitoring (Optional)"
$setupMonitoring = Read-Host "Do you want to set up Application Insights monitoring? (yes/no)"

if ($setupMonitoring -eq "yes") {
    $insightsName = "$WebAppName-insights"
    
    # Check if extension is installed
    $extensionInstalled = az extension list --query "[?name=='application-insights'].name" -o tsv
    if (-not $extensionInstalled) {
        Write-Info "Installing Application Insights extension..."
        az extension add --name application-insights --output none
    }
    
    Write-Info "Creating Application Insights..."
    az monitor app-insights component create `
        --app $insightsName `
        --location $Location `
        --resource-group $ResourceGroup `
        --application-type web `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        $insightsKey = az monitor app-insights component show `
            --app $insightsName `
            --resource-group $ResourceGroup `
            --query "instrumentationKey" -o tsv
        
        az webapp config appsettings set `
            --name $WebAppName `
            --resource-group $ResourceGroup `
            --settings APPINSIGHTS_INSTRUMENTATIONKEY=$insightsKey `
            --output none
        
        Write-Success "Application Insights configured"
    }
}

# Summary
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ✓ Deployment Completed Successfully            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Your application is now deployed to Azure!

📝 Deployment Details:
   - Web App URL:        https://$WebAppName.azurewebsites.net
   - Resource Group:     $ResourceGroup
   - App Service Plan:   $AppServicePlan
   - Location:           $Location

📊 Next Steps:
   1. Open your app:     https://$WebAppName.azurewebsites.net
   2. View logs:         az webapp log tail --name $WebAppName --resource-group $ResourceGroup
   3. Monitor:           Azure Portal → $WebAppName → Monitoring
   4. Configure domain:  See docs/AZURE_DEPLOYMENT_QUICK_START.md

⚠️  Important:
   - Database connectivity requires VNet Integration or Hybrid Connection
   - Configure firewall rules to allow Azure IPs
   - Set up backups in Azure Portal

💰 Estimated Monthly Cost:
   - App Service Plan ($Sku): ~$75-150/month
   - Application Insights:     ~$5/month (if enabled)

📚 Documentation:
   - Quick Start:  docs/AZURE_DEPLOYMENT_QUICK_START.md
   - Checklist:    docs/AZURE_DEPLOYMENT_CHECKLIST.md
   - Full Guide:   docs/DEPLOYMENT.md

"@ -ForegroundColor Green

# Open browser
$openBrowser = Read-Host "Do you want to open the app in your browser? (yes/no)"
if ($openBrowser -eq "yes") {
    Start-Process "https://$WebAppName.azurewebsites.net"
}

Write-Success "Deployment script completed!"
