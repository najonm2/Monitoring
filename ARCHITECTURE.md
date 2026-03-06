# PASE Monitoring Portal - System Architecture

## 🏗️ High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER ACCESS LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │   Browser    │  │   Browser    │  │   Browser    │                      │
│  │  (Chrome)    │  │  (Firefox)   │  │   (Edge)     │                      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                      │
│         │                 │                  │                               │
│         └─────────────────┴──────────────────┘                               │
│                           │                                                  │
│                    HTTPS/HTTP Requests                                       │
└───────────────────────────┼──────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────────────────┐
│                     WEB SERVER LAYER (IIS/Development)                       │
│                           │                                                  │
│  ┌────────────────────────▼─────────────────────────┐                       │
│  │         SSO/Windows Authentication                │                       │
│  │    (Captures REMOTE_USER → CUID: AB64033)        │                       │
│  └────────────────────────┬─────────────────────────┘                       │
│                           │                                                  │
│  ┌────────────────────────▼─────────────────────────┐                       │
│  │         Django Application Server                 │                       │
│  │              (Python 3.x)                         │                       │
│  │                                                   │                       │
│  │  ┌─────────────────────────────────────────┐    │                       │
│  │  │       URL Router (urls.py)              │    │                       │
│  │  │  /dashboards/level3/                    │    │                       │
│  │  │  /dashboards/mdm/                       │    │                       │
│  │  │  /dashboards/erp/                       │    │                       │
│  │  │  /reports/<slug>/view/                  │    │                       │
│  │  └─────────────────┬───────────────────────┘    │                       │
│  │                    │                             │                       │
│  │  ┌─────────────────▼───────────────────────┐    │                       │
│  │  │    Views Layer (views.py)               │    │                       │
│  │  │  - home()                               │    │                       │
│  │  │  - app_dashboards()                     │    │                       │
│  │  │  - report_view()                        │    │                       │
│  │  └─────────────────┬───────────────────────┘    │                       │
│  │                    │                             │                       │
│  │  ┌─────────────────▼───────────────────────┐    │                       │
│  │  │  Service Layer (services/)              │    │                       │
│  │  │  - level3_service.py                    │    │                       │
│  │  │    * get_level3_jobs_last_7_days()     │    │                       │
│  │  │    * get_level3_failed_with_error()    │    │                       │
│  │  │  - mdm_service.py                       │    │                       │
│  │  │  - erp_service.py                       │    │                       │
│  │  └─────────────────┬───────────────────────┘    │                       │
│  │                    │                             │                       │
│  │  ┌─────────────────▼───────────────────────┐    │                       │
│  │  │  Database Client (db/oracle_client.py)  │    │                       │
│  │  │  - fetch_all() with LOB support         │    │                       │
│  │  │  - Connection pooling                    │    │                       │
│  │  │  - 10MB LONG field reading               │    │                       │
│  │  └─────────────────┬───────────────────────┘    │                       │
│  │                    │                             │                       │
│  └────────────────────┼─────────────────────────────┘                       │
└───────────────────────┼──────────────────────────────────────────────────────┘
                        │
                   SQL Queries
                   (oracledb driver)
                        │
┌───────────────────────┼──────────────────────────────────────────────────────┐
│                  DATA SOURCE LAYER (Oracle Databases)                        │
│                       │                                                      │
│  ┌────────────────────▼────────────────────┐                                │
│  │     REP_DW_ADMIN Schema (Level3)        │                                │
│  │  ┌───────────────────────────────────┐  │                                │
│  │  │  OPB_TASK_INST_RUN Table          │  │                                │
│  │  │  - workflow_name                  │  │                                │
│  │  │  - start_time (DATE)              │  │                                │
│  │  │  - end_time (DATE)                │  │                                │
│  │  │  - task_status (VARCHAR2)         │  │                                │
│  │  │  - run_err_msg (LONG) ← 10MB     │  │                                │
│  │  └───────────────────────────────────┘  │                                │
│  └─────────────────────────────────────────┘                                │
│                                                                              │
│  ┌─────────────────────────────────────────┐                                │
│  │     ICSM Schema (MDM)                   │                                │
│  │  ┌───────────────────────────────────┐  │                                │
│  │  │  app_control_status Table         │  │                                │
│  │  │  - pipeline_name                  │  │                                │
│  │  │  - start_dt (TIMESTAMP)           │  │                                │
│  │  │  - end_dt (TIMESTAMP)             │  │                                │
│  │  │  - status_cd (VARCHAR2)           │  │                                │
│  │  │  Time Zone: MST (GMT-7)           │  │                                │
│  │  └───────────────────────────────────┘  │                                │
│  └─────────────────────────────────────────┘                                │
│                                                                              │
│  ┌─────────────────────────────────────────┐                                │
│  │     ERP Schema                          │                                │
│  │  - Workflow execution tables            │                                │
│  │  - Job status tracking                  │                                │
│  └─────────────────────────────────────────┘                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Architecture

