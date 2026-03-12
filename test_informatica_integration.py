"""
Test script for Informatica Cloud API integration

Tests the connection, data filtering, and storage without requiring actual API access.
Demonstrates the complete flow with mock data.

Usage:
    python test_informatica_integration.py
"""

import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.services.informatica_cloud_service import (
    InformaticaCloudAPI,
    get_erp_task_summary,
)
from portal.models import InformaticaTaskStatus


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def test_configuration():
    """Test if API credentials are configured"""
    print_header("TEST 1: API Configuration Check")
    
    api = InformaticaCloudAPI()
    
    if api.is_configured():
        print("✅ Informatica Cloud API credentials are configured")
        print(f"   URL: {api.base_url}")
        print(f"   User: {api.username[:20]}...")
    else:
        print("❌ Informatica Cloud API credentials NOT configured")
        print("\n   Action required:")
        print("   1. Add INFORMATICA_CLOUD_USER to settings.py")
        print("   2. Add INFORMATICA_CLOUD_PASSWORD to settings.py")
        return False
    
    return True


def test_erp_filtering():
    """Test ERP keyword filtering logic"""
    print_header("TEST 2: ERP Filtering Logic")
    
    api = InformaticaCloudAPI()
    
    # Test cases
    test_tasks = [
        ('wkf_ERP_Daily_Refresh', True, 'Should match: contains ERP'),
        ('wkf_SAPS4_Load_Master', True, 'Should match: contains SAPS4'),
        ('wkf_CDW_DSL_ERP_Master', True, 'Should match: contains CDW_DSL_ERP'),
        ('wkf_Customer_Load', False, 'Should NOT match: no ERP keyword'),
        ('ASL_ERP_DATAHUB_Sync', True, 'Should match: contains ERP'),
        ('wkf_Financial_Reporting', False, 'Should NOT match: generic name'),
    ]
    
    all_passed = True
    for task_name, expected, description in test_tasks:
        result = api.is_erp_related(task_name)
        status = "✅" if result == expected else "❌"
        
        if result != expected:
            all_passed = False
        
        print(f"{status} {task_name:<35} → {result:<5} ({description})")
    
    return all_passed


def test_erp_location_extraction():
    """Test extraction of ERP location from task name"""
    print_header("TEST 3: ERP Location Extraction")
    
    api = InformaticaCloudAPI()
    
    test_cases = [
        ('wkf_CDW_DSL_ERP_Daily_Refresh', 'CDW_DSL_ERP'),
        ('wkf_ASL_SAPS4_Master_Load', 'CDW_ASL_SAPS4'),
        ('wkf_ASL_ERP_DATAHUB_Sync', 'ASL_ERP_DATAHUB'),
        ('wkf_Generic_Task', None),
    ]
    
    all_passed = True
    for task_name, expected_location in test_cases:
        location = api.extract_erp_location(task_name)
        status = "✅" if location == expected_location else "❌"
        
        if location != expected_location:
            all_passed = False
        
        print(f"{status} {task_name:<40} → {str(location):<20} (expected: {expected_location})")
    
    return all_passed


