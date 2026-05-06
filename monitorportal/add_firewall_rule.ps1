# Add Windows Firewall rule for Django server
Write-Host "Adding Windows Firewall rules..." -ForegroundColor Cyan

# Remove existing rules if they exist
netsh advfirewall firewall delete rule name="Django Dev Server Port 8000" 2>$null
netsh advfirewall firewall delete rule name="SMTP Email Outbound" 2>$null

# Add new inbound rule for port 8000 (Django server)
Write-Host "`n1. Adding Django server rule (port 8000)..." -ForegroundColor Yellow
netsh advfirewall firewall add rule name="Django Dev Server Port 8000" dir=in action=allow protocol=TCP localport=8000 profile=any

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Django firewall rule added successfully!" -ForegroundColor Green
} else {
    Write-Host "   ✗ Failed to add Django firewall rule" -ForegroundColor Red
}

# Add new outbound rule for SMTP (port 25)
Write-Host "`n2. Adding SMTP outbound rule (port 25)..." -ForegroundColor Yellow
netsh advfirewall firewall add rule name="SMTP Email Outbound" dir=out action=allow protocol=TCP remoteport=25 profile=any

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ SMTP firewall rule added successfully!" -ForegroundColor Green
} else {
    Write-Host "   ✗ Failed to add SMTP firewall rule" -ForegroundColor Red
}

Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  - Django server accessible at: http://10.161.206.34:8000" -ForegroundColor White
Write-Host "  - Email sending enabled via SMTP (mailrelay.corp.intranet:25)" -ForegroundColor White

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️  Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
}
