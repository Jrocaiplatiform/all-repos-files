import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class IndustrialHUDService:
    layer_id = "layer-09-industrial-hud"
    service_name = "industrial-hud"
    THEMES = {"jroc-electric": "#00D4FF", "dracula": "#BD93F9", "nord": "#88C0D0"}

    def __init__(self, root_dir: Path, kernel):
        self.root_dir = Path(root_dir)
        self.kernel = kernel
        self.active_theme = "jroc-electric"
        self._server = None
        self._thread = None

    def start(self) -> dict:
        return {
            "theme": self.active_theme,
            "legacy_hud": (self.root_dir / "layer-09-industrial-hud" / "jroc_desktop_hud.py").exists(),
        }

    def set_theme(self, name: str) -> str:
        if name not in self.THEMES:
            raise ValueError("Unsupported theme")
        self.active_theme = name
        return self.THEMES[name]

    def start_web_server(self, host: str = "127.0.0.1", port: int = 0) -> dict:
        if host not in {"127.0.0.1", "localhost"}:
            raise ValueError("HUD bridge may only bind to loopback")
        kernel = self.kernel

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                return

            def do_GET(self):
                token = self.headers.get("X-JROC-Token", "")
                if not kernel.verify_token(token):
                    self.send_response(401)
                    self.end_headers()
                    return
                body = json.dumps({"ok": True, "data": kernel.health()}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self._server = ThreadingHTTPServer((host, port), Handler)
        _, actual_port = self._server.server_address
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return {"host": host, "port": actual_port}

    def health_check(self) -> dict:
        return {"theme": self.active_theme, "server_running": self._server is not None}

    def stop(self) -> dict:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        return {"status": "stopped"}