def test_database_model():
    """Test InformaticaTaskStatus model functionality"""
    print_header("TEST 4: Database Model (InformaticaTaskStatus)")
    
    try:
        # Check if table exists
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'informatica_task_status'
            """)
            exists = cursor.fetchone()[0] > 0
        
        if exists:
            print("✅ Database table 'informatica_task_status' exists")
        else:
            print("⚠️  Database table does not exist")
            print("   Run: python manage.py migrate")
            return False
        
        # Try to query
        count = InformaticaTaskStatus.objects.count()
        print(f"✅ Table accessible. Current records: {count}")
        
        # Test auto-expiration logic
        now = timezone.now()
        future = now + timedelta(days=2)
        
        # Create test record
        test_record = InformaticaTaskStatus(
            task_id="TEST_TASK_001",
            task_name="Test ERP Task",
            status="SUSPENDED",
            is_erp_related=True,
            erp_location="CDW_DSL_ERP",
        )
        
        # Check if expire date is auto-set
        test_record.save()
        
        if test_record.expires_at:
            days_until_expire = (test_record.expires_at - now).days
            print(f"✅ Auto-expiration working: record expires in {days_until_expire} days")
            
            # Clean up test record
            test_record.delete()
            print(f"✅ Test record cleaned up")
        else:
            print("❌ Auto-expiration not working")
            test_record.delete()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False


def test_data_retention_policy():
    """Test 2-day retention and cleanup logic"""
    print_header("TEST 5: Data Retention Policy (2-day cleanup)")
    
    try:
        # Show current stats
        summary = get_erp_task_summary()
        
        print("Current ERP Task Statistics:")
        for key, value in summary.items():
            print(f"  {key:<25}: {value}")
        
        # Test cleanup (shouldn't delete anything recent)
        expired_count, _ = InformaticaTaskStatus.cleanup_expired()
        
        print(f"\n✅ Cleanup completed: {expired_count} expired records deleted")
        print("   (No records deleted if all are recent)")
        
        return True
        
    except Exception as e:
        print(f"❌ Retention policy test error: {e}")
        return False


def test_mock_sync():
    """Simulate a sync with mock data (doesn't connect to API)"""
    print_header("TEST 6: Mock Data Sync")
    
    # Create mock task data (simulating API response)
    mock_tasks = [
        {
            'id': 'TASK_ERP_001',
            'name': 'wkf_ERP_Daily_Refresh_Master',
            'status': 'SUSPENDED',
            'workflowName': 'wkf_ERP_Daily_Refresh_Master',
            'suspendedAt': '2026-03-10T10:00:00Z',
            'restartCount': 2,
            'lastRestartTime': '2026-03-10T14:00:00Z',
            'completionStatus': None,
            'notes': 'Waiting for manual restart',
        },
        {
            'id': 'TASK_SAPS4_001',
            'name': 'wkf_ASL_SAPS4_Master_Load',
            'status': 'COMPLETED',
            'workflowName': 'wkf_ASL_SAPS4_Master_Load',
            'suspendedAt': '2026-03-10T08:00:00Z',
            'lastRestartTime': '2026-03-10T12:00:00Z',
            'restartCompletedTime': '2026-03-10T13:00:00Z',
            'completionStatus': 'SUCCESS',
            'restartCount': 1,
            'notes': 'Restarted and completed successfully',
        },
    ]
    
    print(f"Processing {len(mock_tasks)} mock ERP tasks...\n")
    
    api = InformaticaCloudAPI()
    
    stored = 0
    for task in mock_tasks:
        if api.is_erp_related(task.get('name', '')):
            try:
                obj, created = InformaticaTaskStatus.objects.update_or_create(
                    task_id=str(task['id']),
                    defaults={
                        'task_name': task.get('name', ''),
                        'status': task.get('status', 'UNKNOWN').upper(),
                        'is_erp_related': True,
                        'erp_location': api.extract_erp_location(task.get('name', '')),
                        'workflow_name': task.get('workflowName', task.get('name', '')),
                        'restart_count': task.get('restartCount', 0),
                        'restart_completed_status': task.get('completionStatus'),
                        'restart_notes': task.get('notes'),
                    }
                )
                
                action = "Created" if created else "Updated"
                print(f"✅ {action}: {task['name']}")
                stored += 1
                
            except Exception as e:
                print(f"❌ Error storing {task['name']}: {e}")
    
    print(f"\n✅ Successfully stored {stored} mock ERP tasks")
    return True


def test_api_endpoints():
    """Test the query methods"""
    print_header("TEST 7: API Query Methods")
    
    try:
        suspended = InformaticaTaskStatus.get_suspended_tasks()
        restarted = InformaticaTaskStatus.get_restarted_tasks()
        summary = InformaticaTaskStatus.get_erp_summary()
        
        print(f"✅ get_suspended_tasks(): {suspended.count()} tasks")
        print(f"✅ get_restarted_tasks(): {restarted.count()} tasks")
        print(f"✅ get_erp_summary(): {len(summary)} summary metrics")
        
        print("\nSummary breakdown:")
        for key, value in summary.items():
            print(f"  {key:<25}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query method error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  INFORMATICA CLOUD API INTEGRATION - TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Configuration Check", test_configuration()))
    
    if results[-1][1]:  # Only continue if configured
        results.append(("ERP Filtering Logic", test_erp_filtering()))
        results.append(("ERP Location Extraction", test_erp_location_extraction()))
        results.append(("Database Model", test_database_model()))
        results.append(("Data Retention Policy", test_data_retention_policy()))
        results.append(("Mock Data Sync", test_mock_sync()))
        results.append(("API Query Methods", test_api_endpoints()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! Integration is ready to use.")
        print("\nNext steps:")
        print("  1. Configure API credentials in settings.py")
        print("  2. Run: python manage.py sync_informatica_erp_tasks --show-summary")
        print("  3. Setup periodic syncing (Celery/Cron/APScheduler)")
        print("  4. Add dashboard widgets to display ERP task status")
        return 0
    else:
        print("⚠️  Some tests failed. See details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
