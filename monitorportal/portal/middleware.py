# portal/middleware.py
"""
Development middleware to capture logged-in user info.
Automatically detects Windows username and display name.
"""
import os
import platform


def _get_windows_display_name():
    """
    Get the full display name of the currently logged-in Windows user.
    Falls back to USERNAME environment variable if display name is unavailable.
    """
    if platform.system() != 'Windows':
        return os.environ.get('USER', 'Guest')
    
    try:
        import ctypes
        GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
        NameDisplay = 3  # NameDisplay enum value
        size = ctypes.pointer(ctypes.c_ulong(0))
        GetUserNameEx(NameDisplay, None, size)
        if size.contents.value > 0:
            nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
            GetUserNameEx(NameDisplay, nameBuffer, size)
            if nameBuffer.value:
                return nameBuffer.value
    except Exception:
        pass
    
    return os.environ.get('USERNAME', 'Guest')


class DevRemoteUserMiddleware:
    """
    Captures the logged-in user's CUID and display name.
    Works with Windows SSO (REMOTE_USER) or falls back to OS username.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set REMOTE_USER from OS if not already set by SSO
        if not request.META.get('REMOTE_USER'):
            request.META['REMOTE_USER'] = os.environ.get('USERNAME', os.environ.get('USER', 'Guest'))
        
        # Attach the full display name to the request for templates
        request.user_display_name = _get_windows_display_name()
        
        response = self.get_response(request)
        return response
