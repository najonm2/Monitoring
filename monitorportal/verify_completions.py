#!/usr/bin/env python
"""Verify recovery records have completion times"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorportal.settings")
import django
django.setup()

from portal.models import ERPRunRecovery

print("\n" + "=" * 100)
print("RECOVERY RECORDS WITH COMPLETION TIMES")
print("=" * 100)
print()

recoveries = ERPRunRecovery.objects.filter(is_active=True).order_by('-run_start_time')

for rec in recoveries:
    print(f"Run ID: {rec.taskflow_run_id}")
    print(f"  Start Time:      {rec.run_start_time}")
    print(f"  Completion Time: {rec.completion_time if rec.completion_time else '❌ NOT SET'}")
    print(f"  Status:          {rec.original_status} → {rec.final_status}")
    print(f"  Recovered by:    {rec.recovered_by}")
    print()

print("=" * 100)
