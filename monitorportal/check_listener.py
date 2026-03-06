# check_listener.py - Diagnose available Oracle services
import socket

def check_listener():
    """Check if the Oracle listener is accessible"""
    host = "azeus2loraipcp2.corp.intranet"
    port = 1521
    
    print(f"\n🔍 Checking Oracle listener at {host}:{port}")
    print("="*80)
    
    try:
        # Try to connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is OPEN and accepting connections")
            print("\nℹ️  The listener is accessible, but service/SID 'IDG01P' is not registered.")
            print("\n💡 Possible reasons:")
            print("   1. The database name might be different (not IDG01P)")
            print("   2. The database might be down or not registered with the listener")
            print("   3. There might be a typo in the database name")
            print("\n📋 Please verify the correct database identifier:")
            print("   - Is it 'IDG01P' or something else?")
            print("   - Is it a service name or SID?")
            print("   - Is the database currently running?")
        else:
            print(f"❌ Port {port} is CLOSED or unreachable")
            print("   The listener might be down or blocked by firewall")
    
    except socket.timeout:
        print(f"⏱️  Connection timeout - listener at {host}:{port} is not responding")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATION:")
    print("="*80)
    print("Please verify the correct database connection details:")
    print("  1. Run: tnsping IDG01P")
    print("  2. Or check: lsnrctl status")
    print("  3. Or ask DBA for the exact service name/SID for MAPDQPRD schema")
    print("\nAlternatively, provide the full TNS connection string.")

if __name__ == "__main__":
    check_listener()
