import math

from django.core.cache import cache

from apps.sentiment_module.services.databricks_client import DatabricksSentimentClient
from apps.sentiment_module.services.finbert_client import FinBERTSentimentClient
from apps.sentiment_module.services.news_service import NewsService
from apps.stock_search_module.models import StockReference

POSITIVE_WORDS = {
    "beat", "beats", "growth", "gains", "gain", "strong", "surge", "upside", "positive", "profit",
    "profits", "record", "expands", "expansion", "bullish", "upgrade", "improves", "improved", "optimistic",
}
NEGATIVE_WORDS = {
    "fall", "falls", "drop", "drops", "weak", "loss", "losses", "miss", "misses", "lawsuit", "downgrade",
    "risk", "risks", "decline", "declines", "bearish", "cuts", "cut", "slump", "warning", "uncertain",
}


class SentimentService:
    def __init__(self):
        self.finbert_client = FinBERTSentimentClient()
        self.databricks_client = DatabricksSentimentClient()

    def analyze_text(self, text: str) -> dict:
        normalized_text = (text or "").strip()
        if not normalized_text:
            return {"label": "Neutral", "score": 0.0, "source": "empty"}

        try:
            result = self.finbert_client.get_sentiment(normalized_text)
            result["source"] = "finbert"
            return result
        except Exception:
            pass

        try:
            result = self.databricks_client.get_sentiment(normalized_text)
            result["source"] = "databricks"
            return result
        except Exception:
            return self._fallback_sentiment(normalized_text)

    def _fallback_sentiment(self, text: str) -> dict:
        try:
            from textblob import TextBlob  # type: ignore

            polarity = float(TextBlob(text).sentiment.polarity)
            return {"label": self._label_from_score(polarity), "score": polarity, "source": "textblob"}
        except Exception:
            pass

        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore

            analyzer = SentimentIntensityAnalyzer()
            compound = float(analyzer.polarity_scores(text)["compound"])
            return {"label": self._label_from_score(compound), "score": compound, "source": "vader"}
        except Exception:
            pass

        tokens = [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()]
        positive_hits = sum(1 for token in tokens if token in POSITIVE_WORDS)
        negative_hits = sum(1 for token in tokens if token in NEGATIVE_WORDS)
        raw_score = (positive_hits - negative_hits) / max(math.sqrt(max(len(tokens), 1)), 1)
        bounded_score = max(min(raw_score, 1.0), -1.0)
        return {"label": self._label_from_score(bounded_score), "score": bounded_score, "source": "keyword"}

    def _label_from_score(self, score: float) -> str:
        if score > 0.15:
            return "Positive"
        if score < -0.15:
            return "Negative"
        return "Neutral"


class SentimentAggregationService:
    CACHE_TIMEOUT_SECONDS = 600

    def __init__(self):
        self.news_service = NewsService()
        self.sentiment_service = SentimentService()

    def analyze_stock(self, stock_symbol: str) -> dict:
        normalized_symbol = stock_symbol.strip().upper()
        if not normalized_symbol:
            return self._error_response("Invalid stock symbol.", status=400)

        cache_key = f"sentiment_analysis:{normalized_symbol}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        news_result = self.news_service.fetch_news(normalized_symbol)
        articles = news_result.get("articles") or []
        news_message = news_result.get("message", "")
        provider_name = news_result.get("provider", "")

        if not articles:
            message = news_message or "No news found for the selected stock."
            neutral_result = {
                "stock": normalized_symbol,
                "stock_name": self._resolve_stock_name(normalized_symbol),
                "overall_sentiment": "Neutral",
                "score": 0,
                "articles": [],
                "message": message,
                "news_provider": provider_name,
                "is_cached_news": bool(news_result.get("used_cache")),
                "summary": {"positive": 0, "negative": 0, "neutral": 100},
            }
            cache.set(cache_key, neutral_result, min(self.CACHE_TIMEOUT_SECONDS, 120))
            return neutral_result

        analyzed_articles = []
        score_total = 0.0
        counts = {"positive": 0, "negative": 0, "neutral": 0}

        for article in articles:
            content = " ".join(filter(None, [article.get("title"), article.get("description")])).strip()
            sentiment = self.sentiment_service.analyze_text(content)
            label_key = sentiment["label"].lower()
            counts[label_key] = counts.get(label_key, 0) + 1
            score_total += float(sentiment["score"])
            analyzed_articles.append(
                {
                    **article,
                    "sentiment": {
                        "label": sentiment["label"],
                        "score": round(float(sentiment["score"]), 4),
                        "source": sentiment.get("source", "fallback"),
                    },
                }
            )

        total = len(analyzed_articles)
        average_score = score_total / total if total else 0.0
        result = {
            "stock": normalized_symbol,
            "stock_name": self._resolve_stock_name(normalized_symbol),
            "overall_sentiment": self.sentiment_service._label_from_score(average_score),
            "score": round(average_score, 4),
            "articles": analyzed_articles,
            "message": news_message,
            "news_provider": provider_name,
            "is_cached_news": bool(news_result.get("used_cache")),
            "summary": {
                "positive": round((counts["positive"] / total) * 100) if total else 0,
                "negative": round((counts["negative"] / total) * 100) if total else 0,
                "neutral": round((counts["neutral"] / total) * 100) if total else 0,
            },
        }
        cache.set(cache_key, result, self.CACHE_TIMEOUT_SECONDS)
        return result

    def _resolve_stock_name(self, stock_symbol: str) -> str:
        base_symbol = stock_symbol.split(".")[0]
        stock_reference = StockReference.objects.filter(symbol__iexact=base_symbol, is_active=True).only("name").first()
        return stock_reference.name if stock_reference else base_symbol

    def _error_response(self, message: str, status: int = 400, stock: str = "") -> dict:
        return {
            "stock": stock,
            "stock_name": stock.split(".")[0] if stock else "",
            "overall_sentiment": "Neutral",
            "score": 0,
            "articles": [],
            "message": "",
            "news_provider": "",
            "is_cached_news": False,
            "summary": {"positive": 0, "negative": 0, "neutral": 0},
            "error": message,
            "error_status": status,
        }
