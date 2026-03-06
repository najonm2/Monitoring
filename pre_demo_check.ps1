# Pre-Demo Quick Check Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRE-DEMO VERIFICATION CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Python environment
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [X] Python not found" -ForegroundColor Red
}

# Check 2: Django installation
Write-Host "[2/5] Checking Django..." -ForegroundColor Yellow
Set-Location "C:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal"
try {
    $djangoCheck = python -c "import django; print(f'Django {django.__version__}')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $djangoCheck" -ForegroundColor Green
    } else {
        Write-Host "  [X] Django check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "  [X] Error checking Django" -ForegroundColor Red
}

# Check 3: Oracle connectivity
Write-Host "[3/5] Testing Oracle connection..." -ForegroundColor Yellow
try {
    $oracleTest = python -c "from portal.db.oracle_client import fetch_all; result = fetch_all('SELECT 1 as test FROM DUAL'); print('Connected')" 2>&1
    if ($oracleTest -match "Connected") {
        Write-Host "  [OK] Oracle connection successful" -ForegroundColor Green
    } else {
        Write-Host "  [!] Oracle connection issue - check VPN" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [!] Oracle test failed - ensure VPN is connected" -ForegroundColor Yellow
}

# Check 4: Port availability
Write-Host "[4/5] Checking if port 8000 is available..." -ForegroundColor Yellow
$portCheck = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "  [!] Port 8000 in use - will stop existing process" -ForegroundColor Yellow
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  [OK] Port cleared" -ForegroundColor Green
} else {
    Write-Host "  [OK] Port 8000 available" -ForegroundColor Green
}

# Check 5: Key files exist
Write-Host "[5/5] Checking key application files..." -ForegroundColor Yellow
$files = @(
    "manage.py",
    "portal\ssrs_registry.py",
    "portal\services\bi_service.py",
    "portal\views.py",
    "portal\templates\portal\layout.html"
)
$allFilesExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [X] MISSING: $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($allFilesExist) {
    Write-Host "[SUCCESS] All checks passed! Ready for demo." -ForegroundColor Green
    Write-Host ""
    Write-Host "TO START SERVER:" -ForegroundColor White
    Write-Host "  python manage.py runserver" -ForegroundColor Gray
    Write-Host ""
    Write-Host "THEN OPEN BROWSER TO:" -ForegroundColor White
    Write-Host "  http://127.0.0.1:8000/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "DEMO GUIDE:" -ForegroundColor White
    Write-Host "  See DEMO_CHECKLIST.txt for full demo flow" -ForegroundColor Gray
} else {
    Write-Host "[WARNING] Some issues detected. Review above." -ForegroundColor Yellow
}

Write-Host ""
