# portal/middleware.py
"""
Development middleware to simulate SSO REMOTE_USER header for local testing.
This should ONLY be used in development environments, never in production!
"""


class DevRemoteUserMiddleware:
    """
    Simulates SSO REMOTE_USER header for local development testing.
    
    Usage:
    1. Add this middleware to settings.py MIDDLEWARE list
    2. Set the username you want to test with below
    3. Remove this middleware before deploying to production!
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set a test username for local development
        # Change 'AB64033' to your actual CUID for testing
        if not request.META.get('REMOTE_USER'):
            request.META['REMOTE_USER'] = 'AB64033'
        
        response = self.get_response(request)
        return response
