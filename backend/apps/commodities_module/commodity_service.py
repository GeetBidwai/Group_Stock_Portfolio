from __future__ import annotations

import logging

import pandas as pd
from django.core.cache import cache
from sklearn.linear_model import LinearRegression

from apps.shared.services.market_data_service import MarketDataService


logger = logging.getLogger(__name__)


class CommodityAnalyticsService:
    CACHE_TIMEOUT_SECONDS = 3600
    GOLD_TICKER = "GC=F"
    SILVER_TICKER = "SI=F"
    FX_TICKER = "USDINR=X"
    HISTORY_PERIOD = "1y"
    HISTORY_INTERVAL = "1d"
    SOURCE_NAME = "Yahoo Finance"
    TROY_OUNCE_TO_GRAMS = 31.1034768
    FORECAST_STEPS = {
        "3m": 66,
        "6m": 132,
        "1y": 252,
    }

    def __init__(self):
        self.market_data = MarketDataService()

    def build_gold_payload(self) -> dict:
        return self._build_commodity_payload(
            "gold",
            self.GOLD_TICKER,
            "Gold Futures",
            unit_label="Rs / 10 gm",
            transform=self._gold_to_inr_per_10g,
        )

    def build_silver_payload(self) -> dict:
        return self._build_commodity_payload(
            "silver",
            self.SILVER_TICKER,
            "Silver Futures",
            unit_label="Rs / kg",
            transform=self._silver_to_inr_per_kg,
        )

    def build_correlation_payload(self) -> dict:
        cache_key = "commodities:correlation"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            gold_df, silver_df = self._load_converted_correlation_frames()
            if len(gold_df) < 2 or len(silver_df) < 2:
                return {"error": "Data unavailable"}

            gold_prices = [{"date": row["date"], "price": round(float(row["close"]), 2)} for _, row in gold_df.iterrows()]
            silver_prices = [{"date": row["date"], "price": round(float(row["close"]), 2)} for _, row in silver_df.iterrows()]
            payload = {
                "correlation": self.calculate_correlation(gold_df, silver_df),
                "gold_prices": gold_prices,
                "silver_prices": silver_prices,
                "source": self.SOURCE_NAME,
            }
        except Exception:
            logger.exception("Commodity correlation payload generation failed")
            payload = {"error": "Data unavailable"}

        if "error" not in payload:
            cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

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

    def train_linear_model(self, prices: pd.Series) -> LinearRegression:
        model = LinearRegression()
        x_values = pd.DataFrame({"day_index": range(len(prices))})
        model.fit(x_values, prices.astype(float))
        return model

    def _build_commodity_payload(self, name: str, ticker: str, display_name: str, unit_label: str, transform) -> dict:
        cache_key = f"commodities:{name}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            data_frame = self._load_history_frame(ticker)
            if len(data_frame) < 2:
                logger.warning("Commodity payload unavailable for %s due to insufficient rows: %s", name, len(data_frame))
                return {"error": "Data unavailable"}

            fx_rate = self._latest_fx_rate()
            converted = self._build_converted_frame(data_frame, transform, fx_rate)

            prices = converted["close"]
            model = self.train_linear_model(prices)
            trend = [
                {
                    "date": row["date"],
                    "price": round(float(model.predict(pd.DataFrame({"day_index": [index]}))[0]), 2),
                }
                for index, (_, row) in enumerate(converted.iterrows())
            ]
            historical = [
                {
                    "date": row["date"],
                    "open": round(float(row["open"]), 2),
                    "close": round(float(row["close"]), 2),
                    "high": round(float(row["high"]), 2),
                    "low": round(float(row["low"]), 2),
                }
                for _, row in converted.iterrows()
            ]
            forecasts = {
                horizon: round(
                    float(model.predict(pd.DataFrame({"day_index": [len(prices) - 1 + step]}))[0]),
                    2,
                )
                for horizon, step in self.FORECAST_STEPS.items()
            }
            payload = {
                "name": display_name,
                "current_price": round(float(prices.iloc[-1]), 2),
                "latest_rate_date": str(converted.iloc[-1]["date"])[:10],
                "historical": historical,
                "regression": trend,
                "forecasts": forecasts,
                "unit": unit_label,
                "source": f"{self.SOURCE_NAME} ({ticker})",
            }
        except Exception:
            logger.exception("Commodity payload generation failed for %s", name)
            payload = {"error": "Data unavailable"}

        if "error" not in payload:
            cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

    def _load_history_frame(self, ticker: str) -> pd.DataFrame:
        history = self.market_data.get_history(ticker, period=self.HISTORY_PERIOD, interval=self.HISTORY_INTERVAL)
        frame = pd.DataFrame(history)
        if frame.empty:
            return frame

        frame["date"] = pd.to_datetime(frame["date"], errors="coerce", utc=True).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
        for column in ["open", "close", "high", "low"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["date", "open", "close", "high", "low"]).sort_values("date").reset_index(drop=True)
        return frame

    def _build_converted_frame(self, data_frame: pd.DataFrame, transform, fx_rate: float) -> pd.DataFrame:
        converted = data_frame.copy()
        for column in ["open", "high", "low", "close"]:
            converted[column] = converted[column].apply(lambda value: transform(value, fx_rate))
        return converted

    def _load_converted_correlation_frames(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        gold_df = self._load_history_frame(self.GOLD_TICKER)
        silver_df = self._load_history_frame(self.SILVER_TICKER)
        if len(gold_df) < 2 or len(silver_df) < 2:
            return gold_df, silver_df

        try:
            fx_rate = self._latest_fx_rate()
            return (
                self._build_converted_frame(gold_df, self._gold_to_inr_per_10g, fx_rate),
                self._build_converted_frame(silver_df, self._silver_to_inr_per_kg, fx_rate),
            )
        except Exception:
            logger.exception("USD/INR conversion unavailable for commodity correlation; falling back to commodity payload history.")
            return self._fallback_correlation_frames()

    def _fallback_correlation_frames(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        gold_payload = self.build_gold_payload()
        silver_payload = self.build_silver_payload()
        return (
            self._history_payload_to_frame(gold_payload.get("historical") or []),
            self._history_payload_to_frame(silver_payload.get("historical") or []),
        )

    def _history_payload_to_frame(self, historical: list[dict]) -> pd.DataFrame:
        frame = pd.DataFrame(historical)
        if frame.empty:
            return frame

        frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        for column in ["open", "close", "high", "low"]:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
        return frame.dropna(subset=["date", "close"]).sort_values("date").reset_index(drop=True)

    def _latest_fx_rate(self) -> float:
        fx_df = self._load_history_frame(self.FX_TICKER)
        if fx_df.empty:
            raise ValueError("USD/INR rate unavailable")
        return float(fx_df["close"].iloc[-1])

    def _gold_to_inr_per_10g(self, usd_per_oz: float, fx_rate: float) -> float:
        inr_per_oz = float(usd_per_oz) * fx_rate
        return inr_per_oz * 10 / self.TROY_OUNCE_TO_GRAMS

    def _silver_to_inr_per_kg(self, usd_per_oz: float, fx_rate: float) -> float:
        inr_per_oz = float(usd_per_oz) * fx_rate
        return inr_per_oz * 1000 / self.TROY_OUNCE_TO_GRAMS
