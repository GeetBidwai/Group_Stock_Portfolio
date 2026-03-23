from apps.shared.services.market_data_service import MarketDataService


class BTCForecastService:
    def hourly_forecast(self) -> dict:
        history = MarketDataService().get_history("BTC-USD", period="7d", interval="1h")
        closes = [point["close"] for point in history if point.get("close") is not None]
        current_price = closes[-1] if closes else None
        if len(closes) < 10:
            return {"current_price": current_price, "forecast_next_hour": None, "history": history}
        from statsmodels.tsa.arima.model import ARIMA

        model = ARIMA(closes, order=(2, 1, 1))
        fitted = model.fit()
        prediction = float(fitted.forecast()[0])
        return {
            "current_price": round(float(current_price), 2) if current_price else None,
            "forecast_next_hour": round(prediction, 2),
            "history": [{"date": point["date"], "value": point["close"]} for point in history],
            "predicted_point": {"date": "next_hour", "value": round(prediction, 2)},
        }
