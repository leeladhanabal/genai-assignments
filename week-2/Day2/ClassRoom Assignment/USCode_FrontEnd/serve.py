import json
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer

BACKEND_URL = 'http://localhost:5678/webhook-test/userstory_reviewer'
PORT = 8001

class ProxyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        super().end_headers()

    def do_OPTIONS(self):
        if self.path == '/api/review':
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Max-Age', '86400')
            self.end_headers()
        else:
            super().do_OPTIONS()

    def do_POST(self):
        if self.path != '/api/review':
            self.send_error(404, 'Not Found')
            return

        length = int(self.headers.get('Content-Length', '0'))
        payload = self.rfile.read(length)

        req = urllib.request.Request(
            BACKEND_URL,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as backend_response:
                body = backend_response.read()
                self.send_response(backend_response.status)
                self.send_header('Content-Type', backend_response.headers.get('Content-Type', 'application/json'))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as error:
            body = error.read()
            self.send_response(error.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
        except Exception as error:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Backend request failed', 'details': str(error)}).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f'Serving frontend and proxy on http://localhost:{PORT}')
    httpd.serve_forever()
