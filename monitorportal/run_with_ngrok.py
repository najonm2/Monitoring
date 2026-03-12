"""
PASE Monitor Portal - Temporary Public Access via ngrok
Run this script to expose your Django portal to others temporarily.
"""

from pyngrok import ngrok, conf
import subprocess
import threading
import time
import sys

def run_django_server():
    """Run Django development server"""
    print("🚀 Starting Django development server...")
    subprocess.run([
        sys.executable, 
        "manage.py", 
        "runserver", 
        "8000"
    ])

def main():
    print("=" * 70)
    print("🌐 PASE Monitor Portal - Temporary Public Access")
    print("=" * 70)
    
    # Optional: Set your ngrok auth token (get free token from https://dashboard.ngrok.com)
    # Uncomment and add your token to avoid session limits:
    # ngrok.set_auth_token("YOUR_AUTH_TOKEN_HERE")
    
    try:
        # Start Django server in background thread
        django_thread = threading.Thread(target=run_django_server, daemon=True)
        django_thread.start()
        
        # Give Django a moment to start
        print("⏳ Waiting for Django to start...")
        time.sleep(3)
        
        # Open ngrok tunnel to port 8000
        print("🔗 Opening ngrok tunnel...")
        public_url = ngrok.connect(8000, bind_tls=True)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Your portal is now publicly accessible!")
        print("=" * 70)
        print(f"\n📍 Public URL: {public_url}")
        print(f"📍 Local URL:  http://localhost:8000")
        print("\n📋 Share the public URL with others for temporary access")
        print("⚠️  WARNING: This exposes your portal to the internet!")
        print("🔒 Make sure ALLOWED_HOSTS is configured in settings.py")
        print("\n💡 Press Ctrl+C to stop the server and close the tunnel")
        print("=" * 70 + "\n")
        
        # Keep the script running
        django_thread.join()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down ngrok tunnel and Django server...")
        ngrok.disconnect(public_url)
        print("✅ Tunnel closed. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if port 8000 is already in use")
        print("   2. Get free ngrok token: https://dashboard.ngrok.com/signup")
        print("   3. Add token: ngrok.set_auth_token('YOUR_TOKEN')")
        sys.exit(1)

if __name__ == "__main__":
    main()
