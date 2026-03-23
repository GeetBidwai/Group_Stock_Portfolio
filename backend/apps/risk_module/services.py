import numpy as np

from apps.shared.services.market_data_service import MarketDataService


class RiskCategorizationService:
    def classify(self, symbol: str) -> dict:
        history = MarketDataService().get_history(symbol, period="1y", interval="1d")
        closes = np.array([point["close"] for point in history if point.get("close") is not None])
        returns = np.diff(closes) / closes[:-1] if closes.size > 2 else np.array([])
        volatility = float(np.std(returns) * np.sqrt(252)) if returns.size else 0.0
        if volatility < 0.2:
            category = "low"
        elif volatility < 0.35:
            category = "medium"
        else:
            category = "high"
        return {
            "symbol": symbol.upper(),
            "volatility": round(volatility, 4),
            "risk_category": category,
            "explanation": f"{symbol.upper()} is classified as {category} risk because annualized volatility is {volatility:.2f}.",
        }
