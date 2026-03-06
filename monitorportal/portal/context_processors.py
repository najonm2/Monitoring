# portal/context_processors.py
from .ssrs_registry import APPS


def nav_apps(request):
    """
    Make APPS (SSRS registry) available globally in all templates.
    Also provides user CUID for display.
    """
    # Get CUID from REMOTE_USER header or fallback to username
    cuid = request.META.get('REMOTE_USER', '').upper()
    if not cuid and request.user.is_authenticated:
        cuid = request.user.username.upper()
    
    return {
        "nav_apps": APPS,
        "user_cuid": cuid if cuid else "GUEST",
        "user_display": cuid if cuid else "Guest",
    }
