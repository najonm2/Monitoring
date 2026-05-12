# Login-First Authentication System

## Overview
Implemented a mandatory login system where ALL users must authenticate before accessing the portal. Access level is determined by Informatica PowerCenter permissions.

## Authentication Flow

```
1. User opens portal (any URL)
   ↓
2. Redirected to /informatica/login/
   ↓
3. Enter CUID + LDAP Password
   ↓
4. System attempts Informatica authentication
   ↓
5a. ✅ SUCCESS → Full Access           5b. ❌ FAIL → Read-Only Access
    - Can restart workflows                - Can view reports
    - Can stop workflows                   - Can view dashboards
    - Can schedule workflows               - Cannot manage workflows
    - Can check workflow status            - Informatica buttons disabled
   ↓                                      ↓
6. Home page with username displayed at top
   ↓
7. Access-appropriate features enabled
```

## User Types

### Full Access Users (Prod Support)
- **Authentication**: Informatica credentials succeed
- **Permissions**: Complete workflow management
- **Features**: Restart, stop, schedule, unschedule, status check
- **Badge**: Green "✅ Full Access" banner

### Read-Only Users (Developers)
- **Authentication**: Informatica credentials fail, but login still allowed
- **Permissions**: View-only access
- **Features**: Dashboards, reports, metrics (no workflow management)
- **Badge**: Blue "👁️ Read-Only Access" banner

## Key Files Modified

### 1. informatica_login.html
- Removed guest option
- Single login form (mandatory)
- Shows access level info

### 2. informatica_credentials_views.py - informatica_login()
- Tries Informatica authentication
- Success → `has_informatica_access=True`, stores credentials
- Fail → `has_informatica_access=False`, `access_level='readonly'`
- Both cases → User logged into portal

### 3. views.py - home() & dashboards()
- Check `portal_logged_in` session
- Redirect to /informatica/login/ if not logged in
- Pass access level to templates

### 4. context_processors.py
- Globally provides `user_display` (username in header)
- Globally provides `has_informatica_access`
- Globally provides `access_level`

### 5. informatica_auth.py - informatica_credentials_required()
- Checks `has_informatica_access` instead of credentials
- Returns 403 for read-only users
- Redirects to /informatica/guest-restricted/

### 6. api_views.py - get_informatica_credentials_from_session()
- Added access level check
- Returns None if user doesn't have Informatica access

## Session Variables

| Variable | Values | Purpose |
|----------|--------|---------|
| `portal_logged_in` | True/False | User authenticated with portal |
| `has_informatica_access` | True/False | User has Informatica permissions |
| `access_level` | 'full'/'readonly' | Access level indicator |
| `display_username` | String (CUID) | Username for display |
| `informatica_username` | String | Stored Informatica CUID (full access only) |
| `informatica_password` | Encrypted string | Stored password (full access only) |
| `login_warning` | String | Warning message for first login (read-only) |

## UI Changes

### Header (All Pages)
- Shows username: `{{ user_display }}`
- Example: "AB64033"

### Home Page
**Full Access Users:**
```
✅ Full Access — You can restart, stop, and schedule Informatica workflows
                                                                      [Logout]
```

**Read-Only Users:**
```
👁️ Read-Only Access — You can view reports and dashboards. Informatica workflow actions are disabled.
                                                                              [Logout & Retry]
```

**Read-Only First Login (Shows once):**
```
⚠️ Read-Only Access Mode

You have been logged in with read-only access. Informatica authentication failed: [error message]. 
You can view reports and dashboards, but cannot perform workflow operations.
```

### Restricted Access Page
When read-only user tries to access Informatica features:
- Shows `/informatica/guest-restricted/`
- Lists what requires full access
- Lists what's available in read-only
- Button: "Logout & Login with Different Credentials"

## Testing Scenarios

### Test 1: Full Access User (Prod Support)
1. Open http://127.0.0.1:8000/
2. Enter valid Informatica CUID + password
3. ✅ See green "Full Access" banner
4. ✅ Username shows in header
5. ✅ Can access /informatica/manual-restart/
6. ✅ Can restart workflows

### Test 2: Read-Only User (Developer)
1. Open http://127.0.0.1:8000/
2. Enter CUID without Informatica permissions
3. ✅ See warning message about read-only access
4. ✅ See blue "Read-Only Access" banner
5. ✅ Username shows in header
6. ✅ Can view dashboards
7. ❌ Cannot access /informatica/manual-restart/ (redirected to restricted page)
8. ❌ Informatica API calls return 403

### Test 3: Invalid Credentials
1. Open http://127.0.0.1:8000/
2. Enter wrong password
3. ✅ Still logged in with read-only access
4. ✅ See warning about connection error
5. ✅ Can view reports

### Test 4: Direct URL Access (Not Logged In)
1. Open http://127.0.0.1:8000/dashboards/
2. ✅ Redirected to /informatica/login/
3. After login → Back to /dashboards/

### Test 5: Logout
1. Click "Logout" link
2. ✅ All session cleared
3. ✅ Redirected to /informatica/login/
4. ✅ Cannot access any portal pages without login

## Security Features

1. **Mandatory Authentication**: No anonymous access
2. **Permission-Based Access**: Informatica features gated by actual permissions
3. **Encrypted Credentials**: Passwords encrypted in session (Fernet)
4. **Session-Only Storage**: Credentials cleared on logout
5. **Graceful Degradation**: Failed auth → Read-only (not blocked)

## API Protection

All Informatica API endpoints return:
- **Full Access**: Normal operation with user's credentials
- **Read-Only**: `403 Forbidden` with message:
  ```json
  {
    "success": false,
    "error": "Informatica access required",
    "message": "This feature requires full Informatica permissions. You are currently in read-only mode.",
    "access_level": "readonly"
  }
  ```

## Benefits

✅ **Security**: Everyone must authenticate  
✅ **Flexibility**: Developers can still view reports  
✅ **Clarity**: Clear access level indicators  
✅ **User-Friendly**: Doesn't block users without permissions  
✅ **Audit Trail**: All actions tied to specific CUID  
✅ **Professional**: Clean, polished UX  

## Migration Notes

If users were previously logged in, they will be redirected to the login page on their next visit. No database changes required - all session-based.
