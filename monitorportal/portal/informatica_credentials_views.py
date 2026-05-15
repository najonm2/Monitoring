"""
Informatica Credentials Management Views
=========================================
Handles user credential entry and management for Informatica operations.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from portal.informatica_auth import (
    store_informatica_credentials,
    get_informatica_credentials,
    clear_informatica_credentials,
    has_informatica_credentials
)
from portal.services.informatica_restart_service import InformaticaRestartService
from django.conf import settings


@require_http_methods(["GET", "POST"])
def informatica_login(request):
    """
    Informatica login page - first page after SSO authentication.
    All users must login here. Access level determined by Informatica authentication:
    - Success: Full access (can restart/stop/schedule workflows)
    - Fail: Read-only access (can view reports but not manage workflows)
    """
    # Check if user is already logged in with portal
    user_mode = request.session.get('portal_logged_in', False)
    if user_mode:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            return render(request, "portal/informatica_login.html", {
                "error": "Both username and password are required",
                "username": username,
            })
        
        # Test credentials with Informatica
        service = InformaticaRestartService(username=username, password=password)
        
        try:
            result = service.establish_connection()
            
            if result.get('success'):
                # Informatica authentication successful - FULL ACCESS
                store_informatica_credentials(request, username, password)
                request.session['portal_logged_in'] = True
                request.session['has_informatica_access'] = True
                request.session['access_level'] = 'full'
                request.session['display_username'] = username
                
                return redirect('home')
            else:
                # Informatica authentication failed - READ-ONLY ACCESS
                # Still let them in to view reports
                request.session['portal_logged_in'] = True
                request.session['has_informatica_access'] = False
                request.session['access_level'] = 'readonly'
                request.session['display_username'] = username
                
                warning_msg = (
                    f"You have been logged in with read-only access. "
                    f"Informatica authentication failed: {result.get('error') or result.get('message') or 'Authentication failed'}. "
                    f"You can view reports and dashboards, but cannot perform workflow operations."
                )
                
                # Redirect to home with warning
                request.session['login_warning'] = warning_msg
                return redirect('home')
                
        except Exception as e:
            # Connection error - Still grant read-only access
            request.session['portal_logged_in'] = True
            request.session['has_informatica_access'] = False
            request.session['access_level'] = 'readonly'
            request.session['display_username'] = username
            
            warning_msg = (
                f"You have been logged in with read-only access. "
                f"Could not connect to Informatica: {str(e)}. "
                f"You can view reports and dashboards, but cannot perform workflow operations."
            )
            
            request.session['login_warning'] = warning_msg
            return redirect('home')
    
    # GET request - show login form
    return render(request, "portal/informatica_login.html", {})


@login_required
@require_http_methods(["GET", "POST"])
def informatica_credentials(request):
    """
    Informatica credentials management page.
    Users enter their LDAP password for Informatica access.
    """
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            return render(request, "portal/informatica_credentials.html", {
                "error": "Both username and password are required",
                "username": username or request.user.username,
            })
        
        # Test credentials with Informatica before storing
        service = InformaticaRestartService(username=username, password=password)
        
        try:
            result = service.establish_connection()
            
            if result.get('success'):
                # Store encrypted credentials in session
                store_informatica_credentials(request, username, password)
                
                # Redirect to where they were trying to go
                next_url = request.GET.get('next', '/informatica/manual-restart/')
                return redirect(next_url)
            else:
                error_message = result.get('error') or result.get('message') or 'Authentication failed'
                return render(request, "portal/informatica_credentials.html", {
                    "error": f"Informatica authentication failed: {error_message}",
                    "username": username,
                })
        except Exception as e:
            return render(request, "portal/informatica_credentials.html", {
                "error": f"Connection error: {str(e)}",
                "username": username,
            })
    
    # GET request - show form
    return render(request, "portal/informatica_credentials.html", {
        "username": request.user.username,
        "has_credentials": has_informatica_credentials(request),
    })


@login_required
@require_http_methods(["POST"])
def clear_credentials(request):
    """Clear stored Informatica credentials"""
    clear_informatica_credentials(request)
    return JsonResponse({"success": True, "message": "Credentials cleared"})


@login_required
@require_http_methods(["GET"])
def check_credentials(request):
    """Check if user has stored Informatica credentials"""
    has_creds = has_informatica_credentials(request)
    username, _ = get_informatica_credentials(request)
    
    return JsonResponse({
        "has_credentials": has_creds,
        "username": username if has_creds else None,
    })


@login_required
@require_http_methods(["GET", "POST"])
def informatica_logout(request):
    """Logout from portal session and return to login page"""
    # Clear all session data
    clear_informatica_credentials(request)
    if 'portal_logged_in' in request.session:
        del request.session['portal_logged_in']
    if 'has_informatica_access' in request.session:
        del request.session['has_informatica_access']
    if 'access_level' in request.session:
        del request.session['access_level']
    if 'display_username' in request.session:
        del request.session['display_username']
    if 'login_warning' in request.session:
        del request.session['login_warning']
    if 'guest_mode' in request.session:
        del request.session['guest_mode']
    if 'authenticated_mode' in request.session:
        del request.session['authenticated_mode']
    request.session.modified = True
    
    # Redirect to login page
    return redirect('/informatica/login/')


@login_required
@require_http_methods(["GET"])
def guest_restricted(request):
    """Page shown to guest users trying to access Informatica features"""
    return render(request, "portal/guest_restricted.html", {})
