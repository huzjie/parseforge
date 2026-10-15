"""Zero-dependency HTTP server (stdlib http.server).

Endpoints:
    GET  /health          -> {"status": "ok"}
    GET  /v1/models       -> list of registered backends
    POST /v1/parse        -> {"doc_id", "text", "candidates"} -> structured JSON

The server is intentionally dependency-free (no FastAPI/Flask) so it runs on the
managed Python. It is OpenAI-compatible in spirit (JSON in / JSON out).
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from .engine import OmniParser
from .parse import Document


class ParseHandler(BaseHTTPRequestHandler):
    parser = None

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "backend": self.parser.backend_name})
        elif self.path == "/v1/models":
            from .backends import list_backends
            self._send(200, {"object": "list", "data": list_backends()})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/parse":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw) if raw else {}
            doc = Document(
                doc_id=data.get("doc_id", "api-0"),
                text=data.get("text", ""),
                candidates=data.get("candidates", []),
            )
            result = self.parser.parse(doc)
            self._send(200, result.as_dict())
        except Exception as e:  # pragma: no cover
            self._send(500, {"error": str(e)})


def run_server(host, port, cfg):
    ParseHandler.parser = OmniParser(cfg)
    httpd = HTTPServer((host, port), ParseHandler)
    print("parseforge serving on http://%s:%d" % (host, port), flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    from .config import load_config
    run_server(args.host, args.port, load_config(None))
