# SQLite writes for the hourly market bar and labeled articles.

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


MARKET_COLUMNS = [
    "timestamp",
    "btc_open",
    "btc_high",
    "btc_low",
    "btc_close",
    "btc_volume",
    "btc_quote_volume",
    "btc_trades",
    "btc_volatility",
    "btc_taker_buy_volume",
    "btc_taker_sell_volume",
    "btc_taker_buy_sell_ratio",
    "btc_funding_rate",
    "btc_open_interest",
    "btc_open_interest_value",
    "btc_long_account",
    "btc_short_account",
    "btc_long_short_ratio",
    "eth_close",
]


class SQLiteStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _setup(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS market_data (
                    timestamp TEXT PRIMARY KEY,
                    btc_open REAL,
                    btc_high REAL,
                    btc_low REAL,
                    btc_close REAL,
                    btc_volume REAL,
                    btc_quote_volume REAL,
                    btc_trades INTEGER,
                    btc_volatility REAL,
                    btc_taker_buy_volume REAL,
                    btc_taker_sell_volume REAL,
                    btc_taker_buy_sell_ratio REAL,
                    btc_funding_rate REAL,
                    btc_open_interest REAL,
                    btc_open_interest_value REAL,
                    btc_long_account REAL,
                    btc_short_account REAL,
                    btc_long_short_ratio REAL,
                    eth_close REAL,
                    created_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS news (
                    url TEXT PRIMARY KEY,
                    timestamp TEXT,
                    title TEXT,
                    summary TEXT,
                    label TEXT,
                    confidence REAL,
                    created_at TEXT
                )
                """
            )

    def save_market(self, market: dict) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        placeholders = ", ".join("?" for _ in MARKET_COLUMNS)
        with self._connect() as connection:
            connection.execute(
                f"""
                INSERT OR REPLACE INTO market_data
                ({", ".join(MARKET_COLUMNS)}, created_at)
                VALUES ({placeholders}, ?)
                """,
                [market[column] for column in MARKET_COLUMNS] + [created_at],
            )

    def save_news(self, articles: list[dict]) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO news
                (url, timestamp, title, summary, label, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        article["url"],
                        article["timestamp"].isoformat(),
                        article["title"],
                        article["summary"],
                        article["label"],
                        article["confidence"],
                        created_at,
                    )
                    for article in articles
                ],
            )
