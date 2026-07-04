import json
import time
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

EMAIL = "24f2007163@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-bbpad6.example.com"

class handler(BaseHTTPRequestHandler):
    def send_json(self, status_code, payload, allow_origin=None, started=None):
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Request-ID", str(uuid.uuid4()))

        if started is None:
            started = time.perf_counter()
        self.send_header("X-Process-Time", f"{time.perf_counter() - started:.6f}")

        if allow_origin == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Vary", "Origin")

        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        started = time.perf_counter()
        origin = self.headers.get("Origin")

        self.send_response(204)
        self.send_header("X-Request-ID", str(uuid.uuid4()))
        self.send_header("X-Process-Time", f"{time.perf_counter() - started:.6f}")

        if origin == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Vary", "Origin")

        self.end_headers()

    def do_GET(self):
        started = time.perf_counter()
        origin = self.headers.get("Origin")
        query = parse_qs(urlparse(self.path).query)
        raw_values = query.get("values", [None])[0]

        if raw_values is None or raw_values == "":
            self.send_json(
                400,
                {"error": "values is required"},
                origin,
                started
            )
            return

        try:
            values = [int(value.strip()) for value in raw_values.split(",")]
        except ValueError:
            self.send_json(
                400,
                {"error": "values must be comma-separated integers"},
                origin,
                started
            )
            return

        self.send_json(
            200,
            {
                "email": EMAIL,
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values)
            },
            origin,
            started
        )
