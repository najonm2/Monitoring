# Password & Connection Update Guide

**Last Updated:** March 9, 2026

## 🔑 Where Passwords Are Stored

All Oracle database credentials are currently stored in:

**📁 File Location:**
```
monitorportal/portal/db/oracle_client.py
```

---

## 📝 What To Update

### **1. Level3 Application Database (Informatica Repository)**

**Location:** Lines 11-17 in `portal/db/oracle_client.py`

```python
DB_CONFIG = {
    "host": "azeus2loraipcp2.corp.intranet",
    "port": 1521,
    "service": "infr01p_app",
    "user": "icsm_appl",
    "password": "icsm_appl_infprd"  # ← UPDATE THIS PASSWORD HERE
}
```

**Used For:**
- Level3 Failed Jobs Status
- Level3 Long Running Jobs
- Level3 7-Day Statistics
- BI Feed Report

**Tables Accessed:**
- `INFA_PCREPO.REP_TASK_INST_RUN`
- `ICSM.app_control_status`

---

### **2. MAPDQPRD Database (MDM, ERP, ADF Applications)**

**Location:** Lines 20-26 in `portal/db/oracle_client.py`

```python
MAPDQPRD_DB_CONFIG = {
    "host": "RACORAP32-SCAN.CORP.INTRANET",
    "port": 1521,
    "service": "SVC_IDG01P",
    "user": "mapdqprd",
    "password": "2026NewIDMC"  # ← UPDATE THIS PASSWORD HERE
}
```

**Used For:**
- ERP Last 8 Runs
- ERP All Runs (Last 7 Days)
- MDM Status
- ADF Pipeline Monitoring

**Tables Accessed:**
- `MAPDQPRD.IICS_CDI_RUN_INFO`
- `MAPDQPRD.IICS_ADF_RUN_TRACKER`

---

## 🔄 Step-by-Step Update Process

### **Option A: Quick Update (Development/Testing)**

1. **Open the file:**
   ```bash
   cd c:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
   code portal/db/oracle_client.py
   ```

2. **Update the password:**
   - Find the appropriate `DB_CONFIG` or `MAPDQPRD_DB_CONFIG` section
   - Change the `"password": "..."` value to the new password
   - Save the file

3. **Restart Django:**
   ```bash
   # Stop the current server (Ctrl+C)
   python manage.py runserver
   ```

4. **Test the connection:**
   ```bash
   # Test Level3 connection
   python -c "from portal.db.oracle_client import get_conn; conn = get_conn(); print('✅ Level3 Connected'); conn.close()"
   
   # Test MAPDQPRD connection
   python -c "from portal.db.oracle_client import get_mapdqprd_conn; conn = get_mapdqprd_conn(); print('✅ MAPDQPRD Connected'); conn.close()"
   ```

5. **Verify in browser:**
   - Open: http://localhost:8000/portal/level3/lvl3-failed-job-status/
   - Should see data (not error page)

---

### **Option B: Secure Update (Production - RECOMMENDED)**

For production, **DO NOT hardcode passwords** in the Python file. Use environment variables or Oracle Wallet.

#### **Method 1: Environment Variables**

1. **Update `oracle_client.py`:**

```python
import os

DB_CONFIG = {
    "host": os.getenv("ORACLE_HOST", "azeus2loraipcp2.corp.intranet"),
    "port": int(os.getenv("ORACLE_PORT", "1521")),
    "service": os.getenv("ORACLE_SERVICE", "infr01p_app"),
    "user": os.getenv("ORACLE_USER", "icsm_appl"),
    "password": os.getenv("ORACLE_PASSWORD", "")  # Read from environment
}

MAPDQPRD_DB_CONFIG = {
    "host": os.getenv("MAPDQPRD_HOST", "RACORAP32-SCAN.CORP.INTRANET"),
    "port": int(os.getenv("MAPDQPRD_PORT", "1521")),
    "service": os.getenv("MAPDQPRD_SERVICE", "SVC_IDG01P"),
    "user": os.getenv("MAPDQPRD_USER", "mapdqprd"),
    "password": os.getenv("MAPDQPRD_PASSWORD", "")  # Read from environment
}
```

2. **Set environment variables on Windows Server:**

```powershell
# Open PowerShell as Administrator
[System.Environment]::SetEnvironmentVariable('ORACLE_PASSWORD', 'your_new_password', 'Machine')
[System.Environment]::SetEnvironmentVariable('MAPDQPRD_PASSWORD', 'your_new_password', 'Machine')

# Restart IIS/Application to pick up new environment variables
iisreset
```

3. **Or use a `.env` file (Development only):**

Create `.env` file in `monitorportal/` directory:
```bash
ORACLE_USER=icsm_appl
ORACLE_PASSWORD=your_new_password
MAPDQPRD_USER=mapdqprd
MAPDQPRD_PASSWORD=your_new_password
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Update `settings.py` (top of file):
```python
from dotenv import load_dotenv
load_dotenv()
```

---

#### **Method 2: Oracle Wallet (Most Secure - Production)**

1. **Create Oracle Wallet:**

```bash
# On Windows Server
mkstore -wrl C:\Oracle\Wallet -create

