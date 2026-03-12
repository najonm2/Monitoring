# Allow Port 8000 Through Windows Firewall
# Run this script as Administrator

Write-Host "Adding Windows Firewall rule for Django port 8000..." -ForegroundColor Cyan

# Allow inbound TCP connections on port 8000
New-NetFirewallRule `
    -DisplayName "Django Development Server - Port 8000" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue

if ($?) {
    Write-Host "SUCCESS! Port 8000 is now open for incoming connections." -ForegroundColor Green
    Write-Host ""
    Write-Host "Your portal is now accessible at:" -ForegroundColor Yellow
    Write-Host "  http://10.161.206.34:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "Users can now access it from Lumen VPN!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Could not create firewall rule." -ForegroundColor Red
    Write-Host "Please run this script as Administrator (Right-click > Run as Administrator)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
