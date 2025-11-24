# app/ssl_patch.py
"""
Patch SSL verification for corporate environments.
This should be imported early in main.py
"""
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context


# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SSLContextAdapter(HTTPAdapter):
    """HTTP adapter that disables SSL verification."""
    
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


# Monkey patch requests to use our adapter by default
original_get = requests.get
original_post = requests.post


def patched_get(*args, **kwargs):
    if 'verify' not in kwargs:
        kwargs['verify'] = False
    return original_get(*args, **kwargs)


def patched_post(*args, **kwargs):
    if 'verify' not in kwargs:
        kwargs['verify'] = False
    return original_post(*args, **kwargs)


requests.get = patched_get
requests.post = patched_post


def apply_ssl_patch():
    """Apply SSL verification bypass."""
    print("SSL patch applied - SSL verification disabled for corporate certificates")
