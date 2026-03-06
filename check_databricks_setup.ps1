# PowerShell Helper Script: Check Databricks ODBC Setup
# This script checks if you're ready to configure the DSN

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Databricks ODBC Setup Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: ODBC Driver
Write-Host "[1/4] Checking for Simba Spark ODBC Driver..." -ForegroundColor Yellow
$driver = Get-OdbcDriver | Where-Object {$_.Name -like "*Spark*" -or $_.Name -like "*Databricks*"}

if ($driver) {
    Write-Host "  [OK] FOUND: $($driver.Name) ($($driver.Platform))" -ForegroundColor Green
} else {
    Write-Host "  [X] NOT FOUND: Simba Spark ODBC Driver" -ForegroundColor Red
    Write-Host "     Install it from: Databricks workspace -> JDBC/ODBC tab" -ForegroundColor Yellow
    Write-Host ""
}

# Check 2: DSN Exists
Write-Host "[2/4] Checking for DSN: DataBricks_For_DBX_APP_64B_PRD..." -ForegroundColor Yellow
$dsn = Get-OdbcDsn -Name "DataBricks_For_DBX_APP_64B_PRD" -DsnType "System" -ErrorAction SilentlyContinue

if ($dsn) {
    Write-Host "  [OK] FOUND: DSN is configured" -ForegroundColor Green
    Write-Host "     Name: $($dsn.Name)" -ForegroundColor Gray
    Write-Host "     Type: $($dsn.DsnType)" -ForegroundColor Gray
    Write-Host "     Driver: $($dsn.DriverName)" -ForegroundColor Gray
} else {
    Write-Host "  [i] NOT CONFIGURED YET: DSN needs to be created" -ForegroundColor Cyan
    Write-Host "     Follow SETUP_DSN_STEP_BY_STEP.md guide" -ForegroundColor Yellow
    Write-Host ""
}

# Check 3: Python pyodbc module
Write-Host "[3/4] Checking Python pyodbc module..." -ForegroundColor Yellow
try {
    $pyodbcCheck = python -c "import pyodbc; print(pyodbc.version)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] INSTALLED: pyodbc version $pyodbcCheck" -ForegroundColor Green
    } else {
        Write-Host "  [X] NOT INSTALLED: pyodbc" -ForegroundColor Red
        Write-Host "     Install with: pip install pyodbc" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [X] ERROR: Unable to check pyodbc" -ForegroundColor Red
}

# Check 4: Network connectivity (if DSN exists)
if ($dsn) {
    Write-Host "[4/4] Testing Databricks connection..." -ForegroundColor Yellow
    
    $result = python test_databricks_connection.py 2>&1 | Out-String
    if ($result -match "connection SUCCESSFUL") {
        Write-Host "  [OK] CONNECTION SUCCESSFUL!" -ForegroundColor Green
    } elseif ($result -match "Data source name not found") {
        Write-Host "  [X] DSN EXISTS but not configured properly" -ForegroundColor Red
        Write-Host "     Open odbcad32.exe and reconfigure the DSN" -ForegroundColor Yellow
    } else {
        Write-Host "  [X] CONNECTION FAILED" -ForegroundColor Red
        Write-Host "     Check VPN, token, and connection settings" -ForegroundColor Yellow
    }
} else {
    Write-Host "[4/4] Skipping connection test (DSN not configured)" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($driver -and $dsn -and $result -match "connection SUCCESSFUL") {
    Write-Host "[SUCCESS] ALL CHECKS PASSED! Databricks is ready to use." -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now query Databricks from the portal:" -ForegroundColor White
    Write-Host "  from portal.db.databricks_client import DatabricksClient" -ForegroundColor Gray
    Write-Host "  results = DatabricksClient.fetch_all('SELECT * FROM table')" -ForegroundColor Gray
} elseif (-not $driver) {
    Write-Host "[WARNING] NEXT STEP: Install Simba Spark ODBC Driver" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Get driver from Databricks workspace" -ForegroundColor White
    Write-Host "2. Run the .msi installer" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
} elseif (-not $dsn) {
    Write-Host "[WARNING] NEXT STEP: Configure DSN" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run: Start-Process odbcad32.exe" -ForegroundColor White
    Write-Host "Follow: SETUP_DSN_STEP_BY_STEP.md guide" -ForegroundColor White
} else {
    Write-Host "[WARNING] NEXT STEP: Fix connection issue" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check:" -ForegroundColor White
    Write-Host "  * VPN connection" -ForegroundColor White
    Write-Host "  * Access token is valid" -ForegroundColor White
    Write-Host "  * Server hostname and HTTP path are correct" -ForegroundColor White
}

Write-Host ""
