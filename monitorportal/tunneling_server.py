#!/usr/bin/env python
"""
PASE Monitor Portal - Tunneling Server
Allows corporate network peers to access the portal without external approval
Run this alongside Django: python tunneling_server.py
"""

import socket
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urljoin
import sys

DJANGO_URL = "http://127.0.0.1:8000"
TUNNEL_PORT = 9000

class PortalProxyHandler(SimpleHTTPRequestHandler):
    """Proxy requests to Django server"""
    
    def do_GET(self):
        self._proxy_request()
    
    def do_POST(self):
        self._proxy_request()
    
    def do_PUT(self):
        self._proxy_request()
    
    def do_DELETE(self):
        self._proxy_request()
    
    def _proxy_request(self):
        """Proxy the request to Django"""
        try:
            # Build target URL
            target_url = urljoin(DJANGO_URL, self.path)
            if '?' in self.path:
                query = self.path.split('?', 1)[1]
                target_url = urljoin(DJANGO_URL, self.path.split('?')[0]) + f"?{query}"
            
            # Read request body if present
            content_length = self.headers.get('Content-Length')
            body = None
            if content_length:
                body = self.rfile.read(int(content_length))
            
            # Forward headers
            headers = dict(self.headers)
            headers.pop('Host', None)
            headers.pop('Content-Length', None)
            
            # Make request to Django
            method = self.command
            if method == 'GET':
                resp = requests.get(target_url, headers=headers, timeout=30)
            elif method == 'POST':
                resp = requests.post(target_url, data=body, headers=headers, timeout=30)
            elif method == 'PUT':
                resp = requests.put(target_url, data=body, headers=headers, timeout=30)
            elif method == 'DELETE':
                resp = requests.delete(target_url, headers=headers, timeout=30)
            else:
                self.send_error(405, "Method Not Allowed")
                return
            
            # Send response back to client
            self.send_response(resp.status_code)
            
            # Send response headers
            for header, value in resp.headers.items():
                if header.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(header, value)
            
            self.end_headers()
            
            # Send response body
            if resp.content:
                self.wfile.write(resp.content)
        
        except requests.exceptions.ConnectionError:
            self.send_error(503, "Django server not running on port 8000")
            print("❌ Error: Cannot connect to Django. Make sure it's running on localhost:8000")
        except Exception as e:
            self.send_error(500, str(e))
            print(f"❌ Error: {e}")
    
    def log_message(self, format, *args):
        """Suppress default logging; use custom logging"""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def get_local_ip():
    """Get machine's local network IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    """Start the tunneling server"""
    local_ip = get_local_ip()
    
    print("\n" + "="*70)
    print("🌍 PASE MONITOR PORTAL - CORPORATE NETWORK TUNNELING SERVER")
    print("="*70)
    print(f"\n✅ Django Server:  http://127.0.0.1:8000")
    print(f"✅ Tunnel Server:  http://127.0.0.1:{TUNNEL_PORT}")
    print(f"\n📢 SHARE THIS URL WITH PEERS:")
    print(f"   http://{local_ip}:{TUNNEL_PORT}")
    print(f"\n💡 Peers must be on the same corporate network (Lumen LAN)")
    print(f"💡 URL will work for anyone on the network")
    print("\n" + "="*70)
    print("Press Ctrl+C to stop the server\n")
    
    try:
        server = HTTPServer(('0.0.0.0', TUNNEL_PORT), PortalProxyHandler)
        print(f"🚀 Server starting on port {TUNNEL_PORT}...\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n❌ Server stopped by user")
        sys.exit(0)
    except OSError as e:
        print(f"\n❌ Error: Cannot bind to port {TUNNEL_PORT}: {e}")
        print(f"   Try a different port or check if something is already using port {TUNNEL_PORT}")
        sys.exit(1)


if __name__ == "__main__":
    main()
