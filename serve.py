#!/usr/bin/env python3
import http.server, os, sys
os.chdir("/Users/Hesham/Documents/quran-analytics")
handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("", 8765), handler)
print(f"Serving at http://localhost:8765")
httpd.serve_forever()
