#!/usr/bin/env python
"""
Test Oracle database connections after password change
Run this after updating credentials in portal/db/oracle_client.py
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
django.setup()

from portal.db.oracle_client import get_conn, get_mapdqprd_conn

def test_level3_connection():
    """Test Level3 Informatica repository connection"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ Level3 Connection: SUCCESS")
            return True
        else:
            print("❌ Level3 Connection: FAILED (Unexpected result)")
            return False
    except Exception as e:
        print(f"❌ Level3 Connection: FAILED")
        print(f"   Error: {e}")
        return False

def test_mapdqprd_connection():
    """Test MAPDQPRD database connection"""
    try:
        conn = get_mapdqprd_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ MAPDQPRD Connection: SUCCESS")
            return True
        else:
            print("❌ MAPDQPRD Connection: FAILED (Unexpected result)")
            return False
    except Exception as e:
        print(f"❌ MAPDQPRD Connection: FAILED")
        print(f"   Error: {e}")
        return False

def test_level3_data():
    """Test fetching actual Level3 data"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFA_PCREPO.REP_TASK_INST_RUN 
            WHERE TASK_TYPE_NAME = 'Session'
              AND TRUNC(START_TIME) = TRUNC(SYSDATE)
        """)
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ Level3 Data Query: SUCCESS ({count} sessions today)")
        return True
    except Exception as e:
        print(f"❌ Level3 Data Query: FAILED")
        print(f"   Error: {e}")
        return False

def test_mapdqprd_data():
    """Test fetching actual MAPDQPRD data"""
    try:
        conn = get_mapdqprd_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM MAPDQPRD.IICS_CDI_RUN_INFO 
            WHERE ASSET_NAME = 'wkf_ERP_DAILY_REFRESH_MASTER'
        """)
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ MAPDQPRD Data Query: SUCCESS ({count} ERP runs in history)")
        return True
    except Exception as e:
        print(f"❌ MAPDQPRD Data Query: FAILED")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 Testing Oracle Database Connections")
    print("="*60 + "\n")
    
    level3_ok = test_level3_connection()
    mapdqprd_ok = test_mapdqprd_connection()
    
    print("\n" + "="*60)
    print("🔍 Testing Data Access")
    print("="*60 + "\n")
    
    level3_data_ok = test_level3_data() if level3_ok else False
    mapdqprd_data_ok = test_mapdqprd_data() if mapdqprd_ok else False
    
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    
    all_ok = all([level3_ok, mapdqprd_ok, level3_data_ok, mapdqprd_data_ok])
    
    if all_ok:
        print("✅ ALL TESTS PASSED - Connections working!")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        print("\nTroubleshooting:")
        print("1. Verify password is correct in portal/db/oracle_client.py")
        print("2. Check that database is accessible (ping hostname)")
        print("3. Verify user account is not locked in Oracle")
        print("4. Check firewall rules (port 1521)")
    
    print("="*60 + "\n")
    
    sys.exit(0 if all_ok else 1)
