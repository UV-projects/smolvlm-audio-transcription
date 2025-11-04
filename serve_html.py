"""
Simple HTTP server to serve the HTML interface
Run this alongside main_video.py to access from LAN
"""

import http.server
import socketserver
import sys

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == "__main__":
    print(f"\n🌐 Starting HTTP Server on http://0.0.0.0:{PORT}")
    print(f"📂 Serving files from: {__file__.rsplit('/', 1)[0] if '/' in __file__ else __file__.rsplit('\\\\', 1)[0]}")
    print(f"\n🔗 Access from this PC: http://localhost:{PORT}/index_video.html")
    
    # Get local IP
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        print(f"🔗 Access from LAN: http://{local_ip}:{PORT}/index_video.html")
    except:
        print(f"🔗 Access from LAN: http://[YOUR-PC-IP]:{PORT}/index_video.html")
    
    print("\n⚠️  Make sure main_video.py is running!")
    print("⚠️  Allow port 8080 in Windows Firewall if accessing from LAN\n")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
            sys.exit(0)
