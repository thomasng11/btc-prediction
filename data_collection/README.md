# Hourly collection job

`collect_hour.py` is the hourly job. It pulls the latest Binance bar and new CryptoPanic articles, labels them with FinBERT, and writes both to SQLite.

| File | Role |
|---|---|
| `collect_hour.py` | Entry point. One hour of market data and news, then write. |
| `binance.py` | BTC hourly OHLCV, volume, funding, open interest, taker flow, long/short; ETH close. |
| `cryptopanic.py` | Headless Chrome scrape of new Bitcoin articles (timestamp, title, summary). |
| `sentiment.py` | FinBERT on `title. summary` → `positive` / `negative` + confidence. |
| `storage.py` | SQLite tables `market_data` and `news`. |
