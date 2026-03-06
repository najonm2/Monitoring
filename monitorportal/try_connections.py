# try_connections.py - Try different connection variations
import oracledb

def try_connection(host, port, identifier, use_service=True, user="mapdqprd", password="2026NewIDMC"):
    """Try connecting with different configurations"""
    try:
        if use_service:
            dsn = oracledb.makedsn(host, port, service_name=identifier)
            conn_type = "service_name"
        else:
            dsn = oracledb.makedsn(host, port, sid=identifier)
            conn_type = "SID"
        
        print(f"\n🔄 Trying {conn_type}: {identifier}")
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"✅ SUCCESS with {conn_type}: {identifier}")
        print(f"   DSN: {dsn}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "ORA-12505" in error_msg or "DPY-6003" in error_msg:
            print(f"❌ SID not registered: {identifier}")
        elif "ORA-12514" in error_msg or "DPY-6001" in error_msg:
            print(f"❌ Service not registered: {identifier}")
        elif "ORA-01017" in error_msg or "invalid username" in error_msg.lower():
            print(f"❌ Invalid credentials for: {identifier}")
        else:
            print(f"❌ Error: {error_msg[:100]}")
        return False

def main():
    host = "azeus2loraipcp2.corp.intranet"
    port = 1521
    user = "mapdqprd"
    password = "2026NewIDMC"
    
    print("\n" + "="*80)
    print("🧪 TESTING DIFFERENT CONNECTION VARIATIONS")
    print("="*80)
    
    # List of possible database identifiers to try
    variations = [
        ("IDG01P", True),   # service_name uppercase
        ("idg01p", True),   # service_name lowercase
        ("IDG01P", False),  # SID uppercase
        ("idg01p", False),  # SID lowercase
        ("idg01p_app", True),  # pattern like infr01p_app
        ("IDG01P_APP", True),
        ("mapdqprd", True),    # schema name as service
        ("MAPDQPRD", True),
    ]
    
    successful = []
    
    for identifier, use_service in variations:
        if try_connection(host, port, identifier, use_service, user, password):
            successful.append((identifier, "service_name" if use_service else "SID"))
    
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    
    if successful:
        print("\n✅ Successful connections:")
        for identifier, conn_type in successful:
            print(f"   - {conn_type}: {identifier}")
    else:
        print("\n❌ No successful connections found")
        print("\n💡 NEXT STEPS:")
        print("   1. Verify the database name with DBA")
        print("   2. Check if the database is running: select status from v$instance;")
        print("   3. Verify credentials are correct")
        print("   4. Check TNS entries in tnsnames.ora file")

if __name__ == "__main__":
    main()
