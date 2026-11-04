#!/usr/bin/env python3
"""
one.club-dashboard Institutional Server
Serves the Execution Terminal web interface and live REST API.
"""
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from app.db import db

PORT = int(os.environ.get("PORT", 8899))

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        # API Endpoints
        if self.path == "/api/trades":
            self._send_json(db.get_live_trades())
        elif self.path == "/api/studies":
            self._send_json(db.get_historical_studies())
        elif self.path == "/api/metrics":
            self._send_json(db.get_account_metrics() or {})
        elif self.path.startswith("/dashboard_data.json"):
            # Serve live polling stream
            data_file = os.path.join(BASE_DIR, "logs", "dashboard_data.json")
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            else:
                self._send_json({"error": "No data stream active"})
        elif self.path == "/":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def _send_json(self, data):
        content = json.dumps(data, default=str)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

def main():
    print(f"🚀 one.club Execution Terminal Server listening on http://localhost:{PORT}")
    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")

if __name__ == "__main__":
    main()
