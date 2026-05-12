"""
Informatica Authentication Helper
==================================
Manages per-user Informatica credentials using session storage.
Users enter their LDAP password once, then it's used for all Informatica operations.
"""
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from cryptography.fernet import Fernet
import base64
import hashlib
from functools import wraps


def get_encryption_key():
    """
    Get encryption key for password storage in session.
    Uses SECRET_KEY to derive a Fernet-compatible key.
    """
    # Derive a 32-byte key from Django SECRET_KEY
    key_material = settings.SECRET_KEY.encode()
    key_hash = hashlib.sha256(key_material).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt_password(password: str) -> str:
    """Encrypt password for session storage"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password from session"""
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_password.encode())
    return decrypted.decode()


def store_informatica_credentials(request, username: str, password: str):
    """
    Store user's Informatica credentials in encrypted session.
    
    Args:
        request: Django request object
        username: User's CUID/Informatica username
        password: User's LDAP/Informatica password
    """
    encrypted = encrypt_password(password)
    request.session['informatica_password'] = encrypted
    request.session['informatica_username'] = username
    request.session.modified = True


def get_informatica_credentials(request) -> tuple:
    """
    Get user's Informatica credentials from session.
    
    Returns:
        tuple: (username, password) or (None, None) if not stored
    """
    encrypted_password = request.session.get('informatica_password')
    username = request.session.get('informatica_username')
    
    if not encrypted_password or not username:
        return (None, None)
    
    try:
        password = decrypt_password(encrypted_password)
        return (username, password)
    except Exception:
        # Decryption failed - clear invalid credentials
        clear_informatica_credentials(request)
        return (None, None)


def clear_informatica_credentials(request):
    """Clear stored Informatica credentials from session"""
    if 'informatica_password' in request.session:
        del request.session['informatica_password']
    if 'informatica_username' in request.session:
        del request.session['informatica_username']
    request.session.modified = True


def has_informatica_credentials(request) -> bool:
    """Check if user has stored Informatica credentials"""
    return bool(request.session.get('informatica_password') and 
                request.session.get('informatica_username'))


def informatica_credentials_required(view_func):
    """
    Decorator to ensure user has Informatica access (full access mode).
    Redirects to restricted page for read-only users.
    For API endpoints, returns JSON error instead of redirect.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user has Informatica access
        has_access = request.session.get('has_informatica_access', False)
        
        if not has_access:
            # Check if this is an API request
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'success': False,
                    'error': 'Informatica access required',
                    'message': 'This feature requires full Informatica permissions. You are currently in read-only mode.',
                    'access_level': request.session.get('access_level', 'readonly'),
                }, status=403)
            else:
                # Redirect to restricted page for non-API requests
                return redirect('/informatica/guest-restricted/')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def is_guest_mode(request) -> bool:
    """Check if user is in guest mode"""
    return request.session.get('guest_mode', False)


def is_authenticated_mode(request) -> bool:
    """Check if user is authenticated with Informatica"""
    return request.session.get('authenticated_mode', False) and has_informatica_credentials(request)


def get_user_mode(request) -> str:
    """
    Get user's current mode.
    Returns: 'authenticated', 'guest', or 'none'
    """
    if is_authenticated_mode(request):
        return 'authenticated'
    elif is_guest_mode(request):
        return 'guest'
    else:
        return 'none'
