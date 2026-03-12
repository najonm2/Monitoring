"""
PASE Monitor Portal - ngrok Public Access
Starts Django and creates ngrok tunnel with auth token
"""

from pyngrok import ngrok
import subprocess
import time
import sys
import os

def main():
    print("=" * 70)
    print("🌐 PASE Monitor Portal - Creating Public Access")
    print("=" * 70)
    
    # Set ngrok auth token
    auth_token = "2sRrkaUwreZydQ1Zwtf4WM70KMp_7gHwimEVSJbEiQ52s6DM3"
    print("\n🔑 Setting ngrok auth token...")
    ngrok.set_auth_token(auth_token)
    print("✅ Auth token configured")
    
    # Start Django server in background
    print("\n🚀 Starting Django development server...")
    django_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Wait for Django to start
    print("⏳ Waiting for Django to initialize (5 seconds)...")
    time.sleep(5)
    
    # Check if Django started successfully
    if django_process.poll() is not None:
        print("\n❌ Django failed to start!")
        print("Check if port 8000 is already in use")
        sys.exit(1)
    
    print("✅ Django server running on http://localhost:8000")
    
    # Create ngrok tunnel
    print("\n🔗 Opening ngrok tunnel...")
    try:
        public_url = ngrok.connect(8000, bind_tls=True)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Portal is Now Publicly Accessible!")
        print("=" * 70)
        print(f"\n📍 Public URL:  {public_url}")
        print(f"📍 Local URL:   http://localhost:8000")
        print("\n📋 Instructions:")
        print("   • Share the PUBLIC URL with others")
        print("   • They can access it from anywhere (no VPN needed)")
        print("   • Tunnel stays open until you press Ctrl+C")
        print("\n⚠️  Security Notes:")
        print("   • Portal is exposed to the internet")
        print("   • ALLOWED_HOSTS is configured for ngrok domains")
        print("   • Monitor access logs for suspicious activity")
        print("\n💡 Press Ctrl+C to stop server and close tunnel")
        print("=" * 70 + "\n")
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            
    except Exception as e:
        print(f"\n❌ Error creating tunnel: {e}")
        django_process.terminate()
        sys.exit(1)
    
    # Cleanup
    print("🔒 Closing ngrok tunnel...")
    ngrok.disconnect(public_url)
    print("🛑 Stopping Django server...")
    django_process.terminate()
    django_process.wait()
    print("✅ Cleanup complete. Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
