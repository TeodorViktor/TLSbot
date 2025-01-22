from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Automation script is running.")


def start_server():
    server = HTTPServer(("0.0.0.0", 8000), SimpleServer)
    print("HTTP server started on port 8000.")
    server.serve_forever()



