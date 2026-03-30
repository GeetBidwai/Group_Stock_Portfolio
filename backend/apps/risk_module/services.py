import numpy as np

from apps.shared.services.market_data_service import MarketDataService
from apps.shared.services.risk_service import RiskService


class RiskCategorizationService:
    def classify(self, symbol: str) -> dict:
        history = MarketDataService().get_history(symbol, period="1y", interval="1d")
        closes = np.array([point["close"] for point in history if point.get("close") is not None])
        volatility = RiskService().calculate_volatility(closes.tolist()) if closes.size > 2 else None
        category = RiskService().categorize_risk(volatility).lower()
        return {
            "symbol": symbol.upper(),
            "volatility": round(volatility or 0.0, 4),
            "risk_category": category,
            "explanation": f"{symbol.upper()} is classified as {category} risk because annualized volatility is {(volatility or 0.0):.2f}.",
        }
