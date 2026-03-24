import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor

from apps.portfolio_module.models import PortfolioStock
from apps.shared.services.market_data_service import MarketDataService


class StockForecastingService:
    HORIZON_STEPS = {"3M": 63, "6M": 126, "1Y": 252}
    HISTORY_WINDOW = 180

    def forecast(self, symbol: str, model_name: str = "ARIMA", horizon: str = "3M", interval: str = "1d", period: str = "5y") -> dict:
        history = MarketDataService().get_history(symbol, period=period, interval=interval)
        historical_items = self._normalize_history(history)
        series = self._prepare_series(historical_items)
        steps = self.HORIZON_STEPS.get(horizon, 63)

        if isinstance(series, dict):
            return self._error_response(symbol, model_name, horizon, historical_items, series["error"], series["status"])

        try:
            if model_name == "RNN":
                forecast_values = self._forecast_rnn(series, steps)
            else:
                forecast_values = self._forecast_arima(series, steps)
        except Exception as exc:
            print("FORECAST ERROR:", str(exc))
            return self._error_response(symbol, model_name, horizon, historical_items, str(exc), 500)

        future_dates = self._build_future_dates(historical_items[-1]["date"], steps)
        forecast_items = [
            {"date": date_value, "price": round(float(price_value), 2)}
            for date_value, price_value in zip(future_dates, forecast_values)
        ]

        return {
            "symbol": symbol.upper(),
            "model": model_name,
            "horizon": horizon,
            "historical": historical_items[-self.HISTORY_WINDOW:],
            "forecast": forecast_items,
            "history": [{"date": point["date"], "value": point["price"]} for point in historical_items[-self.HISTORY_WINDOW:]],
            "predicted_series": [{"date": point["date"], "value": point["price"]} for point in forecast_items],
            "prediction": round(float(forecast_values[0]), 2) if len(forecast_values) else None,
        }

    def _normalize_history(self, history: list[dict]) -> list[dict]:
        normalized = []
        for point in history:
            close_value = point.get("close")
            if close_value is None:
                continue
            try:
                normalized.append({
                    "date": str(pd.to_datetime(point["date"]).date()),
                    "price": float(close_value),
                })
            except Exception:
                continue
        return normalized

    def _prepare_series(self, historical_items: list[dict]) -> pd.Series | dict:
        data = pd.Series([point["price"] for point in historical_items], dtype="float64")
        data = pd.to_numeric(data, errors="coerce").dropna()
        data = data[np.isfinite(data)]

        print("DATA LENGTH:", len(data))
        print("NULL VALUES:", int(data.isna().sum()))
        print("HEAD:", data.head().tolist())

        if data.empty:
            return {"error": "No historical data available for forecast", "status": 400}
        if len(data) < 30:
            return {"error": "Not enough data for ARIMA", "status": 400}
        if data.nunique() <= 1:
            return {"error": "Data has no variance", "status": 400}

        return data.reset_index(drop=True)

    def _forecast_arima(self, data: pd.Series, steps: int) -> np.ndarray:
        from statsmodels.tsa.arima.model import ARIMA

        data = pd.Series(data).dropna()
        data = pd.to_numeric(data, errors="coerce").dropna()

        if len(data) < 30:
            raise ValueError("Not enough data for ARIMA")
        if data.nunique() <= 1:
            raise ValueError("Data has no variance")

        try:
            log_prices = np.log(data.astype(float))
            model = ARIMA(
                log_prices,
                order=(2, 1, 2),
                trend="t",
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            model_fit = model.fit()
            forecast = np.exp(np.asarray(model_fit.forecast(steps=steps), dtype=float))
            return self._shape_arima_forecast(data, forecast)
        except Exception as exc:
            print("ARIMA ERROR:", str(exc))
            return self._arima_fallback_forecast(data, steps)

    def _forecast_rnn(self, data: pd.Series, steps: int) -> np.ndarray:
        series = pd.Series(data).dropna()
        values = series.to_numpy(dtype=float)

        if len(values) < 30:
            raise ValueError("Not enough data for RNN")
        if pd.Series(values).nunique() <= 1:
            raise ValueError("Data has no variance")

        window = min(30, max(12, len(values) // 10))
        if len(values) <= window + 5:
            return self._moving_average_forecast(series, steps)

        minimum = float(values.min())
        maximum = float(values.max())
        scale = maximum - minimum or 1.0
        normalized = (values - minimum) / scale

        samples = []
        targets = []
        for index in range(len(normalized) - window):
            samples.append(normalized[index:index + window])
            targets.append(normalized[index + window])

        if len(samples) < 10:
            return self._moving_average_forecast(series, steps)

        model = MLPRegressor(
            hidden_layer_sizes=(96, 48),
            activation="tanh",
            solver="adam",
            learning_rate_init=0.001,
            max_iter=600,
            random_state=42,
            early_stopping=True,
        )
        model.fit(np.asarray(samples), np.asarray(targets))

        sequence = normalized[-window:].tolist()
        predictions = []
        for _ in range(steps):
            next_value = float(model.predict([sequence])[0])
            next_value = float(np.clip(next_value, -0.25, 1.25))
            predictions.append(next_value)
            sequence = sequence[1:] + [next_value]

        return np.asarray(predictions) * scale + minimum

    def _moving_average_forecast(self, data: pd.Series, steps: int) -> np.ndarray:
        window = min(10, len(data))
        moving_average = float(pd.Series(data).tail(window).mean())
        return np.asarray([moving_average] * steps, dtype=float)

    def _shape_arima_forecast(self, data: pd.Series, forecast: np.ndarray) -> np.ndarray:
        if len(forecast) == 0:
            return forecast

        history = pd.Series(data, dtype="float64").reset_index(drop=True)
        last_price = float(history.iloc[-1])
        recent_changes = history.diff().dropna()

        if recent_changes.empty:
            forecast[0] = last_price
            return forecast

        recent_window = recent_changes.tail(min(20, len(recent_changes)))
        local_drift = float(recent_window.tail(min(5, len(recent_window))).mean())
        centered_pattern = recent_window - float(recent_window.mean())
        repeated_pattern = np.resize(centered_pattern.to_numpy(dtype=float), len(forecast))

        drift_curve = np.linspace(local_drift * 0.15, local_drift * 0.75, len(forecast))
        wave_curve = np.cumsum(repeated_pattern * np.linspace(0.12, 0.04, len(forecast)))
        adjusted = forecast + drift_curve + wave_curve

        adjusted = pd.Series(np.concatenate([[last_price], adjusted])).ewm(alpha=0.55, adjust=False).mean().to_numpy()[1:]
        adjusted[0] = (adjusted[0] + last_price) / 2
        adjusted = np.clip(adjusted, a_min=0.0, a_max=None)
        return adjusted

    def _arima_fallback_forecast(self, data: pd.Series, steps: int) -> np.ndarray:
        history = pd.Series(data, dtype="float64").reset_index(drop=True)
        last_price = float(history.iloc[-1])
        recent_changes = history.diff().dropna()

        if recent_changes.empty:
            return np.asarray([last_price] * steps, dtype=float)

        local_drift = float(recent_changes.tail(min(10, len(recent_changes))).mean())
        centered_pattern = recent_changes.tail(min(12, len(recent_changes))) - float(recent_changes.tail(min(12, len(recent_changes))).mean())
        repeated_pattern = np.resize(centered_pattern.to_numpy(dtype=float), steps)

        forecast = []
        next_price = last_price
        for index in range(steps):
            next_price += (local_drift * 0.35) + (repeated_pattern[index] * 0.18)
            forecast.append(max(next_price, 0.0))

        return pd.Series(forecast).ewm(alpha=0.6, adjust=False).mean().to_numpy(dtype=float)

    def _error_response(self, symbol: str, model_name: str, horizon: str, historical_items: list[dict], error_message: str, status: int) -> dict:
        return {
            "symbol": symbol.upper(),
            "model": model_name,
            "horizon": horizon,
            "historical": historical_items[-self.HISTORY_WINDOW:],
            "forecast": [],
            "history": [{"date": point["date"], "value": point["price"]} for point in historical_items[-self.HISTORY_WINDOW:]],
            "predicted_series": [],
            "prediction": None,
            "error": error_message,
            "error_status": status,
        }

    def _build_future_dates(self, last_date: str, steps: int) -> list[str]:
        start = pd.to_datetime(last_date) + pd.offsets.BDay(1)
        return [str(date.date()) for date in pd.bdate_range(start=start, periods=steps)]


class PortfolioForecastService:
    def next_day(self, user, portfolio_type_id: int | None = None) -> dict:
        queryset = PortfolioStock.objects.filter(user=user)
        if portfolio_type_id:
            queryset = queryset.filter(portfolio_type_id=portfolio_type_id)
        forecaster = StockForecastingService()
        items = [forecaster.forecast(stock.symbol) for stock in queryset]
        valid_predictions = [item["prediction"] for item in items if item["prediction"] is not None]
        mean_prediction = float(np.mean(valid_predictions)) if valid_predictions else None
        return {"items": items, "portfolio_prediction_average": round(mean_prediction, 2) if mean_prediction else None}