### Request Flow (Level3 Example)

```
1. User Request
   │
   ├─> Browser: GET /dashboards/level3/
   │
   └─> IIS/Server captures REMOTE_USER header (CUID: AB64033)

2. Authentication Middleware
   │
   ├─> DevRemoteUserMiddleware (Development only)
   │   └─> Sets request.META['REMOTE_USER'] = 'AB64033'
   │
   └─> RemoteUserMiddleware (Production)
       └─> Captures SSO CUID from Windows Auth

3. URL Routing
   │
   └─> urls.py: /dashboards/<app_slug>/
       └─> Calls: views.app_dashboards(request, app_slug='level3')

4. View Processing
   │
   ├─> Fetch from SSRS Registry: APPS configuration
   │
   ├─> Call Service Layer:
   │   └─> level3_service.get_level3_jobs_last_7_days_optimized()
   │
   └─> Render template: app_dashboards.html

5. Service Layer (Level3)
   │
   ├─> TODAY Query:
   │   SELECT COUNT(*) WHERE TRUNC(start_time) = TRUNC(SYSDATE)
   │   └─> Executes in ~3-5 seconds
   │
   └─> Historical Queries (Loop 6 times):
       SELECT COUNT(*) WHERE TRUNC(start_time) = TRUNC(SYSDATE) - :days_ago
       └─> Each executes in ~8-12 seconds
       └─> Total: 64-83 seconds (30-40% faster than single GROUP BY)

6. Database Client Layer
   │
   ├─> oracle_client.fetch_all(sql, params)
   │   ├─> cursor.setoutputsize(10000000)  # 10MB for LONG fields
   │   ├─> Execute SQL with parameter binding
   │   └─> LOB Reading:
   │       if hasattr(value, 'read'):
   │           value = value.read()  # Read complete LONG field
   │
   └─> Return: List[Dict] with lowercase column names

7. Template Rendering
   │
   ├─> app_dashboards.html
   │   ├─> Hero section with app info
   │   ├─> Report tiles (clickable)
   │   ├─> 7-Day Insights section (TODAY card + 6-day grid)
   │   └─> Information Guidelines section
   │
   └─> Response: HTML with CSS (#FF6A13 theme)

8. Browser Rendering
   │
   └─> Professional Lumen CSS:
       ├─> Header: #133D3C (Dark Teal)
       ├─> Theme: #FF6A13 (Vibrant Orange)
       ├─> Logo: logo_lumen.jpg (40px height)
       └─> User Display: AB64033 (from REMOTE_USER)
```

---

## 🔧 Technology Stack

### Backend Technologies
```
┌──────────────────────────────────────────────┐
│  Framework: Django 5.1.4                     │
│  Language: Python 3.11+                      │
│  Database Driver: python-oracledb 2.5.0     │
│  Oracle Client: Thick mode with Oracle 21c  │
│  Authentication: SSO via REMOTE_USER header │
└──────────────────────────────────────────────┘
```

### Frontend Technologies
```
┌──────────────────────────────────────────────┐
│  Templating: Django Templates (Jinja2-like) │
│  CSS: Custom Professional Lumen Theme        │
│  Color Scheme:                               │
│    - Primary Header: #133D3C (Dark Teal)    │
│    - Theme Color: #FF6A13 (Vibrant Orange)  │
│  JavaScript: Vanilla JS (modal, formatting) │
│  Icons: Unicode Emoji (📈 🗄️ 🎯)           │
└──────────────────────────────────────────────┘
```

