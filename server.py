"""server.py：本机服务（路径到内核方法的映射）。"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from goldenbytes import Packer

CODEC = Packer()
ROUTES = {
    "/pack_delta": lambda payload: {"hex": CODEC.pack_delta(payload["numbers"]).hex()},
    "/unpack_delta": lambda payload: {"numbers": CODEC.unpack_delta(bytes.fromhex(payload["hex"]))},
    "/pack": lambda payload: {"hex": CODEC.pack(payload["numbers"]).hex()},
    "/resync": lambda payload: CODEC.resync(bytes.fromhex(payload["hex"])),
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.reply(CODEC.stats())

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or b"{}")
        route = ROUTES.get(self.path.split("?")[0])
        self.reply(route(payload) if route else {})

    def reply(self, result):
        body = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


    def log_message(self, *args):
        pass


def serve(port: int = 0):
    return HTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print("listening on http://127.0.0.1:%d" % port)
    serve(port).serve_forever()
