# Entry point for one UTC hour: Binance bar + new CryptoPanic articles → FinBERT → SQLite.

import argparse
from datetime import datetime, timedelta, timezone

from data_collection.binance import BinanceCollector
from data_collection.cryptopanic import CryptoPanicCollector
from data_collection.sentiment import FinBertLabeler
from data_collection.storage import SQLiteStore


def collect_hour(database: str, sentiment_model: str) -> None:
    hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    store = SQLiteStore(database)
    store.save_market(BinanceCollector().collect_hour(hour))
    store.save_news(
        FinBertLabeler(sentiment_model).label(
            CryptoPanicCollector().collect_since(hour - timedelta(hours=1))
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect the current UTC hour of market data and labeled news."
    )
    parser.add_argument("--database", default="data/btc_data.db")
    parser.add_argument("--sentiment-model", required=True, help="Path to the FinBERT weights")
    arguments = parser.parse_args()
    collect_hour(arguments.database, arguments.sentiment_model)
