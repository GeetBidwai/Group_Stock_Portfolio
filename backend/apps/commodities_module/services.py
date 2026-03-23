import numpy as np

from apps.shared.services.market_data_service import MarketDataService


class GoldSilverCorrelationService:
    def analyze(self) -> dict:
        market_data = MarketDataService()
        gold = market_data.get_history("GC=F", period="5y", interval="1wk")
        silver = market_data.get_history("SI=F", period="5y", interval="1wk")
        pairs = list(zip(gold, silver))
        gold_values = np.array([g["close"] for g, _ in pairs], dtype=float)
        silver_values = np.array([s["close"] for _, s in pairs], dtype=float)
        correlation = float(np.corrcoef(gold_values, silver_values)[0, 1]) if len(pairs) > 1 else 0.0
        slope, intercept = np.polyfit(gold_values, silver_values, 1) if len(pairs) > 1 else (0.0, 0.0)
        return {
            "correlation": round(correlation, 4),
            "line_chart": [{"date": g["date"], "gold": g["close"], "silver": s["close"]} for g, s in pairs],
            "scatter_plot": [{"gold": g["close"], "silver": s["close"]} for g, s in pairs],
            "regression": {"slope": round(float(slope), 4), "intercept": round(float(intercept), 4)},
        }
