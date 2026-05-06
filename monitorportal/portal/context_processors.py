# portal/context_processors.py
from .ssrs_registry import APPS


def nav_apps(request):
    """
    Make APPS (SSRS registry) available globally in all templates.
    Also provides user CUID and display name for all pages.
    """
    # Get CUID from REMOTE_USER header or fallback to username
    cuid = request.META.get('REMOTE_USER', '').upper()
    if not cuid and request.user.is_authenticated:
        cuid = request.user.username.upper()
    
    # Get full display name from middleware (set by DevRemoteUserMiddleware)
    display_name = getattr(request, 'user_display_name', None)
    if not display_name:
        display_name = cuid if cuid else 'Guest'
    
    return {
        "nav_apps": APPS,
        "user_cuid": cuid if cuid else "GUEST",
        "user_display": display_name,
    }
