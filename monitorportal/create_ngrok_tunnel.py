"""
PASE Monitor Portal - Simple ngrok Setup
Run Django first, then create tunnel
"""

from pyngrok import ngrok, conf
import time
import urllib.request

# Set config path to current directory to avoid permission issues
import os
config_path = os.path.join(os.path.dirname(__file__), ".ngrok2", "ngrok.yml")
conf.get_default().config_path = config_path

# Set auth token
AUTH_TOKEN = "2sRrkaUwreZydQ1Zwtf4WM70KMp_7gHwimEVSJbEiQ52s6DM3"

print("=" * 70)
print("🌐 PASE Monitor Portal - Public Access Setup")
print("=" * 70)

print("\n🔑 Configuring ngrok...")
try:
    ngrok.set_auth_token(AUTH_TOKEN)
    print("✅ Auth token set successfully")
except Exception as e:
    print(f"⚠️  Warning: {e}")
    print("   Continuing anyway...")

# Check if Django is running
print("\n🔍 Checking if Django is running on port 8000...")
try:
    response = urllib.request.urlopen("http://localhost:8000", timeout=2)
    print("✅ Django is running!")
except:
    print("❌ Django is NOT running!")
    print("\n📋 Please start Django first in another terminal:")
    print("   cd monitorportal")
    print("   python manage.py runserver 8000")
    print("\nThen run this script again.")
    exit(1)

# Create tunnel
print("\n🔗 Creating ngrok tunnel...")
try:
    public_url = ngrok.connect(8000, bind_tls=True)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Portal is Now Publicly Accessible!")
    print("=" * 70)
    print(f"\n📍 Public URL:  {public_url}")
    print(f"📍 Local URL:   http://localhost:8000")
    print("\n📋 Share the PUBLIC URL with others!")
    print("   They can access it from anywhere (no VPN needed)")
    print("\n💡 Keep this window open to maintain the tunnel")
    print("   Press Ctrl+C to close the tunnel")
    print("=" * 70 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Closing tunnel...")
        ngrok.disconnect(public_url)
        print("✅ Tunnel closed. Goodbye!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Django is running on port 8000")
    print("2. Check if another ngrok tunnel is already open")
    print("3. Try restarting your terminal")
    exit(1)
