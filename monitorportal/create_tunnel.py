"""
Simple ngrok tunnel - Run after Django is started
"""
from pyngrok import ngrok
import urllib.request
import time

print("=" * 70)
print("🔗 PASE Portal - ngrok Tunnel Creator")
print("=" * 70)

# Check if Django is running
print("\n⏳ Checking if Django is running on port 8000...")
max_attempts = 10
for attempt in range(max_attempts):
    try:
        urllib.request.urlopen("http://localhost:8000", timeout=1)
        print("✅ Django is running!")
        break
    except:
        if attempt == 0:
            print("⚠️  Django not detected. Make sure it's running:")
            print("   Terminal 1: cd monitorportal && python manage.py runserver 8000")
        time.sleep(1)
else:
    print("\n❌ Django is not running on port 8000")
    print("\n📋 Please start Django first:")
    print("   cd monitorportal")
    print("   python manage.py runserver 8000")
    input("\nPress Enter to exit...")
    exit(1)

print("\n🔗 Creating ngrok tunnel...")

try:
    # Optional: Add your auth token here to remove limits
    # ngrok.set_auth_token("YOUR_TOKEN_HERE")
    
    # Create tunnel
    public_url = ngrok.connect(8000, bind_tls=True)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Your portal is now publicly accessible!")
    print("=" * 70)
    print(f"\n📍 Public URL: {public_url}")
    print(f"📍 Local URL:  http://localhost:8000")
    print("\n📋 Share the public URL with others for temporary access")
    print("⚠️  Keep this window open to maintain the tunnel")
    print("🔒 Tunnel is active - anyone with URL can access")
    print("💡 Press Ctrl+C to close the tunnel")
    print("=" * 70 + "\n")
    
    # Keep tunnel open
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Closing tunnel...")
    
except KeyboardInterrupt:
    print("\n🛑 Closing tunnel...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Get free ngrok token: https://dashboard.ngrok.com/signup")
    print("   2. Add token in this script: ngrok.set_auth_token('YOUR_TOKEN')")
    print("   3. Or set env variable: NGROK_AUTHTOKEN")
    input("\nPress Enter to exit...")
