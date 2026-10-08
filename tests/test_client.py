import os

import pytest

from inventory import client

SAMPLE = [
    {"id": "A", "title": "가", "quantity": 1, "price": 1000},
    {"id": "B", "title": "나", "quantity": 10, "price": 2000},
]


def test_low_stock():
    assert [p["id"] for p in client.low_stock(SAMPLE)] == ["A"]


@pytest.mark.skipif("INTERNAL_API_URL" not in os.environ, reason="사내 API 주소 없음")
def test_live_report():
    report = client.format_report(client.low_stock(client.fetch_products()))
    assert "원" in report
