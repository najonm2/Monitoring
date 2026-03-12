# Add Windows Firewall rule for Django server
Write-Host "Adding Windows Firewall rule for Django on port 8000..." -ForegroundColor Cyan

# Remove existing rule if it exists
netsh advfirewall firewall delete rule name="Django Dev Server Port 8000" 2>$null

# Add new inbound rule for port 8000
netsh advfirewall firewall add rule name="Django Dev Server Port 8000" dir=in action=allow protocol=TCP localport=8000 profile=any

if ($LASTEXITCODE -eq 0) {
    Write-Host "Firewall rule added successfully!" -ForegroundColor Green
    Write-Host "Django server is now accessible at: http://10.161.206.34:8000" -ForegroundColor Yellow
} else {
    Write-Host "Failed to add firewall rule" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
}
