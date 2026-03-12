"""
Comprehensive Data Validation for LAST 8 RUNS STATUS - AI INSIGHTS
Cross-verify table data, formatting, and completeness
"""
import os
import sys

# Setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'monitorportal.settings'
import django
django.setup()

from portal.erp_mdm_insights import get_erp_run_history
from portal.services.level3_service import get_erp_last_8_runs

def format_duration(minutes):
    """Replicate the Django template filter"""
    try:
        mins = float(minutes)
        if mins < 60:
            return f"{mins:.0f}m"
        hours = int(mins // 60)
        remaining_mins = int(mins % 60)
        if remaining_mins == 0:
            return f"{hours}h"
        return f"{hours}h {remaining_mins}m"
    except (ValueError, TypeError):
        return "-"

def validate_all_fields():
    """Validate all fields in LAST 8 RUNS table"""
    print("\n" + "="*100)
    print("COMPREHENSIVE DATA VALIDATION - LAST 8 RUNS STATUS TABLE")
    print("="*100)
    
    data = get_erp_run_history()
    
    if not data.get('success'):
        print(f"❌ Failed to retrieve data: {data.get('message')}")
        return
    
    last_8_runs = data.get('last_8_runs', [])
    
    print(f"\n✅ Retrieved {len(last_8_runs)} runs for validation\n")
    
    headers = ['#', 'RUN TIME (MST)', 'END TIME (MST)', 'DURATION', 'TOTAL', '✅', '⏱️', '❌', '⏸️', 'SUCCESS %', 'STATUS', 'SLA']
    
    # Print table header
    print(f"{'#':<4} {'RUN TIME (MST)':<25} {'END TIME (MST)':<25} {'DURATION':<12} {'TOTAL':<8} {'✅':<5} {'⏱️':<5} {'❌':<5} {'⏸️':<5} {'%-RATE':<9} {'STATUS':<11} {'SLA':<15}")
    print("-" * 150)
    
    validation_errors = []
    
    for idx, run in enumerate(last_8_runs, 1):
        # Prepare display values
        run_time = run.get('start_time', run.get('run_label', 'N/A'))
        
        # Handle end time based on status
        if run.get('is_recovered') and run.get('recovery_info', {}).get('completion_time'):
            end_time = run['recovery_info']['completion_time']
        elif run.get('run_status') == 'SUCCESS':
            end_time = run.get('end_time', 'N/A')
        elif run.get('run_status') == 'SUSPENDED' and run.get('latest_success_end_time'):
            end_time = f"{run.get('latest_success_end_time')} (Last Success)"
        elif run.get('run_status') == 'RUNNING':
            end_time = 'Running...'
        else:
            end_time = run.get('end_time', 'N/A')
        
        # Format duration
        duration = format_duration(run.get('duration_minutes'))
        
        # Get counts
        total = run.get('total_jobs', 0)
        succeeded = run.get('succeeded', 0)
        running = run.get('running', 0)
        failed = run.get('failed', 0)
        suspended = run.get('suspended', 0)
        
        # Calculate success rate
        success_rate = run.get('success_rate', 0)
        
        # Status with badge styling
        status = run.get('run_status', 'UNKNOWN')
        
        # SLA Status
        sla_status = run.get('sla_status', '-')
        sla_display = sla_status
        if sla_status == 'MET' and run.get('sla_met_by'):
            sla_display = f"✓ MET ({run.get('sla_met_by'):.0f}m)"
        elif sla_status == 'MISSED' and run.get('sla_met_by'):
            sla_display = f"✗ MISSED ({run.get('sla_met_by'):.0f}m)"
        elif sla_status == 'IN PROGRESS':
            sla_display = "⏱️ IN PROGRESS"
        
        # Print row (shortened)
        run_time_short = run.get('run_label', 'N/A')[:19]
        end_time_short = end_time[:19] if isinstance(end_time, str) else str(end_time)[:19]
        
        print(f"{idx:<4} {run_time_short:<25} {end_time_short:<25} {duration:<12} {total:<8} {succeeded:<5} {running:<5} {failed:<5} {suspended:<5} {success_rate:<9.1f} {status:<11} {sla_display:<15}")
        
        # Validate data integrity
        # 1. Check job count totals
        count_sum = succeeded + running + failed + suspended
        if count_sum != total and total > 0:
            validation_errors.append(f"Run #{idx}: Job count mismatch - Total={total}, Sum={count_sum}")
        
        # 2. Check consistency between status and counts
        if status == 'SUCCESS' and (running > 0 or suspended > 0):
            validation_errors.append(f"Run #{idx}: SUCCESS status but has running={running} or suspended={suspended}")
        
        if status == 'SUSPENDED' and succeeded == 0 and failed == 0:
            # This is expected - all jobs suspended
            pass
        
        # 3. Check SLA status consistency
        if status == 'SUSPENDED':
            if sla_status not in ['UNKNOWN', '-']:
                validation_errors.append(f"Run #{idx}: SUSPENDED status but SLA status is {sla_status}")
        
        # 4. Check if end_time is present when expected
        if status == 'SUCCESS' and run.get('end_time') is None:
            validation_errors.append(f"Run #{idx}: SUCCESS status but no end_time")
    
    # Print validation results
    print("\n" + "-" * 150)
    print("\n📊 VALIDATION REPORT:\n")
    
    if validation_errors:
        print("❌ ERRORS FOUND:\n")
        for error in validation_errors:
            print(f"  • {error}")
    else:
        print("✅ ALL VALIDATION CHECKS PASSED")
    
    # Summary statistics
    print("\n\n📈 SUMMARY STATISTICS:\n")
    
    success_runs = sum(1 for run in last_8_runs if run.get('run_status') == 'SUCCESS')
    suspended_runs = sum(1 for run in last_8_runs if run.get('run_status') == 'SUSPENDED')
    running_runs = sum(1 for run in last_8_runs if run.get('run_status') == 'RUNNING')
    
    total_jobs = sum(run.get('total_jobs', 0) for run in last_8_runs)
    total_succeeded = sum(run.get('succeeded', 0) for run in last_8_runs)
    total_running = sum(run.get('running', 0) for run in last_8_runs)
    total_failed = sum(run.get('failed', 0) for run in last_8_runs)
    total_suspended = sum(run.get('suspended', 0) for run in last_8_runs)
    
    print(f"  Runs by Status:")
    print(f"    ✅ Succeeded:    {success_runs}/8")
    print(f"    ⏱️  Running:     {running_runs}/8")
    print(f"    ⏸️  Suspended:   {suspended_runs}/8\n")
    
    print(f"  Total Jobs Across All Runs:")
    print(f"    Total:          {total_jobs}")
    print(f"    ✅ Succeeded:   {total_succeeded}")
    print(f"    ⏱️  Running:    {total_running}")
    print(f"    ❌ Failed:     {total_failed}")
    print(f"    ⏸️  Suspended:  {total_suspended}\n")
    
    recovered_count = sum(1 for run in last_8_runs if run.get('is_recovered'))
    print(f"  Recovered Runs: {recovered_count}/8\n")
    
    # Detailed field validation
    print("\n" + "="*100)
    print("DETAILED FIELD VALIDATION")
    print("="*100 + "\n")
    
    field_validation = {
        'run_label': 0,
        'taskflow_run_id': 0,
        'start_time': 0,
        'end_time': 0,
        'duration_minutes': 0,
        'total_jobs': 0,
        'succeeded': 0,
        'running': 0,
        'failed': 0,
        'suspended': 0,
        'success_rate': 0,
        'run_status': 0,
        'sla_status': 0,
        'is_recovered': 0,
        'latest_success_end_time': 0,
    }
    
    for run in last_8_runs:
        for field in field_validation:
            if field in run and run[field] is not None:
                field_validation[field] += 1
    
    print("Field Presence Check (out of 8 runs):\n")
    for field, count in sorted(field_validation.items()):
        status = "✅" if count == 8 else "⚠️" if count > 0 else "❌"
        print(f"  {status} {field:<25} : {count}/8 runs have this field")
    
    # Additional checks
    print("\n" + "="*100)
    print("CURRENTRUN VALIDATION")
    print("="*100 + "\n")
    
    current_run = data.get('current_run', {})
    print(f"Current Run Statistics:")
    print(f"  Total Jobs:    {current_run.get('total_jobs', 0)}")
    print(f"  Completed:     {current_run.get('completed', 0)}")
    print(f"  Running:       {current_run.get('running', 0)}")
    print(f"  Failed:        {current_run.get('failed', 0)}")
    print(f"  Suspended:     {current_run.get('suspended', 0)}")
    print(f"  Success Rate:  {current_run.get('success_rate', 0):.1f}%")
    
    # Verify current run sums
    current_total = (current_run.get('completed', 0) + current_run.get('running', 0) + 
                     current_run.get('failed', 0) + current_run.get('suspended', 0))
    expected_total = current_run.get('total_jobs', 0)
    
    if current_total == expected_total:
        print(f"\n  ✅ Current run counts verified: {current_total} = {expected_total}")
    else:
        print(f"\n  ❌ Current run count mismatch: {current_total} != {expected_total}")
    
    print("\n" + "="*100)
    print("✅ CROSS-VERIFICATION COMPLETE")
    print("="*100)

if __name__ == '__main__':
    validate_all_fields()
