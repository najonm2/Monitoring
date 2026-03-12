#!/usr/bin/env python
"""Clear ERP dashboard cache to force refresh"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from django.core.cache import cache

# Clear ERP cache
cache.delete('erp_run_history_data')
print("✅ Cleared ERP dashboard cache")
print("Dashboard will show fresh data on next load")
