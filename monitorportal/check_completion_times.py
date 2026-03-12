#!/usr/bin/env python
"""
Fix completion times - convert to proper MST times
The times were stored incorrectly, need to update with accurate completion times
"""
import sys
import os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.models import ERPRunRecovery

# MST timezone
mst_tz = pytz.timezone('America/Denver')

print("\n" + "=" * 100)
print("CURRENT COMPLETION TIMES (showing what's in database)")
print("=" * 100)
print()

recoveries = ERPRunRecovery.objects.filter(is_active=True).order_by('-run_start_time')

for rec in recoveries:
    start_mst = rec.run_start_time.astimezone(mst_tz) if rec.run_start_time.tzinfo else rec.run_start_time
    completion_mst = rec.completion_time.astimezone(mst_tz) if (rec.completion_time and rec.completion_time.tzinfo) else rec.completion_time
    
    print(f"Run ID: {rec.taskflow_run_id}")
    print(f"  Start Time (MST):      {start_mst.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"  Completion Time (MST): {completion_mst.strftime('%Y-%m-%d %I:%M %p') if completion_mst else 'NOT SET'}")
    print()

print("=" * 100)
print("\nWhat are the CORRECT completion times for these runs?")
print("Please provide in format: YYYY-MM-DD HH:MM:SS (in MST timezone)")
print("\nExample: 2026-03-09 14:30:00")
