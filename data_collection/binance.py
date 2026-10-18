# Public Binance spot/futures pull for one closed UTC hour.

from datetime import datetime

import numpy as np
import requests


class BinanceCollector:
    SPOT_API = "https://api.binance.com/api/v3"
    FUTURES_API = "https://fapi.binance.com/fapi/v1"
    FUTURES_DATA_API = "https://fapi.binance.com/futures/data"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, url: str, **params) -> list:
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _hourly_ohlcv(self, symbol: str, end_ms: int) -> dict[str, float]:
        klines = self._get(
            f"{self.SPOT_API}/klines",
            symbol=symbol,
            interval="1m",
            startTime=end_ms - 3_600_000,
            endTime=end_ms,
            limit=60,
        )
        closes = np.array([float(row[4]) for row in klines])
        return {
            "open": float(klines[0][1]),
            "high": max(float(row[2]) for row in klines),
            "low": min(float(row[3]) for row in klines),
            "close": float(klines[-1][4]),
            "volume": sum(float(row[5]) for row in klines),
            "quote_volume": sum(float(row[7]) for row in klines),
            "trades": sum(int(row[8]) for row in klines),
            "volatility": float(np.diff(np.log(closes)).std()),
        }

    def _btc_derivatives(self, end_ms: int) -> dict[str, float]:
        funding = self._get(
            f"{self.FUTURES_API}/fundingRate",
            symbol="BTCUSDT",
            startTime=end_ms - 86_400_000,
            endTime=end_ms,
            limit=1,
        )[0]
        taker = self._get(
            f"{self.FUTURES_DATA_API}/takerlongshortRatio",
            symbol="BTCUSDT",
            period="1h",
            startTime=end_ms - 3_600_000,
            endTime=end_ms,
            limit=1,
        )[0]
        open_interest = self._get(
            f"{self.FUTURES_DATA_API}/openInterestHist",
            symbol="BTCUSDT",
            period="1h",
            startTime=end_ms - 86_400_000,
            endTime=end_ms,
            limit=1,
        )[0]
        long_short = self._get(
            f"{self.FUTURES_DATA_API}/globalLongShortAccountRatio",
            symbol="BTCUSDT",
            period="1h",
            startTime=end_ms - 3_600_000,
            endTime=end_ms,
            limit=1,
        )[0]
        return {
            "btc_taker_buy_volume": float(taker["buyVol"]),
            "btc_taker_sell_volume": float(taker["sellVol"]),
            "btc_taker_buy_sell_ratio": float(taker["buySellRatio"]),
            "btc_funding_rate": float(funding["fundingRate"]),
            "btc_open_interest": float(open_interest["sumOpenInterest"]),
            "btc_open_interest_value": float(
                open_interest["sumOpenInterestValue"]
            ),
            "btc_long_account": float(long_short["longAccount"]),
            "btc_short_account": float(long_short["shortAccount"]),
            "btc_long_short_ratio": float(long_short["longShortRatio"]),
        }

    def collect_hour(self, end_time: datetime) -> dict[str, float | str]:
        end_ms = int(end_time.timestamp() * 1_000)
        btc = self._hourly_ohlcv("BTCUSDT", end_ms)
        return {
            "timestamp": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            **{f"btc_{name}": value for name, value in btc.items()},
            **self._btc_derivatives(end_ms),
            "eth_close": self._hourly_ohlcv("ETHUSDT", end_ms)["close"],
        }
