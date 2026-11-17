# mock_feed.py
MOCK_AMAZON_ITEMS = [
    {
        "title": "Anker USB-C Charger",
        "price": 19.99,
        "currency": "USD",
        "shipping_price": 0.00,  # Free shipping test case
        "asin": "B071234XYZ"
    },
    {
        "title": "Heavy Gaming Monitor",
        "price": 250.00,        # Should fail the $74.99 customs limit
        "currency": "USD",
        "shipping_price": 0.00,
        "asin": "B089876ABC"
    },
    {
        "title": "Wireless Mouse",
        "price": 45.00,
        "currency": "USD",
        "shipping_price": 15.00, # Should fail due to paid shipping
        "asin": "B095555DEF"
    }
]
