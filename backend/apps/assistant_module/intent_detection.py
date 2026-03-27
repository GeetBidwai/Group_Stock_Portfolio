from __future__ import annotations

import re
from dataclasses import dataclass


STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "best",
    "can",
    "compare",
    "do",
    "for",
    "forecast",
    "get",
    "give",
    "how",
    "i",
    "info",
    "information",
    "is",
    "me",
    "my",
    "news",
    "of",
    "on",
    "performance",
    "predict",
    "prediction",
    "price",
    "risk",
    "sentiment",
    "show",
    "similar",
    "stock",
    "stocks",
    "summary",
    "tell",
    "the",
    "to",
    "vs",
    "versus",
    "what",
}

TIMEFRAME_PATTERNS = (
    r"\b\d+\s*(?:d|day|days|w|week|weeks|m|month|months|y|year|years)\b",
    r"\b(?:today|tomorrow|yesterday)\b",
    r"\b(?:this|next|last)\s+(?:week|month|quarter|year)\b",
    r"\b(?:short|long)\s*term\b",
    r"\b(?:intraday|weekly|monthly|quarterly|yearly|ytd)\b",
)


@dataclass
class IntentDetectionResult:
    intent: str
    entities: dict

    def as_dict(self) -> dict:
        return {
            "intent": self.intent,
            "entities": self.entities,
        }


class IntentDetectionService:
    def detect(self, message: str) -> dict:
        text = str(message or "").strip()
        lowered = text.lower()

        if not text:
            return IntentDetectionResult(intent="unknown", entities={}).as_dict()

        timeframe = self._extract_timeframe(lowered)
        stock_entities = self._extract_stocks(text)

        if self._is_crypto(lowered):
            return self._build("crypto", stock="BTC", timeframe=timeframe)

        if self._is_commodities(lowered):
            commodity = None
            if "gold" in lowered:
                commodity = "gold"
            elif "silver" in lowered:
                commodity = "silver"
            return self._build("commodities", stock=commodity, timeframe=timeframe)

        if self._is_compare(lowered):
            if len(stock_entities) >= 2:
                return self._build("compare_stocks", stocks=stock_entities[:2], timeframe=timeframe)
            return self._build("unknown", timeframe=timeframe)

        if self._is_forecast(lowered):
            if stock_entities:
                return self._build("forecast", stock=stock_entities[0], timeframe=timeframe)
            return self._build("forecast", timeframe=timeframe)

        if self._is_sentiment(lowered):
            if stock_entities:
                return self._build("sentiment", stock=stock_entities[0], timeframe=timeframe)
            return self._build("sentiment", timeframe=timeframe)

        if self._is_clustering(lowered):
            if stock_entities:
                return self._build("clustering", stock=stock_entities[0], timeframe=timeframe)
            return self._build("clustering", timeframe=timeframe)

        if self._is_risk(lowered):
            if stock_entities:
                return self._build("risk_analysis", stock=stock_entities[0], timeframe=timeframe)
            return self._build("risk_analysis", timeframe=timeframe)

        if self._is_portfolio_performance(lowered):
            return self._build("portfolio_performance", timeframe=timeframe)

        if self._is_portfolio_summary(lowered):
            return self._build("portfolio_summary", timeframe=timeframe)

        if self._is_stock_info(lowered):
            if stock_entities:
                return self._build("stock_info", stock=stock_entities[0], timeframe=timeframe)
            return self._build("stock_info", timeframe=timeframe)

        return self._build("unknown", timeframe=timeframe)

    def _build(
        self,
        intent: str,
        *,
        stock: str | None = None,
        stocks: list[str] | None = None,
        timeframe: str | None = None,
    ) -> dict:
        entities: dict[str, object] = {}
        if stock:
            entities["stock"] = stock
        if stocks:
            entities["stocks"] = stocks
        if timeframe:
            entities["timeframe"] = timeframe
        return IntentDetectionResult(intent=intent, entities=entities).as_dict()

    def _extract_timeframe(self, lowered: str) -> str | None:
        for pattern in TIMEFRAME_PATTERNS:
            match = re.search(pattern, lowered)
            if match:
                return match.group(0)
        return None

    def _extract_stocks(self, text: str) -> list[str]:
        normalized = re.sub(r"[^A-Za-z0-9&.\-\s]", " ", text)
        candidates = re.findall(r"\b[A-Za-z][A-Za-z0-9&.\-]{1,20}\b", normalized)

        found: list[str] = []
        for candidate in candidates:
            cleaned = candidate.strip()
            lowered = cleaned.lower()
            if lowered in STOPWORDS:
                continue
            if lowered in {"bitcoin", "btc", "gold", "silver"}:
                continue
            if cleaned.isupper() and len(cleaned) <= 8:
                found.append(cleaned)
                continue
            if len(cleaned) <= 5 and cleaned.isalpha():
                found.append(cleaned.upper())
                continue
            found.append(cleaned[0].upper() + cleaned[1:])

        deduped: list[str] = []
        for item in found:
            if item not in deduped:
                deduped.append(item)
        return deduped

    def _is_crypto(self, lowered: str) -> bool:
        return any(word in lowered for word in {"bitcoin", "btc", "crypto"})

    def _is_commodities(self, lowered: str) -> bool:
        return any(word in lowered for word in {"commodity", "commodities", "gold", "silver"})

    def _is_compare(self, lowered: str) -> bool:
        return any(word in lowered for word in {"compare", "comparison", "versus", " vs ", " vs. "})

    def _is_forecast(self, lowered: str) -> bool:
        return any(word in lowered for word in {"forecast", "predict", "prediction"})

    def _is_sentiment(self, lowered: str) -> bool:
        return "sentiment" in lowered or ("news" in lowered and any(word in lowered for word in {"stock", "market", "share"}))

    def _is_clustering(self, lowered: str) -> bool:
        return any(word in lowered for word in {"cluster", "clustering", "similar stocks", "similar stock"})

    def _is_risk(self, lowered: str) -> bool:
        return "risk" in lowered

    def _is_portfolio_performance(self, lowered: str) -> bool:
        return "portfolio" in lowered and any(
            word in lowered
            for word in {
                "performance",
                "performing",
                "return",
                "returns",
                "profit",
                "loss",
                "gain",
                "gains",
            }
        )

    def _is_portfolio_summary(self, lowered: str) -> bool:
        return "portfolio" in lowered or "investments" in lowered or "holdings" in lowered

    def _is_stock_info(self, lowered: str) -> bool:
        return any(
            phrase in lowered
            for phrase in {
                "stock info",
                "stock information",
                "stock price",
                "share price",
                "price of",
                "tell me about",
                "info about",
                "details of",
            }
        )
