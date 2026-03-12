# Start Django server accessible from network
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting PASE Monitor Portal" -ForegroundColor Green
Write-Host "Accessible at: http://10.161.206.34:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment and start server
& .\.venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
