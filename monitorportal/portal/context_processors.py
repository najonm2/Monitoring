# portal/context_processors.py
from .ssrs_registry import APPS

def nav_apps(request):
    return {"nav_apps": APPS}