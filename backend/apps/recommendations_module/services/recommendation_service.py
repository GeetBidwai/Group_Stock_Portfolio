import hashlib

from django.core.cache import cache

from apps.shared.services.market_data_service import MarketDataService


class RecommendationService:
    CACHE_TIMEOUT_SECONDS = 600
    STOCK_UNIVERSE = [
        {"name": "Tata Consultancy Services", "symbol": "TCS"},
        {"name": "Infosys", "symbol": "INFY"},
        {"name": "Wipro", "symbol": "WIPRO"},
        {"name": "HCL Technologies", "symbol": "HCLTECH"},
        {"name": "Reliance Industries", "symbol": "RELIANCE"},
        {"name": "HDFC Bank", "symbol": "HDFCBANK"},
        {"name": "ICICI Bank", "symbol": "ICICIBANK"},
        {"name": "State Bank of India", "symbol": "SBI"},
        {"name": "ITC", "symbol": "ITC"},
        {"name": "Larsen & Toubro", "symbol": "LT"},
        {"name": "Tata Motors", "symbol": "TATAMOTORS"},
        {"name": "Sun Pharmaceutical", "symbol": "SUNPHARMA"},
        {"name": "Bharti Airtel", "symbol": "BHARTIARTL"},
        {"name": "Asian Paints", "symbol": "ASIANPAINT"},
        {"name": "Maruti Suzuki", "symbol": "MARUTI"},
        {"name": "Axis Bank", "symbol": "AXISBANK"},
        {"name": "Kotak Mahindra Bank", "symbol": "KOTAKBANK"},
        {"name": "Bajaj Finance", "symbol": "BAJFINANCE"},
        {"name": "UltraTech Cement", "symbol": "ULTRACEMCO"},
        {"name": "Titan Company", "symbol": "TITAN"},
    ]

    def __init__(self):
        self.market_data = MarketDataService()

    def fetch_stock_universe(self) -> list[dict]:
        return self.STOCK_UNIVERSE

    def get_sentiment_score(self, stock: dict) -> float:
        try:
            from apps.sentiment_module.services.sentiment_service import SentimentAggregationService

            sentiment_result = SentimentAggregationService().analyze_stock(stock["symbol"])
            if sentiment_result.get("score") is not None:
                return float(sentiment_result["score"])
        except Exception:
            pass
        return self._mock_score(stock["symbol"])

    def get_price_trend(self, stock: dict) -> tuple[float, float]:
        try:
            history = self.market_data.get_history(stock["symbol"], period="7d", interval="1d")
            closes = [float(item["close"]) for item in history if item.get("close") is not None]
            if len(closes) >= 2 and closes[-2] != 0:
                latest = closes[-1]
                previous = closes[-2]
                return (latest - previous) / previous, latest
        except Exception:
            pass
        return 0.0, self._fallback_price(stock["symbol"])

    def calculate_score(self, sentiment: float, trend: float) -> float:
        return (0.6 * sentiment) + (0.4 * trend)

    def generate_recommendations(self) -> dict:
        cache_key = "recommendations:payload"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            recommendations = []
            for stock in self.fetch_stock_universe():
                sentiment = self.get_sentiment_score(stock)
                trend, price = self.get_price_trend(stock)
                score = self.calculate_score(sentiment, trend)
                recommendations.append(
                    {
                        "name": stock["name"],
                        "ticker": f"{stock['symbol']}.NSE",
                        "price": round(float(price), 2),
                        "score": round(float(score), 4),
                        "reason": self._build_reason(sentiment, trend),
                    }
                )

            sorted_items = sorted(recommendations, key=lambda item: item["score"], reverse=True)
            payload = {
                "top_stocks": sorted_items[:10],
                "bottom_stocks": list(reversed(sorted_items[-10:])),
            }
        except Exception:
            payload = self._fallback_payload()

        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

    def _build_reason(self, sentiment: float, trend: float) -> str:
        sentiment_view = "positive" if sentiment > 0.1 else "negative" if sentiment < -0.1 else "mixed"
        trend_view = "uptrend" if trend > 0.01 else "downtrend" if trend < -0.01 else "sideways trend"
        if sentiment > 0.15 and trend > 0:
            return f"Strong sentiment support with a short-term {trend_view}."
        if sentiment < -0.15 and trend <= 0:
            return f"Weak sentiment with a short-term {trend_view}."
        return f"{sentiment_view.title()} sentiment with a recent {trend_view}."

    def _mock_score(self, symbol: str) -> float:
        digest = hashlib.md5(symbol.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) / 0xFFFFFFFF
        return round((bucket * 2) - 1, 4)

    def _fallback_price(self, symbol: str) -> float:
        digest = hashlib.sha1(symbol.encode("utf-8")).hexdigest()
        return 100 + (int(digest[:6], 16) % 4900)

    def _fallback_payload(self) -> dict:
        generated = []
        for stock in self.fetch_stock_universe():
            sentiment = self._mock_score(stock["symbol"])
            trend = self._mock_score(f"{stock['symbol']}:trend") / 10
            score = self.calculate_score(sentiment, trend)
            generated.append(
                {
                    "name": stock["name"],
                    "ticker": f"{stock['symbol']}.NSE",
                    "price": round(self._fallback_price(stock["symbol"]), 2),
                    "score": round(float(score), 4),
                    "reason": self._build_reason(sentiment, trend),
                }
            )
        sorted_items = sorted(generated, key=lambda item: item["score"], reverse=True)
        return {
            "top_stocks": sorted_items[:10],
            "bottom_stocks": list(reversed(sorted_items[-10:])),
        }
