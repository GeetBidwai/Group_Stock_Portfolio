import numpy as np

from apps.shared.services.market_data_service import MarketDataService


class StockComparisonService:
    def __init__(self):
        self.market_data = MarketDataService()

    def compare(self, first: str, second: str) -> dict:
        first_metrics = self._metrics(first)
        second_metrics = self._metrics(second)
        winner = first_metrics if first_metrics["score"] >= second_metrics["score"] else second_metrics
        return {
            "primary": first_metrics,
            "secondary": second_metrics,
            "summary": f"{winner['symbol']} appears stronger based on higher return-adjusted performance and lower relative volatility.",
        }

    def _metrics(self, symbol: str) -> dict:
        history = self.market_data.get_history(symbol, period="6mo", interval="1d")
        closes = np.array([point["close"] for point in history if point.get("close") is not None])
        if closes.size < 3:
            return {"symbol": symbol.upper(), "return": None, "volatility": None, "sharpe_ratio": None, "score": -999}
        returns = np.diff(closes) / closes[:-1]
        total_return = float((closes[-1] - closes[0]) / closes[0])
        volatility = float(np.std(returns) * np.sqrt(252))
        sharpe = float((np.mean(returns) / np.std(returns)) * np.sqrt(252)) if np.std(returns) else 0.0
        score = total_return + sharpe - volatility
        return {
            "symbol": symbol.upper(),
            "return": round(total_return, 4),
            "volatility": round(volatility, 4),
            "sharpe_ratio": round(sharpe, 4),
            "score": round(score, 4),
        }
