"""
Create ADF DSN Automatically via PowerShell
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This script creates an ODBC DSN for Azure Data Factory
Run as Administrator: powershell -ExecutionPolicy Bypass -File create_adf_dsn.ps1
"""

# Configuration - CUSTOMIZE THESE VALUES
$ADF_DSN_Config = @{
    Name = "ADF_Metadata_DSN"
    Driver = "ODBC Driver 17 for SQL Server"
    Description = "Azure Data Factory Metadata Connection"
    
    # Change these values based on your ADF setup
    Server = "your-server.database.windows.net"      # For Azure SQL: *.database.windows.net
                                                       # For On-prem SQL: IP or hostname
    Database = "adf_metadata_db"                      # Change to your actual database
    UserName = "adf_user"                             # Change to your username
    Password = "your_password"                        # Change to your password
    Port = "1433"
    
    # Authentication method
    AuthType = "SQL"                                  # "SQL" or "Windows"
    
    # Encryption options
    Encrypt = "yes"                                   # "yes" for Azure SQL, "optional" for on-prem
    TrustServerCertificate = "no"                     # "no" for Azure SQL, can be "yes" for on-prem
}

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   ADF DSN Setup Script                             ║" -ForegroundColor Cyan
Write-Host "║   Create ODBC Data Source Name for ADF Metadata    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains `
    [Security.Principal.SecurityIdentifier]"S-1-5-32-544")

if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must run as Administrator" -ForegroundColor Red
    Write-Host "   Please open PowerShell as Administrator and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Step 1: Check if driver exists
Write-Host "[1/4] Checking for ODBC Driver 17 for SQL Server..." -ForegroundColor Yellow

$driver = Get-OdbcDriver | Where-Object {$_.Name -eq $ADF_DSN_Config.Driver}

if ($driver) {
    Write-Host "  ✅ Found: $($driver.Name)" -ForegroundColor Green
    Write-Host "     Platform: $($driver.Platform)" -ForegroundColor Gray
} else {
    Write-Host "  ❌ ODBC Driver 17 for SQL Server NOT FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Install the driver:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server" -ForegroundColor Gray
    Write-Host "  2. Run the .msi installer" -ForegroundColor Gray
    Write-Host "  3. Restart PowerShell" -ForegroundColor Gray
    Write-Host "  4. Run this script again" -ForegroundColor Gray
    exit 1
}

# Step 2: Display configuration
Write-Host ""
Write-Host "[2/4] Configuration Details:" -ForegroundColor Yellow
Write-Host "  DSN Name:     $($ADF_DSN_Config.Name)" -ForegroundColor Cyan
Write-Host "  Server:       $($ADF_DSN_Config.Server)" -ForegroundColor Cyan
Write-Host "  Database:     $($ADF_DSN_Config.Database)" -ForegroundColor Cyan
Write-Host "  Username:     $($ADF_DSN_Config.UserName)" -ForegroundColor Cyan
Write-Host "  Port:         $($ADF_DSN_Config.Port)" -ForegroundColor Cyan
Write-Host "  Encrypt:      $($ADF_DSN_Config.Encrypt)" -ForegroundColor Cyan
Write-Host ""

# Step 3: Check if DSN already exists
Write-Host "[3/4] Checking if DSN already exists..." -ForegroundColor Yellow

$existingDsn = Get-OdbcDsn -Name $ADF_DSN_Config.Name -DsnType "System" -ErrorAction SilentlyContinue

if ($existingDsn) {
    Write-Host "  ⚠️  DSN already exists: $($existingDsn.Name)" -ForegroundColor Yellow
    Write-Host "  Removing old configuration..." -ForegroundColor Gray
    
    Remove-OdbcDsn -Name $ADF_DSN_Config.Name -DsnType "System" -Force -ErrorAction SilentlyContinue
    Write-Host "  ✅ Old DSN removed" -ForegroundColor Green
}

# Step 4: Create new DSN
Write-Host ""
Write-Host "[4/4] Creating new ADF DSN..." -ForegroundColor Yellow

try {
    $dsnParams = @{
        Name = $ADF_DSN_Config.Name
        DriverName = $ADF_DSN_Config.Driver
        DsnType = "System"
        SetPropertyValue = @(
            "Server=$($ADF_DSN_Config.Server)",
            "Port=$($ADF_DSN_Config.Port)",
            "Database=$($ADF_DSN_Config.Database)",
            "UID=$($ADF_DSN_Config.UserName)",
            "PWD=$($ADF_DSN_Config.Password)",
            "Encrypt=$($ADF_DSN_Config.Encrypt)",
            "TrustServerCertificate=$($ADF_DSN_Config.TrustServerCertificate)"
        )
        Force = $true
    }
    
    New-OdbcDsn @dsnParams
    
    Write-Host "  ✅ DSN created successfully!" -ForegroundColor Green
    Write-Host "     Name: $($ADF_DSN_Config.Name)" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Failed to create DSN: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Test connection
Write-Host ""
Write-Host "[Testing Connection...]" -ForegroundColor Yellow

try {
    $connStr = "DSN=$($ADF_DSN_Config.Name);"
    $conn = New-Object System.Data.Odbc.OdbcConnection
    $conn.ConnectionString = $connStr
    $conn.Open()
    
    Write-Host "  ✅ Connection Successful!" -ForegroundColor Green
    
    $conn.Close()
}
catch {
    Write-Host "  ❌ Connection Failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Verify server name is correct" -ForegroundColor Gray
    Write-Host "  2. Verify username and password" -ForegroundColor Gray
    Write-Host "  3. Check firewall allows port 1433" -ForegroundColor Gray
    Write-Host "  4. For Azure SQL: Check if your IP is whitelisted" -ForegroundColor Gray
    Write-Host "  5. For on-prem SQL: Check if SQL Server is running and accessible" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Setup Complete!                              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add to Django settings.py:" -ForegroundColor Gray
Write-Host "   ADF_DSN = 'ADF_Metadata_DSN'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test in Python:" -ForegroundColor Gray
Write-Host "   python manage.py shell" -ForegroundColor Gray
Write-Host "   >>> from portal.services.adf_service import ADFDataService" -ForegroundColor Gray
Write-Host "   >>> service = ADFDataService()" -ForegroundColor Gray
Write-Host "   >>> service.test_connection()" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run test script:" -ForegroundColor Gray
Write-Host "   python test_adf_connection.py" -ForegroundColor Gray
Write-Host ""

# Verify DSN creation
Write-Host "Verifying DSN in registry:" -ForegroundColor Gray
$verifyDsn = Get-OdbcDsn -Name $ADF_DSN_Config.Name -DsnType "System" -ErrorAction SilentlyContinue

if ($verifyDsn) {
    Write-Host "  ✅ $($ADF_DSN_Config.Name) is registered and ready to use" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Could not verify DSN creation" -ForegroundColor Yellow
}
