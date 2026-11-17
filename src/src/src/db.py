"""SQLite-хранилище для предотвращения повторной публикации ASIN."""


import sqlite3
from pathlib import Path


class PublishedItems:
    """Хранит опубликованные пары ASIN и Telegram-канал."""

    def __init__(self, path: str = "data/state.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS published_items (
                    asin TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    published_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (asin, channel_id)
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def is_published(self, asin: str, channel_id: str) -> bool:
        """Проверить, публиковался ли ASIN в этом канале."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM published_items
                WHERE asin = ? AND channel_id = ?
                """,
                (asin, channel_id),
            ).fetchone()

        return row is not None

    def mark_published(self, asin: str, channel_id: str) -> None:
        """Записать успешно опубликованный ASIN."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO published_items (asin, channel_id)
                VALUES (?, ?)
                """,
                (asin, channel_id),
            )
