@echo off
echo ============================================================
echo   INFORMATICA MONITORING PORTAL - DATA SOURCE CHECKER
echo ============================================================
echo.

echo Checking Oracle Database Connection...
python test_oracle.py
echo.

echo ============================================================
echo Testing API Endpoint...
echo ============================================================
curl http://localhost:8000/api/reports/level3/lvl3-failed-job-status/ >api_response.json 2>nul
if %errorlevel% == 0 (
    echo [32mAPI Response saved to: api_response.json[0m
    echo.
    echo Open api_response.json to see:
    echo   - "source": "oracle_database" ^(real data^) or "mock_data"
    echo   - "data": array of records
    echo   - "summary": statistics
    echo.
) else (
    echo [31mERROR: Could not connect to API[0m
    echo Make sure server is running: python manage.py runserver
)

echo ============================================================
echo Quick View Browser Test
echo ============================================================
echo Opening portal in browser...
start http://localhost:8000/dashboards/level3/
echo.
echo Click VIEW on any report to see data
echo Press F12 and check Network tab to see "source" field
echo.

pause
