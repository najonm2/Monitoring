# PASE Monitor Portal

## Project Overview

The **PASE Monitor Portal** is an enterprise-grade Django web application designed to monitor and track Informatica jobs across multiple databases and applications. It provides real-time insights into job statuses, performance metrics, and error tracking with a modern, professional user interface.

## Features

### Multi-Application Monitoring
- **Level3**: Failed jobs with errors and long-running session tracking
- **MDM (Master Data Management)**: Asset monitoring with job status tracking
- **ERP (Enterprise Resource Planning)**: Location-based job monitoring with timezone support
- **ADF (Azure Data Factory)**: Pipeline run status and failure tracking (configurable)

### Key Capabilities
✅ Real-time database connectivity to Oracle databases  
✅ REST API architecture for responsive data loading  
✅ Professional Lumen-inspired UI with custom branding  
✅ Dynamic dashboard with status badges and metrics  
✅ Sortable and filterable data tables  
✅ Error handling with fallback mock data support  
✅ Responsive design for desktop and mobile devices  

## Technology Stack

### Backend
- **Framework**: Django 6.0
- **Language**: Python 3.x
- **Database Driver**: python-oracledb (Oracle connectivity)
- **Metadata Storage**: SQLite3

### Frontend
- **Template Engine**: Django Templates
- **Styling**: Custom CSS (professional_lumen.css)
- **JavaScript**: Vanilla JS with Fetch API
- **Icons**: Unicode/Emoji icons

### Databases
- **Primary Oracle DB**: INFA_PCREPO (Level3 jobs)
  - Host: 10.120.190.4:1521
  - Service: infr01p_app
  
- **Secondary Oracle DB**: MAPDQPRD (MDM, ERP, ADF)
  - Host: RACORAP32-SCAN.CORP.INTRANET:1521
  - Service: SVC_IDG01P

## Project Structure

```
monitorportal/
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite metadata database
├── monitorportal/               # Main Django project
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI entry point
├── portal/                      # Main application
│   ├── models.py                # Application & Report models
│   ├── views.py                 # View controllers
│   ├── api_views.py             # REST API endpoints
│   ├── urls.py                  # App URL routing
│   ├── context_processors.py   # Template context
│   ├── ssrs_registry.py         # Application registry
│   ├── db/
│   │   └── oracle_client.py     # Oracle database connections
│   ├── services/
│   │   └── level3_service.py    # Business logic & queries
│   ├── sql/
│   │   └── level3_queries.py    # SQL query definitions
│   ├── static/portal/
│   │   └── professional_lumen.css  # UI styles
│   ├── templates/portal/
│   │   ├── layout.html          # Base template
│   │   ├── home.html            # Homepage
│   │   ├── dashboards_home.html # Application selector
│   │   └── dashboard_view.html  # Data display
│   └── templatetags/
│       └── custom_filters.py    # Template utilities
└── .venv/                       # Python virtual environment
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Oracle Instant Client (for database connectivity)
- Network access to Oracle databases

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd infa_monitor_portal
```

### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install django python-oracledb
```

### Step 4: Configure Database Credentials

Edit `portal/db/oracle_client.py` with your database credentials:

```python
# Level3 Database Configuration
DB_CONFIG = {
    'user': 'your_username',
    'password': 'your_password',
    'host': '10.120.190.4',
    'port': 1521,
    'service_name': 'infr01p_app'
}

# MDM/ERP/ADF Database Configuration
MAPDQPRD_DB_CONFIG = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'RACORAP32-SCAN.CORP.INTRANET',
    'port': 1521,
    'service_name': 'SVC_IDG01P'
}
```

### Step 5: Initialize Database
```bash
cd monitorportal
python manage.py migrate
```

### Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Access the portal at: **http://localhost:8000**

## Architecture

### REST API Design

The application uses a modern REST API architecture:

1. **Frontend** (HTML/JavaScript) makes asynchronous requests
2. **API Views** (`api_views.py`) handle endpoints
3. **Service Layer** (`level3_service.py`) contains business logic
4. **Database Layer** (`oracle_client.py`) manages connections

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/level3/failed-with-error/` | GET | Level3 failed jobs with error messages |
| `/api/level3/long-running/` | GET | Level3 long-running sessions |
| `/api/mdm/job-status/` | GET | MDM job status for specific assets |
| `/api/erp/job-status/` | GET | ERP job status with location filtering |
| `/api/adf/run-status/` | GET | ADF pipeline run status (if configured) |
| `/api/adf/failed-jobs/` | GET | ADF failed jobs (if configured) |

### Data Flow

```
User Browser
    ↓ (HTTP Request)
Django Views (views.py)
    ↓ (Renders Template)
HTML Template + JavaScript
    ↓ (Fetch API Call)
API Views (api_views.py)
    ↓ (Calls Service)
Service Layer (level3_service.py)
    ↓ (Executes Query)
Oracle Client (oracle_client.py)
    ↓ (SQL Query)
Oracle Database
```

## Database Queries

### Level3 Queries

#### Failed Jobs with Error
```sql
WITH error_sessions AS (
    SELECT DISTINCT workflow_run_id
    FROM REP_SESS_LOG
    WHERE instance_name = 'IDG01P'
    AND end_time >= SYSDATE - 1
    AND UPPER(task_name) LIKE '%ERROR%'
)
SELECT ...
```