# Add credentials
mkstore -wrl C:\Oracle\Wallet -createCredential oracle_level3 icsm_appl your_password
mkstore -wrl C:\Oracle\Wallet -createCredential oracle_mapdqprd mapdqprd your_password
```

2. **Update `oracle_client.py` to use wallet:**

```python
def get_conn() -> oracledb.Connection:
    """
    Connect using Oracle Wallet (most secure)
    """
    dsn = oracledb.makedsn(
        DB_CONFIG["host"],
        DB_CONFIG["port"],
        service_name=DB_CONFIG["service"]
    )
    
    # Connect using wallet - no password in code!
    conn = oracledb.connect(
        dsn=dsn,
        config_dir="C:\\Oracle\\Wallet",
        wallet_location="C:\\Oracle\\Wallet",
        wallet_password=os.getenv("WALLET_PASSWORD")
    )
    return conn
```

---

## 🔗 If Connection Details Change

### **Change Hostname/Port/Service Name:**

**Same file:** `portal/db/oracle_client.py`

**Update the DB_CONFIG dictionaries:**

```python
# Example: New Oracle server
DB_CONFIG = {
    "host": "new-oracle-server.corp.intranet",  # NEW HOST
    "port": 1522,                                # NEW PORT
    "service": "new_service_name",               # NEW SERVICE
    "user": "icsm_appl",
    "password": "icsm_appl_infprd"
}
```

---

## 🧪 Testing After Password Change

### **Test Script:**

Create `test_connection.py` in `monitorportal/` directory:

```python
#!/usr/bin/env python
"""
Test Oracle database connections after password change
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
        print("1. Verify password is correct")
        print("2. Check that database is accessible (ping hostname)")
        print("3. Verify user account is not locked in Oracle")
        print("4. Check firewall rules (port 1521)")
    
    print("="*60 + "\n")
    
    sys.exit(0 if all_ok else 1)
```

### **Run the test:**

```bash
cd c:\Users\ab64033\source\repos\infa_monitor_portal\monitorportal
python test_connection.py
```

**Expected Output:**
```
============================================================
🔍 Testing Oracle Database Connections
============================================================

✅ Level3 Connection: SUCCESS
✅ MAPDQPRD Connection: SUCCESS

============================================================
🔍 Testing Data Access
============================================================

✅ Level3 Data Query: SUCCESS (245 sessions today)
✅ MAPDQPRD Data Query: SUCCESS (3456 ERP runs in history)

============================================================
📊 Summary
============================================================
✅ ALL TESTS PASSED - Connections working!
============================================================
```

---

## ⚠️ Troubleshooting

### **Error: ORA-01017: invalid username/password; logon denied**
- ✅ **Solution:** Password is incorrect, update in `oracle_client.py`
- Verify password with DBA team

### **Error: ORA-12154: TNS:could not resolve the connect identifier**
- ✅ **Solution:** Hostname or service name is wrong
- Check `DB_CONFIG["host"]` and `DB_CONFIG["service"]`
- Ping the hostname: `ping azeus2loraipcp2.corp.intranet`

### **Error: Network adapter could not establish the connection**
- ✅ **Solution:** Can't reach database server
- Check firewall rules (port 1521 must be open)
- Verify VPN connection if accessing remotely

### **Error: Account is locked**
- ✅ **Solution:** Contact DBA to unlock the account
- After too many failed login attempts, Oracle locks accounts

---

## 📋 Production Deployment Checklist

When deploying to production with new credentials:

- [ ] **Backup current `oracle_client.py`** before making changes
- [ ] **Use environment variables** (not hardcoded passwords)
- [ ] **Test in DEV first** before deploying to PROD
- [ ] **Update credentials** during maintenance window
- [ ] **Run connection test script** to verify
- [ ] **Check Django logs** for any connection errors
- [ ] **Test 2-3 pages** in browser to confirm data loads
- [ ] **Document the change** (when password was updated, by whom)
- [ ] **Notify DBA team** that monitoring portal is using new credentials

---

## 🔒 Security Best Practices

### **DO:**
- ✅ Use environment variables or Oracle Wallet in production
- ✅ Rotate passwords quarterly (follow company policy)
- ✅ Use read-only database accounts (SELECT only)
- ✅ Enable audit logging on database accounts
- ✅ Restrict file permissions on `oracle_client.py` (chmod 600)

### **DON'T:**
- ❌ Commit passwords to Git repository
- ❌ Share passwords in email/Slack
- ❌ Use same password for DEV and PROD
- ❌ Give application accounts DDL/DML permissions
- ❌ Store passwords in plain text config files

---

## 📞 Who To Contact

| Issue | Contact |
|-------|---------|
| **Password expired/locked** | DBA Team |
| **New hostname/service name** | Database Administrator |
| **Firewall/network issues** | Network Security Team |
| **Application not connecting** | Application Support Team (You!) |
| **Oracle Wallet setup** | Security Team / DBA |

---

## 📚 Related Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- [DATABRICKS_SETUP_GUIDE.md](DATABRICKS_SETUP_GUIDE.md) - Alternative data source
- [DATA_SOURCE_GUIDE.md](DATA_SOURCE_GUIDE.md) - Understanding data sources
- [PRESENTATION_QA_GUIDE.md](PRESENTATION_QA_GUIDE.md) - Q10: Database credentials storage

---

## 🎯 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│                   PASSWORD UPDATE GUIDE                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 FILE:  monitorportal/portal/db/oracle_client.py         │
│                                                              │
│  🔑 Level3:    DB_CONFIG["password"] = "..."                │
│  🔑 MAPDQPRD:  MAPDQPRD_DB_CONFIG["password"] = "..."       │
│                                                              │
│  🔄 UPDATE:    Edit file → Save → Restart Django            │
│  🧪 TEST:      python test_connection.py                    │
│  ✅ VERIFY:    Open browser → Check page loads              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

**Questions? Problems?**  
Contact: [Your Name/Team]  
Last Updated: March 9, 2026
