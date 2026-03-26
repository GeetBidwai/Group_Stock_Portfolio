from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
from django.core.cache import cache
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from apps.shared.services.market_data_service import MarketDataService


class BTCForecastAnalyticsService:
    CACHE_TIMEOUT_SECONDS = 1800
    HISTORY_DAYS = 365
    FORECAST_DAYS = 30
    TICKER = "BTC-USD"
    RANGE_DAYS = {"3m": 90, "6m": 180, "1y": 365}

    def build_payload(self, range_key: str = "3m") -> dict:
        normalized_range = range_key if range_key in self.RANGE_DAYS else "3m"
        cache_key = f"crypto:btc_forecast:{normalized_range}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            full_year_data = self.preprocess_data(self.fetch_btc_data())
            if len(full_year_data) < 30:
                payload = {"error": "Data unavailable"}
            else:
                historical_data = self.filter_data_by_range(full_year_data, normalized_range)
                forecast_values = self.predict_next_30_days(historical_data)
                forecast_data = self.serialize_forecast_data(forecast_values, historical_data["Date"].iloc[-1])
                last_price = float(historical_data["Close"].iloc[-1])
                last_prediction = float(forecast_data[-1]["predicted_price"])
                expected_return = self.calculate_expected_return(last_price, last_prediction)

                payload = {
                    "historical_data": [
                        {
                            "date": row["Date"].strftime("%Y-%m-%d"),
                            "close": round(float(row["Close"]), 2),
                        }
                        for _, row in historical_data.iterrows()
                    ],
                    "forecast_data": forecast_data,
                    "current_price": round(last_price, 2),
                    "predicted_price": round(last_prediction, 2),
                    "expected_return": expected_return,
                    "trend": self.determine_trend(expected_return),
                    "period_returns": self.build_period_returns(full_year_data),
                    "selected_range": normalized_range,
                    "model": "Exponential Smoothing",
                    "forecast_days": self.FORECAST_DAYS,
                }
        except Exception:
            payload = {"error": "Data unavailable"}

        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

    def fetch_btc_data(self) -> pd.DataFrame:
        history = MarketDataService().get_history(self.TICKER, period=f"{self.HISTORY_DAYS}d", interval="1d")
        if not history:
            return pd.DataFrame(columns=["Date", "Close"])
        data_frame = pd.DataFrame(history)
        if data_frame.empty:
            return pd.DataFrame(columns=["Date", "Close"])
        if "date" not in data_frame or "close" not in data_frame:
            return pd.DataFrame(columns=["Date", "Close"])
        return data_frame.rename(columns={"date": "Date", "close": "Close"})[["Date", "Close"]].copy()

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["Date", "Close", "day_index"])

        frame = df.copy()
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.tz_localize(None)
        frame["Close"] = pd.to_numeric(frame["Close"], errors="coerce")
        frame = frame.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)
        frame = self.ensure_date_continuity(frame)
        frame["day_index"] = range(len(frame))
        return frame

    def ensure_date_continuity(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        full_dates = pd.date_range(df["Date"].min(), df["Date"].max(), freq="D")
        frame = (
            df.set_index("Date")[["Close"]]
            .reindex(full_dates)
            .rename_axis("Date")
            .reset_index()
        )
        frame["Close"] = frame["Close"].interpolate(method="linear").ffill().bfill()
        return frame

    def filter_data_by_range(self, df: pd.DataFrame, range_key: str) -> pd.DataFrame:
        days = self.RANGE_DAYS.get(range_key, self.RANGE_DAYS["3m"])
        return df.tail(days).reset_index(drop=True)

    def predict_next_30_days(self, df: pd.DataFrame) -> np.ndarray:
        closes = df["Close"].astype(float).reset_index(drop=True)
        last_price = float(closes.iloc[-1])
        seasonal_periods = 7 if len(closes) >= 21 else None

        if seasonal_periods:
            model = ExponentialSmoothing(
                closes,
                trend="add",
                damped_trend=True,
                seasonal="add",
                seasonal_periods=seasonal_periods,
                initialization_method="estimated",
            )
        else:
            model = ExponentialSmoothing(
                closes,
                trend="add",
                damped_trend=True,
                initialization_method="estimated",
            )

        fitted = model.fit(optimized=True, use_brute=True)
        base_forecast = np.asarray(fitted.forecast(self.FORECAST_DAYS), dtype=float)

        residuals = closes.to_numpy(dtype=float) - np.asarray(fitted.fittedvalues, dtype=float)
        recent_pattern = residuals[-14:] if len(residuals) >= 14 else residuals
        if len(recent_pattern) == 0:
            recent_pattern = np.zeros(1, dtype=float)

        variation = np.resize(recent_pattern, self.FORECAST_DAYS)
        decay = np.linspace(0.35, 0.1, self.FORECAST_DAYS)
        adjusted = base_forecast + (variation * decay)

        anchor_adjustment = last_price - adjusted[0]
        anchor_decay = np.exp(-np.linspace(0, 2.4, self.FORECAST_DAYS))
        adjusted = adjusted + (anchor_adjustment * anchor_decay)
        adjusted[0] = last_price

        smoothed = pd.Series(np.concatenate([[last_price], adjusted])).rolling(window=3, min_periods=1).mean().to_numpy()[1:]
        smoothed[0] = last_price
        smoothed = np.clip(smoothed, a_min=0.0, a_max=None)
        return smoothed

    def serialize_forecast_data(self, predictions: np.ndarray, last_date: pd.Timestamp) -> list[dict]:
        return [
            {
                "date": (last_date + timedelta(days=step)).strftime("%Y-%m-%d"),
                "predicted_price": round(float(predicted_price), 2),
            }
            for step, predicted_price in enumerate(predictions, start=1)
        ]

    def build_period_returns(self, df: pd.DataFrame) -> dict:
        return {
            "3m": self.calculate_period_return(df, 90),
            "6m": self.calculate_period_return(df, 180),
            "1y": self.calculate_period_return(df, 365),
        }

    def calculate_period_return(self, df: pd.DataFrame, days: int) -> float:
        period_frame = df.tail(min(days, len(df)))
        if len(period_frame) < 2:
            return 0.0
        start_price = float(period_frame["Close"].iloc[0])
        end_price = float(period_frame["Close"].iloc[-1])
        return self.calculate_expected_return(start_price, end_price)

    def calculate_expected_return(self, last_price: float, last_prediction: float) -> float:
        if not last_price:
            return 0.0
        return round(((last_prediction - last_price) / last_price) * 100, 2)

    def determine_trend(self, expected_return: float) -> str:
        return "bullish" if expected_return > 0 else "bearish"
