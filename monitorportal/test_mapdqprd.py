# test_mapdqprd.py - Test MAPDQPRD database connectivity
import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all_mapdqprd
from portal.services.level3_service import (
    get_mdm_job_status,
    get_erp_job_status,
    get_adf_run_status,
    get_adf_failed_jobs
)

def test_mapdqprd_connection():
    """Test basic MAPDQPRD database connection"""
    print("\n" + "="*80)
    print("🔍 Testing MAPDQPRD Database Connection")
    print("="*80)
    
    try:
        result = fetch_all_mapdqprd("SELECT 1 AS test FROM DUAL")
        print(f"✅ Connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_mdm_query():
    """Test MDM job status query"""
    print("\n" + "="*80)
    print("🔍 Testing MDM Job Status Query")
    print("="*80)
    
    try:
        data = get_mdm_job_status()
        print(f"✅ Query successful - {len(data)} records retrieved")
        
        if data:
            print("\n📊 Sample Records (first 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"\n  Record {i}:")
                print(f"    Asset Name: {record.get('asset_name')}")
                print(f"    Status: {record.get('status')}")
                print(f"    Start Time: {record.get('start_time')}")
                print(f"    End Time: {record.get('end_time')}")
        
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_erp_query():
    """Test ERP job status query"""
    print("\n" + "="*80)
    print("🔍 Testing ERP Job Status Query")
    print("="*80)
    
    try:
        data = get_erp_job_status()
        print(f"✅ Query successful - {len(data)} records retrieved")
        
        if data:
            print("\n📊 Sample Records (first 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"\n  Record {i}:")
                print(f"    Asset Name: {record.get('asset_name')}")
                print(f"    Subtask: {record.get('subtask_asset_name')}")
                print(f"    Location: {record.get('location')}")
                print(f"    Status: {record.get('status')}")
                print(f"    Start Time (PST): {record.get('start_time_pst')}")
        
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adf_run_status():
    """Test ADF run status query"""
    print("\n" + "="*80)
    print("🔍 Testing ADF Run Status Query")
    print("="*80)
    
    try:
        data = get_adf_run_status()
        print(f"✅ Query successful - {len(data)} records retrieved")
        
        if data:
            print("\n📊 Sample Records (first 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"\n  Record {i}:")
                print(f"    Job Name: {record.get('job_name')}")
                print(f"    Resource Type: {record.get('resource_type')}")
                print(f"    Status: {record.get('job_status')}")
                print(f"    Start Time: {record.get('start_time')}")
        
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adf_failed_jobs():
    """Test ADF failed jobs query"""
    print("\n" + "="*80)
    print("🔍 Testing ADF Failed Jobs Query")
    print("="*80)
    
    try:
        data = get_adf_failed_jobs()
        print(f"✅ Query successful - {len(data)} records retrieved")
        
        if data:
            print("\n📊 Sample Records (first 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"\n  Record {i}:")
                print(f"    Job Name: {record.get('job_name')}")
                print(f"    Resource Type: {record.get('resource_type')}")
                print(f"    Status: {record.get('job_status')}")
                print(f"    Error: {record.get('error_message')[:100] if record.get('error_message') else 'None'}...")
        
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪 "*40)
    print("MAPDQPRD DATABASE TESTS")
    print("🧪 "*40)
    
    results = []
    
    # Test connection
    results.append(("Connection Test", test_mapdqprd_connection()))
    
    # Test MDM query
    results.append(("MDM Query", test_mdm_query()))
    
    # Test ERP query
    results.append(("ERP Query", test_erp_query()))
    
    # Test ADF run status
    results.append(("ADF Run Status", test_adf_run_status()))
    
    # Test ADF failed jobs
    results.append(("ADF Failed Jobs", test_adf_failed_jobs()))
    
    # Print summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! MAPDQPRD database is fully operational.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")

if __name__ == "__main__":
    main()
