# PASE Monitor Portal - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Python Dependencies
```powershell
cd c:\Users\ab64033\source\repos\infa_monitor_portal
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Configure Database (IMPORTANT!)

Create a file `monitorportal/portal/db/db_credentials.py`:

```python
# Level3 Database (INFA_PCREPO)
LEVEL3_DB = {
    'user': 'your_username',
    'password': 'your_password',
    'host': '10.120.190.4',
    'port': 1521,
    'service_name': 'infr01p_app'
}

# MAPDQPRD Database (MDM/ERP/ADF)
MAPDQPRD_DB = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'RACORAP32-SCAN.CORP.INTRANET',
    'port': 1521,
    'service_name': 'SVC_IDG01P'
}
```

⚠️ **Add `db_credentials.py` to `.gitignore`** - Never commit passwords!

### Step 3: Run the Server
```powershell
cd monitorportal
python manage.py runserver
```

Visit: **http://localhost:8000**

---

## 📊 Application Features

### Available Dashboards

1. **Level3 - Failed Jobs with Error**
   - Shows jobs that failed in the last 24 hours
   - Displays error messages and durations
   - Auto-refresh: 5 minutes

2. **Level3 - Long Running Sessions**
   - Identifies sessions running longer than usual
   - Compares against 7-day average
   - Helps identify performance issues

3. **MDM - Job Status**
   - Monitors 17 critical MDM assets
   - Real-time status updates
   - Tracks: RUNNING, SUCCESS, FAILED, WARNING

4. **ERP - Job Status**
   - Tracks ERP integrations
   - Location-specific monitoring
   - PST timezone display

---

## 🎨 UI Customization

All visual styles are in: `portal/static/portal/professional_lumen.css`

### Current Color Scheme
- **Header**: Solid Orange (#FF8C00)
- **Navigation**: Blue to Orange gradient
- **Buttons**: Orange to Blue gradient
- **Logo**: White box with Orange "L"

### To Change Colors

Edit the `:root` variables:
```css
:root {
    --lumen-primary: #FF8C00;        /* Main orange */
    --lumen-accent: #4169E1;         /* Royal blue */
    --lumen-accent-light: #1E90FF;   /* Dodger blue */
}
```

---

## 🔧 Common Tasks

### Add a New Data Source

1. **Update** `portal/services/level3_service.py`:
```python
def get_new_data():
    query = """
        SELECT column1, column2, column3
        FROM your_table
        WHERE condition = 'value'
    """
    return fetch_all_mapdqprd(query)  # or fetch_all() for Level3
```

2. **Add API Endpoint** in `portal/api_views.py`:
```python
elif report_id == 'new_report':
    data = get_new_data()
```

3. **Register Report** in `portal/ssrs_registry.py`:
```python
{
    'id': 'new_report',
    'name': 'New Report Name',
    'api_endpoint': '/api/app/new_report/',
    'columns': ['Column1', 'Column2', 'Column3']
}
```

### Test Database Connection
```powershell
cd monitorportal
python -c "from portal.db.oracle_client import fetch_all; print(fetch_all('SELECT 1 AS test FROM DUAL'))"
```

Expected output: `[{'test': 1}]`

### View All Available Reports
Visit: **http://localhost:8000/dashboards/**

---

## 🐛 Troubleshooting

### "Cannot connect to database"
- Check VPN connection
- Verify database credentials
- Test with `tnsping <service_name>`

### "ModuleNotFoundError"
```powershell
pip install django python-oracledb
```

### "No data showing in tables"
- Check browser console (F12) for JavaScript errors
- Verify API endpoint returns data: `/api/level3/failed-with-error/`
- Check Django logs in terminal

### "Static files not loading"
```powershell
python manage.py collectstatic
```

---

## 📱 Browser Compatibility

✅ **Supported Browsers:**
- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

---

## 🔒 Security Best Practices

1. ✅ Use environment variables for passwords
2. ✅ Set `DEBUG = False` in production
3. ✅ Configure `ALLOWED_HOSTS` properly
4. ✅ Use HTTPS in production
5. ✅ Rotate database passwords regularly
6. ✅ Limit database user permissions (read-only when possible)

---

## 📞 Getting Help

### Check Logs
Django logs appear in the terminal where you ran `runserver`

### Check API Responses
- Open browser DevTools (F12)
- Go to Network tab
- Reload page
- Click on API requests to see responses

### Database Query Testing
```python
python manage.py shell

from portal.services.level3_service import *
data = get_level3_failed_with_error()
print(f"Found {len(data)} records")
print(data[0])  # See first record structure
```

---

## 🎯 Next Steps

1. ✅ Verify all dashboards are working
2. ⏳ Add ADF database connection (when credentials available)
3. ⏳ Set up automated alerts for critical failures
4. ⏳ Add export to Excel functionality
5. ⏳ Implement user authentication
6. ⏳ Configure production deployment

---

**Need more help?** Refer to the main [README.md](README.md) for detailed documentation.
