# portal/context_processors.py
from .ssrs_registry import APPS


def nav_apps(request):
    """
    Make APPS (SSRS registry) available globally in all templates.
    Also provides user CUID, display name, and access level for all pages.
    """
    # Get display username from session (set during login)
    display_username = request.session.get('display_username', None)
    
    # Get CUID from REMOTE_USER header or fallback to username
    cuid = request.META.get('REMOTE_USER', '').upper()
    if not cuid and request.user.is_authenticated:
        cuid = request.user.username.upper()
    
    # If no display username in session, use CUID or display name from middleware
    if not display_username:
        display_name = getattr(request, 'user_display_name', None)
        if not display_name:
            display_name = cuid if cuid else 'Guest'
        display_username = display_name
    
    # Get access information from session
    has_informatica_access = request.session.get('has_informatica_access', False)
    access_level = request.session.get('access_level', 'none')
    
    return {
        "nav_apps": APPS,
        "user_cuid": cuid if cuid else "GUEST",
        "user_display": display_username,
        "has_informatica_access": has_informatica_access,
        "access_level": access_level,
    }
