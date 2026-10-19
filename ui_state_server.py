from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from core.ui_state import get_audio_level, get_state
from core.ui_controls import get_control_mode, set_control


HOST = "127.0.0.1"
PORT = 8765
ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


class UIStateHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path != "/state":
            self.send_json(404, {"error": "Not found"})
            return

        self.send_json(200, {
            "state": get_state(),
            "audio_level": get_audio_level(),
            "control_mode": get_control_mode(),
        })

    def do_POST(self):
        if self.path != "/control":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 4096:
                self.send_json(400, {"error": "Invalid request body"})
                return

            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            command = payload.get("command", "")
            mode = set_control(command)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc) or "Invalid control command"})
            return

        self.send_json(200, {"ok": True, "control_mode": mode})

    def log_message(self, format, *args):
        # Keep the local UI server quiet.
        return


def start_ui_state_server():
    server = ThreadingHTTPServer((HOST, PORT), UIStateHandler)
    print(f"ARIA UI state server running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    start_ui_state_server()
