"""
Test script for Application Monitoring API
Tests the pattern matching and shows what workflows are found
"""
import os
import sys
import django

# Setup Django
sys.path.append(r'c:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import fetch_all

def test_application_patterns():
    """Test each application pattern to see what workflows match"""
    
    patterns = {
        'DSL_SD': '%DSL%SD%',
        'DSL_SALES_PERIOD': '%DSL%SALES%PERIOD%',
        'SMMART': '%SMMART%',
        'AML': '%AML%',
        'DSL_FINANCE': '%DSL%FINANCE%',
        'CAPEX': '%CAPEX%',
        'DATAMKTP': '%DATAMKT%',
        'CODS_TN': '%CODS%TN%',
        'AIM': '%AIM%',
        'SOLAR_LUCENSE': '%SOLAR%',
        'DSL_MARGIN': '%DSL%MARGIN%',
        'PLANNED_BILLED_COST': '%PLANNED%BILLED%',
        'SLV': '%SLV%',
    }
    
    print("\n" + "="*80)
    print("TESTING APPLICATION PATTERNS")
    print("="*80)
    
    # First, show what unique workflow names exist today
    print("\n1. Checking unique workflow names that ran today:")
    unique_query = """
    SELECT DISTINCT WORKFLOW_NAME
    FROM INFA_PCREPO.REP_TASK_INST_RUN
    WHERE TRUNC(START_TIME) = TRUNC(SYSDATE)
    ORDER BY WORKFLOW_NAME
    """
    
    try:
        all_workflows = fetch_all(unique_query)
        print(f"   Found {len(all_workflows)} unique workflows today\n")
        
        # Show first 20
        print("   First 20 workflows:")
        for i, wf in enumerate(all_workflows[:20]):
            print(f"   {i+1}. {wf.get('workflow_name')}")
        
        if len(all_workflows) > 20:
            print(f"   ... and {len(all_workflows) - 20} more\n")
        
    except Exception as e:
        print(f"   ERROR: {e}\n")
        return
    
    # Test each application pattern
    print("\n2. Testing each application pattern:\n")
    print("-" * 80)
    
    for app_name, pattern in patterns.items():
        query = """
        SELECT COUNT(*) as count,
               COUNT(DISTINCT WORKFLOW_NAME) as unique_workflows
        FROM INFA_PCREPO.REP_TASK_INST_RUN
        WHERE UPPER(WORKFLOW_NAME) LIKE UPPER(:pattern)
        AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        """
        
        try:
            result = fetch_all(query, {'pattern': pattern})
            if result and len(result) > 0:
                count = result[0].get('count', 0)
                unique = result[0].get('unique_workflows', 0)
                
                print(f"\n{app_name:20s} Pattern: {pattern:30s}")
                print(f"{'':20s} Found: {count} executions, {unique} unique workflows")
                
                # Show sample workflows for this pattern
                if unique > 0:
                    sample_query = """
                    SELECT DISTINCT WORKFLOW_NAME
                    FROM INFA_PCREPO.REP_TASK_INST_RUN
                    WHERE UPPER(WORKFLOW_NAME) LIKE UPPER(:pattern)
                    AND TRUNC(START_TIME) = TRUNC(SYSDATE)
                    ORDER BY WORKFLOW_NAME
                    """
                    samples = fetch_all(sample_query, {'pattern': pattern})
                    print(f"{'':20s} Sample workflows:")
                    for i, wf in enumerate(samples[:5]):
                        print(f"{'':20s}   - {wf.get('workflow_name')}")
                    if len(samples) > 5:
                        print(f"{'':20s}   ... and {len(samples) - 5} more")
                
        except Exception as e:
            print(f"\n{app_name:20s} ERROR: {e}")
    
    print("\n" + "-" * 80)
    print("\nDone!\n")

if __name__ == '__main__':
    test_application_patterns()