### Database Sources
```
┌──────────────────────────────────────────────┐
│  Database: Oracle 19c/21c Enterprise         │
│  Connection: TNS via tnsnames.ora            │
│  Schemas:                                    │
│    - REP_DW_ADMIN (Level3 workflows)        │
│    - ICSM (MDM pipelines)                   │
│    - ERP schemas (ERP workflows)            │
└──────────────────────────────────────────────┘
```

---

## 🎯 Key Features & Implementation

### 1. Performance Optimization
```
Problem: Single GROUP BY query across 7 days = 91-105 seconds
Solution: 7 separate queries (1 TODAY + 6 historical)
Result: 64-83 seconds (30-40% improvement)

Implementation:
  portal/services/level3_service.py
    └─> get_level3_jobs_last_7_days_optimized()
        ├─> get_level3_jobs_today_only()       # Fast: SYSDATE only
        └─> Loop: get_level3_jobs_single_day(days_ago=1-6)
```

### 2. Oracle LONG Field Handling
```
Problem: Python truncates LONG datatype to ~80 bytes
Solution: Multi-layer approach

Layer 1 (Query):
  SELECT TIR.RUN_ERR_MSG AS error_message
  -- No CAST or DBMS_LOB wrapper

Layer 2 (Python - cursor setup):
  cursor.setoutputsize(10000000)  # 10MB limit

Layer 3 (Python - LOB reading):
  if hasattr(value, 'read'):
      value = value.read()  # Read complete LOB object

Result: Full error messages up to 10MB displayed
```

### 3. Error Message Display UI
```
Feature: "View Full Details" button + Modal

Implementation:
  portal/templates/portal/report_view.html
    └─> formatValue() function
        ├─> Preview: First 80 characters in table
        ├─> Button: "🤖 View Full Details" (if length > 80)
        └─> Modal: Full error message in scrollable dialog

User Experience:
  - Click button → Modal opens with session info + complete error
  - ESC key / Outside click / Close button → Modal closes
  - Mobile responsive
```

### 4. SSO Authentication
```
Development:
  portal/middleware.py
    └─> DevRemoteUserMiddleware
        └─> Sets request.META['REMOTE_USER'] = 'AB64033'

Production:
  IIS Windows Authentication
    └─> Automatically sets REMOTE_USER header
    └─> Django RemoteUserBackend captures CUID

Settings:
  monitorportal/settings.py
    └─> AUTHENTICATION_BACKENDS = [
            'django.contrib.auth.backends.RemoteUserBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]
```

### 5. Color Theme System
```
Main Header (Preserved):
  .top-header: linear-gradient(135deg, #133D3C 0%, #0D2928 100%)

All Other Elements (Unified):
  --lumen-primary: #FF6A13 (Vibrant Orange)
  
Applied to:
  - Navigation bar (solid)
  - Card headers (solid)
  - Tile icons (solid)
  - Feature icons (solid)
  - All buttons and accents (solid)
  - Removed all gradients except main header
```

---

## 📁 Project Structure

```
monitorportal/
├── monitorportal/                  # Project configuration
│   ├── settings.py                # Django settings, DB config
│   ├── urls.py                    # Root URL configuration
│   └── wsgi.py                    # WSGI application entry
│
├── portal/                         # Main application
│   ├── views.py                   # View controllers
│   ├── urls.py                    # App URL patterns
│   ├── models.py                  # Database models (minimal)
│   ├── ssrs_registry.py           # App & report definitions
│   ├── context_processors.py     # Global template context
│   ├── middleware.py              # Dev SSO simulator
│   │
│   ├── db/                        # Database layer
│   │   └── oracle_client.py      # Oracle connection & queries
│   │
│   ├── services/                  # Business logic layer
│   │   └── level3_service.py     # Level3 data queries
│   │
│   ├── sql/                       # SQL query definitions
│   │   └── level3_queries.py     # Level3 SQL statements
│   │
│   ├── templates/portal/          # HTML templates
│   │   ├── layout.html           # Base template
│   │   ├── home.html             # Landing page
│   │   ├── app_dashboards.html   # App dashboard view
│   │   ├── report_view.html      # Report detail view
│   │   └── dashboards_home.html  # All dashboards listing
│   │
│   └── static/portal/             # Static assets
│       ├── professional_lumen.css # Theme CSS (954 lines)
│       └── logo_lumen.jpg        # Lumen logo (3.05 KB)
│
├── db.sqlite3                     # Local dev database
├── manage.py                      # Django management script
├── ARCHITECTURE.md                # This file
└── requirements.txt               # Python dependencies
```

