"""Deterministic mock feed for the Israel market test path."""

from typing import Any


def get_mock_products() -> list[dict[str, Any]]:
    """Return a representative product twice to test duplicate filtering."""
    product = {
        "asin": "B0MOCKIL001",
        "title": "Беспроводные наушники — тестовое предложение",
        "url": "https://www.amazon.com/dp/B0MOCKIL001",
        "price": 59.99,
        "shipping_price": 0,
        "is_free_shipping": True,
        "regular_price": 89.99,
        "rating": 4.6,
        "review_count": 420,
    }
    return [dict(product), dict(product)]
