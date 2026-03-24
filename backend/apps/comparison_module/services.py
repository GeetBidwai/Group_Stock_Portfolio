import numpy as np

from apps.portfolio_module.models import PortfolioStock
from apps.shared.services.market_data_service import MarketDataService


class StockComparisonService:
    RANGE_TO_PERIOD = {
        "1m": ("1mo", 22),
        "3m": ("3mo", 66),
        "6m": ("6mo", 132),
        "1y": ("1y", 252),
    }

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

    def compare_portfolio_stocks(self, user, stock_a: str, stock_b: str, range_key: str = "6m") -> dict:
        normalized_range = range_key.lower() if range_key else "6m"
        normalized_range = normalized_range if normalized_range in self.RANGE_TO_PERIOD else "6m"
        first = self._portfolio_metrics(user, stock_a, normalized_range)
        second = self._portfolio_metrics(user, stock_b, normalized_range)
        return {
            "stockA": first,
            "stockB": second,
            "insights": self._build_insights(first, second),
        }

    def _portfolio_metrics(self, user, symbol: str, range_key: str) -> dict:
        chart_period, chart_window = self.RANGE_TO_PERIOD[range_key]
        history = self.market_data.get_history(symbol, period="1y", interval="1d")
        valid_points = [point for point in history if point.get("close") is not None]
        closes = np.array([point["close"] for point in valid_points], dtype=float)
        dates = [str(point["date"])[:10] for point in valid_points]

        if closes.size < 2 or closes.size < min(chart_window, 22):
            raise ValueError(f"Insufficient data available for {symbol.upper()}")

        chart_closes = closes[-chart_window:]
        chart_dates = dates[-chart_window:]

        normalized_data = [
            {
                "date": date_value,
                "value": round(float((price / chart_closes[0]) * 100), 2),
            }
            for date_value, price in zip(chart_dates, chart_closes)
        ]
        daily_returns = np.diff(chart_closes) / chart_closes[:-1]
        current_price = float(chart_closes[-1])
        return_pct = float(((chart_closes[-1] - chart_closes[0]) / chart_closes[0]) * 100)
        volatility = float(np.std(daily_returns) * 100)
        snapshot = self.market_data.get_ticker_snapshot(symbol)

        holding = PortfolioStock.objects.filter(user=user, symbol__iexact=symbol.upper()).order_by("-created_at").first()
        if holding and holding.average_buy_price:
            profit = float(current_price - float(holding.average_buy_price))
        else:
            profit = float(current_price - chart_closes[0])

        return {
            "symbol": symbol.upper(),
            "current_price": round(current_price, 2),
            "return_pct": round(return_pct, 2),
            "profit": round(profit, 2),
            "volatility": round(volatility, 2),
            "normalized_data": normalized_data,
            "performance": self._build_period_returns(closes),
            "market_cap": snapshot.get("market_cap"),
            "pe_ratio": snapshot.get("trailing_pe"),
            "range": range_key,
        }

    def _build_insights(self, first: dict, second: dict) -> list[str]:
        insights = []

        if first["return_pct"] >= second["return_pct"]:
            delta = round(first["return_pct"] - second["return_pct"], 2)
            insights.append(f"{first['symbol']} outperformed {second['symbol']} by {delta}% over the selected period.")
        else:
            delta = round(second["return_pct"] - first["return_pct"], 2)
            insights.append(f"{second['symbol']} outperformed {first['symbol']} by {delta}% over the selected period.")

        if first["volatility"] <= second["volatility"]:
            insights.append(f"{first['symbol']} is less volatile than {second['symbol']}.")
        else:
            insights.append(f"{second['symbol']} is less volatile than {first['symbol']}.")

        first_trend = first["normalized_data"][-1]["value"] - first["normalized_data"][0]["value"]
        second_trend = second["normalized_data"][-1]["value"] - second["normalized_data"][0]["value"]
        if first_trend >= second_trend:
            insights.append(f"{first['symbol']} shows a stronger normalized trend.")
        else:
            insights.append(f"{second['symbol']} shows a stronger normalized trend.")

        return insights

    def _build_period_returns(self, closes: np.ndarray) -> dict:
        return {
            "1m": self._period_return(closes, 22),
            "3m": self._period_return(closes, 66),
            "6m": self._period_return(closes, 132),
        }

    def _period_return(self, closes: np.ndarray, window: int) -> float:
        if closes.size < 2:
            return 0.0
        period = closes[-min(window, closes.size):]
        if period.size < 2:
            return 0.0
        return round(float(((period[-1] - period[0]) / period[0]) * 100), 2)