---

## 🔐 Security & Configuration

### Database Configuration
```python
# monitorportal/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Oracle connection via portal/db/oracle_client.py
# Uses environment variables or tnsnames.ora:
#   - TNS_ADMIN path
#   - ORACLE_HOME
#   - Connection string: user/password@TNS_NAME
```

### Authentication Backends
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend',  # SSO
    'django.contrib.auth.backends.ModelBackend',       # Fallback
]

MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'portal.middleware.DevRemoteUserMiddleware',        # DEV ONLY
    'django.contrib.auth.middleware.RemoteUserMiddleware',
]
```

### Production Deployment Checklist
```bash
# 1. Remove development middleware
# Edit settings.py, remove:
#   'portal.middleware.DevRemoteUserMiddleware'

# 2. Set DEBUG = False
DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']

# 3. Configure static files
python manage.py collectstatic

# 4. Set up IIS with:
#   - Windows Authentication enabled
#   - ISAPI-WSGI or HttpPlatformHandler
#   - REMOTE_USER header passthrough

# 5. Configure Oracle Instant Client
#   - Set ORACLE_HOME
#   - Configure tnsnames.ora
#   - Test connection: python manage.py shell
```

---

## 📈 Performance Metrics

### Query Performance
```
Level3 7-Day Insights:
  OLD (Single GROUP BY):    91-105 seconds
  NEW (7 Separate Queries): 64-83 seconds
  Improvement:              30-40% faster

Breakdown:
  - TODAY query:            3-5 seconds
  - Each historical query:  8-12 seconds × 6
  - Total:                  64-83 seconds
  - Parallel potential:     Consider async queries in future
```

### Error Message Handling
```
LONG Field Reading:
  Default (truncated):      ~80 bytes
  With setoutputsize:       10 MB (10,000,000 bytes)
  Read success rate:        100% for errors < 10MB
```

---

## 🎨 UI/UX Design Principles

1. **Professional Theme**
   - Dark teal header (#133D3C) - Corporate, stable
   - Vibrant orange theme (#FF6A13) - Energy, alertness
   - Clean white backgrounds - Clarity, readability

2. **Information Hierarchy**
   - Hero sections with app context
   - Report tiles (large, clickable)
   - 7-Day insights (TODAY emphasized)
   - Information guidelines (bottom reference)

3. **Responsive Design**
   - Grid layouts with auto-fit
   - Mobile-friendly navigation
   - Touch-friendly button sizes
   - Readable font sizes (14px-48px)

4. **User Feedback**
   - Hover effects on all interactive elements
   - Loading states (can be added)
   - Error messages with full details button
   - Clear visual hierarchy

---

## 🔄 Future Enhancements

1. **Performance**
   - Implement async database queries
   - Add Redis caching layer
   - Background job processing (Celery)

2. **Features**
   - Real-time refresh (WebSockets)
   - Export to Excel/CSV
   - Email alerts for SLA breaches
   - Custom date range selection

3. **Monitoring**
   - Application performance monitoring (APM)
   - Database query logging
   - User activity tracking
   - Error rate monitoring

4. **UI/UX**
   - Dark mode toggle
   - Customizable dashboards
   - Drag-and-drop report organization
   - Advanced filtering and search

---

## 📞 Key Contacts & Resources

- **Developer**: PASE Monitoring Portal Team
- **CUID**: AB64033
- **Database**: Oracle REP_DW_ADMIN, ICSM schemas
- **Server**: IIS with Windows Authentication
- **Repository**: infa_monitor_portal

---

## 📝 Version History

- **v1.0** - Initial portal with Level3 dashboards
- **v1.1** - Performance optimization (7 separate queries)
- **v1.2** - LONG field handling for full error messages
- **v1.3** - Theme update (#FF6A13 vibrant orange)
- **v1.4** - SSO authentication integration
- **v1.5** - Lumen logo integration
- **v1.6** - Information guidelines section
