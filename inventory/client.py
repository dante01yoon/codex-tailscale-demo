"""사내 재고 API 클라이언트."""

import json
import os
from urllib.request import urlopen

BASE_URL = os.environ.get("INTERNAL_API_URL", "http://localhost:8080")


def fetch_products(base_url=BASE_URL):
    with urlopen(f"{base_url}/v1/products", timeout=5) as resp:
        return json.load(resp)["products"]


def low_stock(products, threshold=5):
    return [p for p in products if p["quantity"] < threshold]


def format_report(products):
    lines = [f"{p['id']} {p['title']}: {p['quantity']}개 ({p['price']:,}원)" for p in products]
    return "\n".join(lines) or "재고 부족 상품 없음"
