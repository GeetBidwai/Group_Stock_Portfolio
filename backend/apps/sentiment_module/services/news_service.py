import os
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

import requests
from django.core.cache import cache
from apps.stock_search_module.models import StockReference


class NewsService:
    CACHE_TIMEOUT_SECONDS = 600
    LAST_GOOD_CACHE_TIMEOUT_SECONDS = 3600

    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "").strip()

    def fetch_news(self, stock_symbol: str) -> dict:
        normalized_symbol = stock_symbol.upper()
        cache_key = f"sentiment_news:{normalized_symbol}"
        last_good_cache_key = f"sentiment_news:last_good:{normalized_symbol}"
        cached = cache.get(cache_key)
        if cached is not None:
            return {
                "articles": cached,
                "message": "",
                "used_cache": True,
                "provider": "cache",
                "rate_limited": False,
            }

        provider_errors = []

        try:
            articles = self._fetch_with_newsapi(normalized_symbol)
            if articles:
                cache.set(cache_key, articles, self.CACHE_TIMEOUT_SECONDS)
                cache.set(last_good_cache_key, articles, self.LAST_GOOD_CACHE_TIMEOUT_SECONDS)
                return {
                    "articles": articles,
                    "message": "",
                    "used_cache": False,
                    "provider": "newsapi",
                    "rate_limited": False,
                }
        except requests.HTTPError as exc:
            provider_errors.append(self._describe_http_error("NewsAPI", exc))
        except requests.RequestException as exc:
            provider_errors.append(f"NewsAPI unavailable: {exc}")

        try:
            articles = self._fetch_with_yahoo_rss(normalized_symbol)
            if articles:
                cache.set(cache_key, articles, self.CACHE_TIMEOUT_SECONDS)
                cache.set(last_good_cache_key, articles, self.LAST_GOOD_CACHE_TIMEOUT_SECONDS)
                return {
                    "articles": articles,
                    "message": "",
                    "used_cache": False,
                    "provider": "yahoo_rss",
                    "rate_limited": False,
                }
        except requests.HTTPError as exc:
            provider_errors.append(self._describe_http_error("Yahoo Finance RSS", exc))
        except requests.RequestException as exc:
            provider_errors.append(f"Yahoo Finance RSS unavailable: {exc}")

        try:
            articles = self._fetch_with_google_news_rss(normalized_symbol)
            if articles:
                cache.set(cache_key, articles, self.CACHE_TIMEOUT_SECONDS)
                cache.set(last_good_cache_key, articles, self.LAST_GOOD_CACHE_TIMEOUT_SECONDS)
                return {
                    "articles": articles,
                    "message": "Using Google News coverage because the primary finance feed is unavailable right now.",
                    "used_cache": False,
                    "provider": "google_news_rss",
                    "rate_limited": False,
                }
        except requests.HTTPError as exc:
            provider_errors.append(self._describe_http_error("Google News RSS", exc))
        except requests.RequestException as exc:
            provider_errors.append(f"Google News RSS unavailable: {exc}")

        last_good = cache.get(last_good_cache_key)
        if last_good:
            message = "Live news providers are temporarily unavailable, so cached sentiment news is being shown."
            cache.set(cache_key, last_good, self.CACHE_TIMEOUT_SECONDS)
            return {
                "articles": last_good,
                "message": message,
                "used_cache": True,
                "provider": "last_good_cache",
                "rate_limited": True,
            }

        message = "News providers are temporarily unavailable or rate-limited. Please try again in a few minutes."
        if provider_errors:
            message = f"{message} ({'; '.join(provider_errors)})"
        return {
            "articles": [],
            "message": message,
            "used_cache": False,
            "provider": "unavailable",
            "rate_limited": True,
        }

    def _fetch_with_newsapi(self, stock_symbol: str) -> list[dict]:
        if not self.newsapi_key:
            return []

        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": stock_symbol,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
            },
            headers={"X-Api-Key": self.newsapi_key},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        articles = payload.get("articles") or []
        return [
            {
                "title": article.get("title") or "",
                "description": article.get("description") or "",
                "url": article.get("url") or "",
                "published_at": article.get("publishedAt") or "",
            }
            for article in articles
            if article.get("title") or article.get("description")
        ]

    def _fetch_with_yahoo_rss(self, stock_symbol: str) -> list[dict]:
        symbol = stock_symbol.upper().strip()
        response = requests.get(
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=IN&lang=en-IN",
            timeout=10,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        articles = []
        for item in root.findall(".//item")[:10]:
            published_at = ""
            pub_date = item.findtext("pubDate", default="")
            if pub_date:
                try:
                    published_at = parsedate_to_datetime(pub_date).isoformat()
                except Exception:
                    published_at = pub_date
            articles.append(
                {
                    "title": item.findtext("title", default=""),
                    "description": item.findtext("description", default=""),
                    "url": item.findtext("link", default=""),
                    "published_at": published_at,
                }
            )
        return articles

    def _fetch_with_google_news_rss(self, stock_symbol: str) -> list[dict]:
        base_symbol = stock_symbol.split(".")[0].upper().strip()
        stock_name = self._resolve_stock_name(base_symbol)
        query = quote_plus(f"{base_symbol} {stock_name} stock")
        response = requests.get(
            f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en",
            timeout=10,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        articles = []
        for item in root.findall(".//item")[:10]:
            published_at = ""
            pub_date = item.findtext("pubDate", default="")
            if pub_date:
                try:
                    published_at = parsedate_to_datetime(pub_date).isoformat()
                except Exception:
                    published_at = pub_date
            articles.append(
                {
                    "title": item.findtext("title", default=""),
                    "description": item.findtext("description", default=""),
                    "url": item.findtext("link", default=""),
                    "published_at": published_at,
                }
            )
        return articles

    def _resolve_stock_name(self, stock_symbol: str) -> str:
        stock_reference = StockReference.objects.filter(symbol__iexact=stock_symbol, is_active=True).only("name").first()
        return stock_reference.name if stock_reference else stock_symbol

    def _describe_http_error(self, provider_name: str, exc: requests.HTTPError) -> str:
        response = exc.response
        if response is not None and response.status_code == 429:
            return f"{provider_name} rate-limited the request"
        if response is not None:
            return f"{provider_name} returned HTTP {response.status_code}"
        return f"{provider_name} request failed"
