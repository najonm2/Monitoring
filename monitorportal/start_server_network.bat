@echo off
REM Start Django server accessible from network
echo ========================================
echo Starting PASE Monitor Portal
echo Accessible at: http://10.161.206.34:8000
echo ========================================
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
