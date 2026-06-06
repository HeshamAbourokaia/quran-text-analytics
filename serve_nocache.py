#!/usr/bin/env python3
"""Dev server for web/ that sends Cache-Control: no-store, so the browser never
holds a stale data.js. Run from anywhere:  python3 serve_nocache.py [port]
"""
import http.server, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8731
WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=WEB, **k)
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        super().end_headers()
    def log_message(self, *a):
        pass

if __name__ == '__main__':
    print(f"serving {WEB} at http://localhost:{PORT} (no-store)")
    http.server.HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
