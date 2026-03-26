from __future__ import annotations

import logging

import pandas as pd
from django.core.cache import cache
from sklearn.linear_model import LinearRegression

from apps.shared.services.market_data_service import MarketDataService


logger = logging.getLogger(__name__)


class CommodityAnalyticsService:
    CACHE_TIMEOUT_SECONDS = 3600
    GOLD_TICKERS = ("GC=F", "XAUUSD=X", "GLD")
    SILVER_TICKERS = ("SI=F", "XAGUSD=X", "SLV")
    HISTORY_VARIANTS = (
        ("1y", "1d"),
        ("6mo", "1d"),
        ("3mo", "1d"),
        ("1mo", "1d"),
    )

    def __init__(self):
        self.market_data = MarketDataService()

    def fetch_gold_data(self) -> pd.DataFrame:
        return self._fetch_data(self.GOLD_TICKERS)

    def fetch_silver_data(self) -> pd.DataFrame:
        return self._fetch_data(self.SILVER_TICKERS)

    def preprocess_data(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty:
            return data_frame

        frame = data_frame.copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce", utc=True).dt.tz_localize(None)
        for column in ["open", "close", "high", "low"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["date", "open", "close", "high", "low"]).sort_values("date").reset_index(drop=True)
        return frame

    def train_linear_model(self, prices: pd.Series) -> LinearRegression:
        model = LinearRegression()
        x_values = pd.DataFrame({"day_index": range(len(prices))})
        model.fit(x_values, prices.astype(float))
        return model

    def predict_next_day(self, model: LinearRegression, last_index: int) -> float:
        prediction = model.predict(pd.DataFrame({"day_index": [last_index + 1]}))
        return float(prediction[0])

    def generate_scatter_data(self, data_frame: pd.DataFrame) -> list[dict]:
        return [
            {"x": int(index), "y": round(float(row["close"]), 2)}
            for index, (_, row) in enumerate(data_frame.iterrows())
        ]

    def calculate_correlation(self, gold_df: pd.DataFrame, silver_df: pd.DataFrame) -> float:
        merged = pd.merge(
            gold_df[["date", "close"]],
            silver_df[["date", "close"]],
            on="date",
            how="inner",
            suffixes=("_gold", "_silver"),
        )
        if len(merged) < 2:
            return 0.0
        return round(float(merged["close_gold"].corr(merged["close_silver"])), 4)

    def build_gold_payload(self) -> dict:
        return self._build_commodity_payload("gold", self.fetch_gold_data)

    def build_silver_payload(self) -> dict:
        return self._build_commodity_payload("silver", self.fetch_silver_data)

    def build_correlation_payload(self) -> dict:
        cache_key = "commodities:correlation"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            gold_df = self.fetch_gold_data()
            silver_df = self.fetch_silver_data()
            if gold_df.empty or silver_df.empty:
                logger.warning("Commodities correlation unavailable: gold_df=%s silver_df=%s", len(gold_df), len(silver_df))
                return {"error": "Data unavailable"}

            gold_prices = [
                {"date": row["date"].strftime("%Y-%m-%d"), "price": round(float(row["close"]), 2)}
                for _, row in gold_df.iterrows()
            ]
            silver_prices = [
                {"date": row["date"].strftime("%Y-%m-%d"), "price": round(float(row["close"]), 2)}
                for _, row in silver_df.iterrows()
            ]

            payload = {
                "correlation": self.calculate_correlation(gold_df, silver_df),
                "gold_prices": gold_prices,
                "silver_prices": silver_prices,
            }
        except Exception:
            logger.exception("Commodities correlation payload generation failed")
            payload = {"error": "Data unavailable"}

        if "error" not in payload:
            cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

    def _fetch_data(self, tickers: tuple[str, ...] | list[str] | str) -> pd.DataFrame:
        candidates = tickers if isinstance(tickers, (tuple, list)) else [tickers]
        for ticker in candidates:
            for period, interval in self.HISTORY_VARIANTS:
                try:
                    history = self.market_data.get_history(ticker, period=period, interval=interval)
                except Exception:
                    logger.warning(
                        "Commodity history fetch failed for %s (%s/%s)",
                        ticker,
                        period,
                        interval,
                        exc_info=True,
                    )
                    continue
                data_frame = self.preprocess_data(pd.DataFrame(history))
                if len(data_frame) >= 2:
                    logger.info(
                        "Commodity history loaded for %s using %s/%s (%s rows)",
                        ticker,
                        period,
                        interval,
                        len(data_frame),
                    )
                    return data_frame
            logger.warning("Commodity ticker exhausted with insufficient data: %s", ticker)
        return pd.DataFrame()

    def _build_commodity_payload(self, name: str, fetcher) -> dict:
        cache_key = f"commodities:{name}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            data_frame = fetcher()
            if len(data_frame) < 2:
                logger.warning("Commodity payload unavailable for %s due to insufficient rows: %s", name, len(data_frame))
                return {"error": "Data unavailable"}

            prices = data_frame["close"]
            model = self.train_linear_model(prices)
            predicted_price = self.predict_next_day(model, len(prices) - 1)
            regression = [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "price": round(float(model.predict(pd.DataFrame({"day_index": [index]}))[0]), 2),
                }
                for index, (_, row) in enumerate(data_frame.iterrows())
            ]
            historical = [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "open": round(float(row["open"]), 2),
                    "close": round(float(row["close"]), 2),
                    "high": round(float(row["high"]), 2),
                    "low": round(float(row["low"]), 2),
                }
                for _, row in data_frame.iterrows()
            ]
            payload = {
                "current_price": round(float(prices.iloc[-1]), 2),
                "predicted_price": round(predicted_price, 2),
                "historical": historical,
                "scatter_data": self.generate_scatter_data(data_frame),
                "regression": regression,
            }
        except Exception:
            logger.exception("Commodity payload generation failed for %s", name)
            payload = {"error": "Data unavailable"}

        if "error" not in payload:
            cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

