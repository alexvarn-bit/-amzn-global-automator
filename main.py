"""Запуск пайплайна публикации с mock-фидом или будущим live-источником."""

import argparse
import html
import logging
import os
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from src.db import PublishedItems
from src.filter import Evaluation, evaluate_product
from src.mock_feed import get_mock_products


LOGGER = logging.getLogger(__name__)

ISRAEL = {
    "max_price_usd": 74.99,
    "free_shipping_required": True,
}

SELECTION_RULES = {
    "min_discount_percent": 0,
    "min_rating": None,
    "min_review_count": 0,
    "ranking_weights": {
        "discount": 0.45,
        "rating": 0.35,
        "review_count": 0.20,
    },
}


def _env_enabled(value: str | None) -> bool:
    """Распознать true-подобные значения переменной окружения."""
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _affiliate_url(url: str, associate_tag: str) -> str:
    """Добавить Amazon associate tag к URL товара."""
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["tag"] = associate_tag

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )


def _format_message(
    product: dict[str, Any],
    associate_tag: str,
    evaluation: Evaluation,
) -> str:
    """Сформировать сообщение на русском языке для Telegram."""
    title = html.escape(str(product["title"]))
    product_url = _affiliate_url(str(product["url"]), associate_tag)
    safe_url = html.escape(product_url, quote=True)
    price = float(product["price"])

    lines = [
        f"<b>{title}</b>",
        f"Цена: <b>${price:.2f} USD</b>",
        "Бесплатная доставка в Израиль",
    ]

    if evaluation.discount_percent > 0:
        lines.append(f"Скидка: {evaluation.discount_percent:.0f}%")

    if product.get("rating") is not None:
        rating = html.escape(str(product["rating"]))
        lines.append(f"Рейтинг: {rating}/5")

    lines.append(f'<a href="{safe_url}">Посмотреть на Amazon</a>')
    return "\n".join(lines)


def _send_telegram_message(
    token: str,
    channel_id: str,
    message: str,
    retries: int = 3,
) -> None:
    """Отправить сообщение в Telegram с ограниченными повторами."""
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "HTML",
    }

    for attempt in range(retries):
        try:
            response = requests.post(endpoint, json=payload, timeout=20)
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise RuntimeError(
                    "Telegram отклонил сообщение: "
                    f"{result.get('description', 'неизвестная ошибка')}"
                )
            return

        except (requests.RequestException, ValueError, RuntimeError) as error:
            if attempt == retries - 1:
                LOGGER.exception("Не удалось отправить сообщение в Telegram")
                raise RuntimeError("Доставка сообщения в Telegram завершилась ошибкой") from error

            delay = 2**attempt
            LOGGER.warning(
                "Ошибка Telegram API; повтор через %s сек.: %s",
                delay,
                error,
            )
            time.sleep(delay)


def _get_live_products() -> list[dict[str, Any]]:
    """Заглушка до подключения Amazon PA-API или другого источника."""
    LOGGER.warning(
        "Источник реальных товаров ещё не подключён; публикация пропущена."
    )
    return []


def run(mock: bool = False) -> None:
    """Отфильтровать, ранжировать и отправить новые товары."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    products = get_mock_products() if mock else _get_live_products()
    if not products:
        LOGGER.info("Нет товаров для обработки.")
        return

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError(
            "Для публикации необходимо задать TELEGRAM_BOT_TOKEN."
        )

    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "@israel_amazon_il")
    associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG", "myproject-il-20")
    database_path = os.getenv("DATABASE_PATH", "data/state.db")
    state = PublishedItems(database_path)

    eligible: list[tuple[float, dict[str, Any], Evaluation]] = []

    for product in products:
        required_fields = ("asin", "title", "url", "price")
        missing_fields = [
            field for field in required_fields
            if product.get(field) in (None, "")
        ]
        if missing_fields:
            LOGGER.warning(
                "Пропуск товара без обязательных полей %s: %s",
                ", ".join(missing_fields),
                product.get("asin", "unknown"),
            )
            continue

        evaluation = evaluate_product(product, ISRAEL, SELECTION_RULES)
        if evaluation.eligible:
            eligible.append((evaluation.score, product, evaluation))
        else:
            LOGGER.info(
                "Товар %s исключён: %s",
                product.get("asin", "unknown"),
                "; ".join(evaluation.reasons),
            )

    eligible.sort(key=lambda item: item[0], reverse=True)

    for _, product, evaluation in eligible:
        asin = str(product["asin"])

        if state.is_published(asin, channel_id):
            LOGGER.info("ASIN %s уже опубликован; пропускаем.", asin)
            continue

        message = _format_message(product, associate_tag, evaluation)
        _send_telegram_message(token, channel_id, message)

        # Записываем ASIN только после успешной отправки.
        state.mark_published(asin, channel_id)
        LOGGER.info("ASIN %s опубликован в канале %s.", asin, channel_id)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mock",
        action="store_true",
        help="использовать тестовые товары из src/mock_feed.py",
    )
    args = parser.parse_args()

    mock_mode = args.mock or _env_enabled(os.getenv("USE_MOCK_DATA"))
    run(mock=mock_mode)


if __name__ == "__main__":
    main()