#### Long Running Jobs
```sql
SELECT workflow_name, session_name, 
       ROUND((end_time - start_time) * 24 * 60, 2) as duration_minutes,
       ROUND(AVG(...) * 24 * 60, 2) as avg_duration_minutes
FROM REP_SESS_LOG
WHERE duration_minutes > avg_duration_minutes * 1.5
```

### MDM Queries
- Monitors 17 specific assets from `IICS_CDI_RUN_INFO`
- Tracks: RUNNING, SUCCESS, FAILED, WARNING statuses

### ERP Queries
- Filters 7 specific locations from `IICS_CDI_RUN_INFO`
- Uses PST timezone conversion
- Tracks: CHILD_RUNNING, CHILD_SUSPENDED, SUCCESS statuses

## UI Design

### Color Scheme
- **Main Header**: Solid Orange (#FF8C00)
- **Navigation Bar**: Blue to Orange gradient
- **Buttons**: Orange to Blue gradient
- **Accent Color**: Orange (#FF8C00)
- **Logo**: White background with Orange "L"

### Components
- **Status Badges**: Color-coded (Success=Green, Failed=Red, Running=Blue)
- **Data Tables**: Sortable columns with gradient headers
- **Cards**: Shadow effects with gradient headers
- **Icons**: Gradient backgrounds matching theme

## Configuration

### Adding New Applications

1. Register in `ssrs_registry.py`:
```python
APPLICATIONS = [
    {
        'id': 'your_app',
        'name': 'Your Application',
        'description': 'Description',
        'icon': '🔧',
        'reports': [
            {
                'id': 'report_id',
                'name': 'Report Name',
                'category': 'Monitoring',
                'api_endpoint': '/api/your-app/endpoint/',
                'refresh_interval': 60000
            }
        ]
    }
]
```

2. Add service function in `level3_service.py`:
```python
def get_your_app_data():
    query = "SELECT * FROM your_table"
    return fetch_all_mapdqprd(query)
```

3. Add API endpoint in `api_views.py`:
```python
elif report_id == 'your_report_id':
    data = get_your_app_data()
```

### Environment Variables (Recommended)

For production, use environment variables instead of hardcoded credentials:

```python
import os

DB_CONFIG = {
    'user': os.getenv('ORACLE_USER'),
    'password': os.getenv('ORACLE_PASSWORD'),
    'host': os.getenv('ORACLE_HOST'),
    'port': int(os.getenv('ORACLE_PORT', 1521)),
    'service_name': os.getenv('ORACLE_SERVICE')
}
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Credentials**: Never commit database credentials to version control
2. **Create `.env` file** for sensitive data (add to `.gitignore`)
3. **Django SECRET_KEY**: Change in production and keep secure
4. **DEBUG mode**: Set `DEBUG = False` in production
5. **ALLOWED_HOSTS**: Configure properly for production
6. **Database permissions**: Use read-only accounts where possible

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables for credentials
- [ ] Set up production database (PostgreSQL/MySQL)
- [ ] Configure static files collection
- [ ] Set up WSGI server (Gunicorn/uWSGI)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure backup strategy

### Example Production Command
```bash
gunicorn monitorportal.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Oracle Connection Issues

**Problem**: `ORA-12514: TNS:listener does not currently know of service`

**Solution**: Verify service name using:
```bash
tnsping <service_name>
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'oracledb'`

**Solution**: 
```bash
pip install python-oracledb
```

### Template Rendering Issues

**Problem**: Custom filters not working

**Solution**: Ensure template tags are loaded:
```django
{% load custom_filters %}
```

## Testing

### Test Database Connection
```bash
cd monitorportal
python -c "from portal.db.oracle_client import fetch_all; print(fetch_all('SELECT 1 FROM DUAL'))"
```

### Test Specific Query
```bash
python -c "from portal.services.level3_service import get_level3_failed_with_error; print(len(get_level3_failed_with_error()))"
```

## Maintenance

### Adding New SQL Queries

1. Define query in `sql/level3_queries.py`
2. Create service function in `services/level3_service.py`
3. Add API endpoint in `api_views.py`
4. Register report in `ssrs_registry.py`
5. Test with browser at `/api/your-endpoint/`

### Updating UI Styles

All styles are in `static/portal/professional_lumen.css`:
- Use CSS variables for consistency
- Follow gradient patterns for headers/buttons
- Test responsive behavior on mobile

## Documentation

Additional documentation is available in the `docs/` folder:

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for getting up and running
- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - High-level project overview
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment procedures and guidelines
- **[docs/WORKFLOW_RESTART_GUIDE.md](docs/WORKFLOW_RESTART_GUIDE.md)** - Workflow restart feature documentation
- **[docs/AI_SYSTEM_README.md](docs/AI_SYSTEM_README.md)** - AI/ML features and integration
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history and changes
- **[docs/INFORMATICA_SETTINGS_EXAMPLE.sh](docs/INFORMATICA_SETTINGS_EXAMPLE.sh)** - Configuration examples

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Django logs for error details
3. Verify database connectivity
4. Check Oracle client installation

## License

Internal enterprise application - All rights reserved.

## Credits

- **Framework**: Django Web Framework
- **Database**: Oracle Database
- **Design**: Lumen-inspired professional theme
- **Developer**: PASE Team

---

**Version**: 1.0.0  
**Last Updated**: March 2, 2026  
**Status**: Production Ready
