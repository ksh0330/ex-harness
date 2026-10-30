"""Local practice repair desk. One process/port, no external services."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import parse_qs, urlsplit

from fde.records import Conflict, NotFound, Store

HTML = Path(__file__).with_name("web.html")


def make_server(db_path, host="0.0.0.0", port=8000):
    store = Store(db_path)

    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, payload, content_type="application/json; charset=utf-8"):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if "json" in content_type else payload
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(body)

        def read_json(self):
            origin = self.headers.get("Origin")
            if origin:
                parsed_origin = urlsplit(origin)
                if parsed_origin.scheme not in ("http", "https") or parsed_origin.netloc != self.headers.get("Host"):
                    raise ValueError("cross-origin writes are not allowed")
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise ValueError("Content-Type must be application/json")
            raw_length = self.headers.get("Content-Length", "")
            if not raw_length.isdecimal() or self.headers.get("Transfer-Encoding"):
                raise ValueError("Content-Length is required; chunked input is unsupported")
            length = int(raw_length)
            if not 1 <= length <= 16384:
                raise ValueError("JSON body must be 1..16384 bytes")
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def dispatch(self):
            try:
                url = urlsplit(self.path)
                if len(url.query) > 4096:
                    raise ValueError("query too long")
                if self.command == "GET" and url.path == "/":
                    return self.reply(200, HTML.read_bytes(), "text/html; charset=utf-8")
                if self.command == "GET" and url.path == "/health":
                    return self.reply(200, {"status": "ok"})
                if self.command == "GET" and url.path == "/api/summary":
                    return self.reply(200, store.summary())
                if self.command == "GET" and url.path == "/api/items":
                    params = parse_qs(url.query, keep_blank_values=True, max_num_fields=10)
                    if params.keys() - {"q", "status", "order", "limit", "offset"} or any(len(v) != 1 for v in params.values()):
                        raise ValueError("unknown or duplicate query parameter")
                    values = {k: v[0] for k, v in params.items()}
                    for key in ("limit", "offset"):
                        if key in values:
                            values[key] = int(values[key])
                    return self.reply(200, {"items": store.list(**values)})
                if self.command == "POST" and url.path == "/api/items":
                    return self.reply(201, store.add(self.read_json()))
                match = re.fullmatch(r"/api/items/([1-9][0-9]{0,18})", url.path)
                if self.command == "PATCH" and match:
                    body = self.read_json()
                    if not isinstance(body, dict) or set(body) != {"status"}:
                        raise ValueError("PATCH requires status only")
                    return self.reply(200, store.transition(int(match[1]), body["status"]))
                self.reply(404, {"error": "route not found"})
            except NotFound as exc:
                self.reply(404, {"error": str(exc)})
            except Conflict as exc:
                self.reply(409, {"error": str(exc)})
            except (ValueError, UnicodeError) as exc:
                self.reply(400, {"error": str(exc)})
            except sqlite3.Error:
                self.reply(503, {"error": "database unavailable"})

        do_GET = do_POST = do_PATCH = dispatch

        def log_message(self, format, *args):
            # Do not log user input/query strings in this practice app.
            pass

    return HTTPServer((host, port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".run/repairs.sqlite3"))
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port must be 0..65535")
    try:
        with make_server(args.db, port=args.port) as server:
            print(f"Listening on 0.0.0.0:{server.server_port}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
        return 0
    except (OSError, sqlite3.Error) as exc:
        print(f"web: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
