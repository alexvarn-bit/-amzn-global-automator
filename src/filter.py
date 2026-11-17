"""Eligibility checks and ranking logic for the Israel launch."""

from dataclasses import dataclass
from math import isfinite, log10
from typing import Any


@dataclass(frozen=True)
class Evaluation:
    eligible: bool
    score: float
    reasons: tuple[str, ...]
    discount_percent: float


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(number) or number < 0:
        return None

    return number


def evaluate_product(
    product: dict[str, Any],
    country: dict[str, Any],
    selection: dict[str, Any],
) -> Evaluation:
    """Apply price/shipping hard gates and calculate a quality ranking score."""
    reasons: list[str] = []

    price = _number(product.get("price"))
    cap = _number(country.get("max_price_usd"))
    if cap is None:
        cap = 74.99

    if price is None or price <= 0:
        reasons.append("missing or invalid price")
    elif price > cap:
        reasons.append(f"price exceeds ${cap:.2f} USD cap")

    shipping_price = _number(product.get("shipping_price"))
    if shipping_price != 0:
        reasons.append("shipping_price must be 0")

    if product.get("is_free_shipping") is not True:
        reasons.append("is_free_shipping must be true")

    regular_price = _number(product.get("regular_price"))
    discount = 0.0
    if price is not None and regular_price is not None and regular_price > price:
        discount = (regular_price - price) / regular_price * 100

    min_discount = _number(selection.get("min_discount_percent"))
    if min_discount is not None and discount < min_discount:
        reasons.append(f"discount is below {min_discount:g}%")

    rating = _number(product.get("rating"))
    min_rating = _number(selection.get("min_rating"))
    if min_rating is not None and (rating is None or rating < min_rating):
        reasons.append(f"rating is below {min_rating:g} or unavailable")

    review_count = _number(product.get("review_count")) or 0.0
    min_review_count = _number(selection.get("min_review_count")) or 0.0
    if review_count < min_review_count:
        reasons.append(f"review count is below {min_review_count:g}")

    weights = selection.get("ranking_weights", {})
    signals = {
        "discount": min(discount / 100, 1.0),
        "rating": min((rating or 0.0) / 5.0, 1.0),
        "review_count": min(log10(review_count + 1) / 4.0, 1.0),
    }

    normalized_weights: dict[str, float] = {}
    for key in signals:
        weight = _number(weights.get(key, 0))
        normalized_weights[key] = weight or 0.0

    total_weight = sum(normalized_weights.values())
    if total_weight:
        score = (
            100
            * sum(signals[key] * normalized_weights[key] for key in signals)
            / total_weight
        )
    else:
        score = 0.0

    return Evaluation(
        eligible=not reasons,
        score=round(score, 2),
        reasons=tuple(reasons),
        discount_percent=round(discount, 2),
    )
