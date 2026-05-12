# User-Based Informatica Credentials Implementation

## Overview
This implementation replaces hardcoded Informatica credentials with user-specific LDAP credentials, improving security for production deployment.

## How It Works

### 1. **User Authentication Flow**
```
User logs in with SSO/CUID  
           ↓
Lands on home page
           ↓
Sees prominent banner: "Set Up Informatica Access" (if not configured)
           ↓
Clicks "Configure Credentials Now"
           ↓
Enters CUID and LDAP password
           ↓
Credentials tested with Informatica
           ↓
Username and password encrypted & stored in session
           ↓
Redirected back to home/dashboard
           ↓
All Informatica operations use their credentials
```

**Key Improvement:** Credentials requested upfront on home page, not in middle of workflow actions!

### 2. **Security Features**
- ✅ Passwords encrypted using Fernet (symmetric encryption)
- ✅ Encryption key derived from Django SECRET_KEY
- ✅ Credentials stored only in session (not database)
- ✅ Credentials cleared when user logs out
- ✅ Password never stored in plain text

### 3. **Files Created/Modified**

#### New Files:
1. **`portal/informatica_auth.py`** - Credential encryption/storage helper
2. **`portal/informatica_credentials_views.py`** - Credential management views
3. **`portal/templates/portal/informatica_credentials.html`** - Password entry UI

#### Modified Files:
1. **`portal/urls.py`** - Added credential management URLs
2. **`portal/services/informatica_restart_service.py`** - Accepts username/password parameters
3. **`portal/api_views.py`** - Uses session credentials instead of settings

### 4. **New URLs**
- `/informatica/credentials/` - Password entry page
- `/api/informatica/credentials/check/` - Check if credentials stored
- `/api/informatica/credentials/clear/` - Clear stored credentials

### 5. **Usage**

#### For End Users:
1. Log in to portal (SSO with CUID)
2. Navigate to any Informatica feature
3. If no credentials stored, redirected to password page
4. Enter CUID and LDAP password
5. All subsequent operations use their credentials

#### For Administrators:
- No hardcoded passwords in production
- Each user enters their own CUID and password
- User can use different CUID than their SSO login if needed
- Audit trail shows which CUID performed actions

### 6. **Production Configuration**

In production settings, update:
```python
# Remove or leave empty - no longer used
INFORMATICA_USERNAME = os.getenv('INFORMATICA_USERNAME', '')  
INFORMATICA_PASSWORD = os.getenv('INFORMATICA_PASSWORD', '')
```

Each user must have:
- Valid CUID
- Informatica PowerCenter account with same CUID
- Appropriate Informatica permissions

### 7. **Remaining Work**

Need to update 5 more API endpoints to use session credentials:
1. Line 499 - `restart_workflow()`
2. Line 570 - `check_workflow_status()`  
3. Line 720 - `stop_workflow()`
4. Line 830 - `get_informatica_folders()`
5. Line 879 - Other Informatica function

Pattern to apply:
```python
# Get user's credentials from session
username, password = get_informatica_credentials_from_session(request)

if not username or not password:
    return JsonResponse({
        'success': False,
        'error': 'Informatica credentials required',
        'redirect_url': '/informatica/credentials/'
    }, status=401)

# Create service with user's credentials
service = InformaticaRestartService(username=username, password=password)
```

### 8. **Testing Steps**

1. **Install cryptography package:**
   ```powershell
   pip install cryptography
   ```

2. **Restart Django server**

3. **Test flow:**
   - Navigate to home page: http://127.0.0.1:8000/
   - Should see prominent yellow banner: "⚡ Set Up Informatica Access"
   - Click "🔓 Configure Credentials Now"
   - Enter your CUID (username) and LDAP password
   - Credentials verified with Informatica before saving
   - Redirected back to home page with green success banner
   - Try navigating to http://127.0.0.1:8000/informatica/manual-restart/
   - Should work without additional prompts
   - Try restarting a workflow - uses your credentials seamlessly

4. **Test API directly:**
   ```powershell
   # Check if credentials stored
   curl http://127.0.0.1:8000/api/informatica/credentials/check/
   
   # Clear credentials
   curl -X POST http://127.0.0.1:8000/api/informatica/credentials/clear/
   ```

### 9. **Benefits**

✅ **Security**: No hardcoded personal credentials  
✅ **Audit**: Each user's actions tracked under their CUID  
✅ **Production Safe**: Your account not at risk  
✅ **LDAP Integration**: Uses corporate credentials  
✅ **Session-Based**: Credentials cleared on logout  
✅ **Better UX**: Credentials requested upfront on home page, not mid-action  
✅ **Non-Intrusive**: Banner appears only if credentials not configured  
✅ **Optional**: Users who don't need Informatica access can ignore  

### 10. **Migration Plan**

**Current State**: ab64033 credentials hardcoded in settings  
**New State**: Each user provides their own credentials  

**Rollout:**
1. Deploy code to production
2. All users prompted for password on first Informatica action
3. Remove INFORMATICA_USERNAME/PASSWORD from environment variables
4. Users with Informatica access can use features
5. Users without access get authentication error (as expected)

### 11. **Troubleshooting**

**Issue**: "Informatica credentials required"  
**Solution**: Click link to enter username and password

**Issue**: "Authentication failed"  
**Solution**: Verify CUID and LDAP password are correct, check Informatica access

**Issue**: "Connection error"  
**Solution**: Check Informatica server connectivity and pmcmd installation

**Issue**: Credentials keep expiring  
**Solution**: Session timeout - need to re-enter password
