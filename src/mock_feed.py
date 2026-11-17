"""Тестовые товары для проверки израильского пайплайна."""


def get_mock_products() -> list[dict]:
    """Вернуть тестовый товар дважды для проверки дедупликации по ASIN."""
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

    # Повторный ASIN проверяет, что один товар не отправляется дважды.
    return [dict(product), dict(product)]
