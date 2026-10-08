"""사내 재고 API (데모용). tailnet 안에서만 열린다고 가정한다."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

ITEMS = [
    {"sku": "MUG-01", "name": "머그컵", "stock": 12, "price_krw": 9900},
    {"sku": "TMB-02", "name": "텀블러", "stock": 3, "price_krw": 18900},
    {"sku": "BAG-03", "name": "에코백", "stock": 0, "price_krw": 12000},
    {"sku": "PEN-04", "name": "볼펜 세트", "stock": 41, "price_krw": 4500},
]


def make_handler(routes):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = routes.get(self.path)
            if body is None:
                self.send_response(404)
                body = {"error": "not found", "path": self.path}
            else:
                self.send_response(200)
            data = json.dumps(body, ensure_ascii=False).encode()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


API_ROUTES = {
    "/health": {"status": "ok", "service": "inventory-internal", "version": "2.3.0"},
    "/v2/items": {"items": ITEMS},
}
ADMIN_ROUTES = {"/": {"service": "inventory-admin", "note": "Codex가 닿으면 안 되는 관리자 포트"}}

if __name__ == "__main__":
    admin = ThreadingHTTPServer(("0.0.0.0", 9090), make_handler(ADMIN_ROUTES))
    Thread(target=admin.serve_forever, daemon=True).start()
    print("inventory API :8080, admin :9090", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), make_handler(API_ROUTES)).serve_forever()
