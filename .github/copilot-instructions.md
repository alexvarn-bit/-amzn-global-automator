## Low-Level Design (LLD) & Component Specs

### 1. Module Structure (`src/`)
- `src/filter.py`: 
  - Input: Raw item dict from Amazon PA-API.
  - Logic: Checks price against `config/countries.yaml` de minimis limits. Drops items exceeding the regional cap (e.g., $74.99 for Israel).
  - Output: Booleans / Filtered item payload.
- `src/db.py`:
  - Storage: SQLite database located at `data/state.db`.
  - Schema: Table `published_items` (`asin` TEXT, `channel_id` TEXT, `published_at` TIMESTAMP).
  - Methods: `is_published(asin, channel_id) -> bool`, `mark_published(asin, channel_id)`.
- `src/publisher.py`:
  - Orchestrator: Loads `config/channels.yaml`, queries API, runs `filter.py`, checks `db.py`, and dispatches via Telegram Bot API with a mandatory `time.sleep(2)` rate-limit delay.

### 2. Error Handling & Logging
- All network calls (Telegram/Amazon) must be wrapped in `try-except` blocks with exponential backoff.
- Missing environment variables (`TELEGRAM_BOT_TOKEN`, etc.) must raise a fatal `EnvironmentError` on startup rather than failing silently.
