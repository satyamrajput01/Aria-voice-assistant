from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from core.ui_state import get_state


HOST = "127.0.0.1"
PORT = 8765


class UIStateHandler(BaseHTTPRequestHandler):

    def send_cors_headers(self):
        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:5173"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path != "/state":
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()
            return

        response = {
            "state": get_state()
        }

        body = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.send_cors_headers()
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_ui_state_server():
    server = ThreadingHTTPServer(
        (HOST, PORT),
        UIStateHandler
    )

    print(
        f"ARIA UI state server running at "
        f"http://{HOST}:{PORT}"
    )

    server.serve_forever()


if __name__ == "__main__":
    start_ui_state_server()