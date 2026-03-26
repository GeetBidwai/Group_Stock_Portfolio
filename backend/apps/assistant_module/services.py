from __future__ import annotations

import logging
import re

from apps.comparison_module.services import StockComparisonService
from apps.forecasting_module.services import StockForecastingService
from apps.portfolio_module.models import PortfolioStock
from apps.assistant_module.rag.rag_pipeline import get_assistant_rag_pipeline
from apps.stocks_module.models import PortfolioEntry, Stock
from apps.stocks_module.services import StocksPortfolioService


logger = logging.getLogger(__name__)


class PersonalAssistantService:
    MAX_HISTORY_MESSAGES = 8

    def reply(self, user, message: str, history: list[dict] | None = None) -> dict:
        cleaned_message = (message or "").strip()
        sanitized_history = self._sanitize_history(history or [])
        holdings = self._portfolio_holdings(user)

        direct_reply = self._direct_reply(user, cleaned_message, holdings)
        if direct_reply:
            return {
                "reply": direct_reply,
                "mode": "project_data",
            }

        rag_reply = self._rag_reply(cleaned_message, sanitized_history)
        if rag_reply:
            return rag_reply

        return {
            "reply": self._default_reply(holdings),
            "mode": "fallback",
        }

    def _sanitize_history(self, history: list[dict]) -> list[dict]:
        sanitized = []
        for item in history[-self.MAX_HISTORY_MESSAGES:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "").strip().lower()
            content = str(item.get("content") or "").strip()
            if role not in {"user", "assistant"} or not content:
                continue
            sanitized.append({"role": role, "content": content})
        return sanitized

    def _portfolio_holdings(self, user) -> list[dict]:
        entries = list(
            PortfolioEntry.objects.filter(user=user)
            .select_related("stock", "sector")
            .order_by("stock__symbol")
        )
        manual = list(
            PortfolioStock.objects.filter(user=user)
            .select_related("portfolio_type")
            .order_by("symbol")
        )

        known_symbols = {entry.stock.symbol.upper(): entry.stock.name for entry in entries}
        missing_symbols = [
            manual_item.symbol.upper()
            for manual_item in manual
            if manual_item.symbol.upper() not in known_symbols
        ]
        if missing_symbols:
            catalog_names = dict(
                Stock.objects.filter(symbol__in=missing_symbols).values_list("symbol", "name")
            )
        else:
            catalog_names = {}

        deduped: dict[str, dict] = {}
        for entry in entries:
            symbol = entry.stock.symbol.upper()
            deduped[symbol] = {
                "symbol": symbol,
                "name": entry.stock.name or symbol,
                "sector": entry.sector.name if entry.sector else None,
            }

        for manual_item in manual:
            symbol = manual_item.symbol.upper()
            if symbol in deduped:
                continue
            deduped[symbol] = {
                "symbol": symbol,
                "name": manual_item.company_name or catalog_names.get(symbol) or symbol,
                "sector": manual_item.portfolio_type.sector.name if manual_item.portfolio_type and manual_item.portfolio_type.sector else None,
            }

        return list(deduped.values())

    def _direct_reply(self, user, message: str, holdings: list[dict]) -> str | None:
        text = message.strip().lower()
        if not text:
            return "Ask me about your portfolio, holdings, comparison, risk view, or forecast."

        if text in {"hi", "hello", "hey", "hii"}:
            return "Hi! I am your portfolio assistant. Ask me about your holdings, sectors, risk view, comparison, or forecast."

        if "what can you do" in text or "help" == text:
            return self._default_reply(holdings)

        if ("portfolio" in text or "holdings" in text or "stocks do i have" in text) and any(
            phrase in text for phrase in {"what", "show", "list", "which", "my"}
        ):
            return self._portfolio_list_reply(holdings)

        if ("how many" in text or "count" in text) and ("stock" in text or "holding" in text or "portfolio" in text):
            return self._portfolio_count_reply(holdings)

        if "sector" in text:
            return self._sector_reply(holdings)

        if any(phrase in text for phrase in {"top gainer", "best performer", "top performer", "top loser", "worst performer", "risk"}):
            return self._insights_reply(user, text)

        if "compare" in text:
            return self._compare_reply(user, text, holdings)

        if any(word in text for word in {"forecast", "prediction", "predict"}):
            return self._forecast_reply(text, holdings)

        return None

    def _portfolio_list_reply(self, holdings: list[dict]) -> str:
        if not holdings:
            return "Your portfolio is empty right now. Add a few stocks first, and then I can help analyze them."

        preview = ", ".join(
            f"{item['symbol']} ({item['name']})" for item in holdings[:8]
        )
        extra = len(holdings) - 8
        if extra > 0:
            preview = f"{preview}, and {extra} more."
        else:
            preview = f"{preview}."
        return f"You currently have {len(holdings)} portfolio stocks: {preview}"

    def _portfolio_count_reply(self, holdings: list[dict]) -> str:
        if not holdings:
            return "You do not have any portfolio stocks yet."
        return f"You currently have {len(holdings)} stocks in your portfolio."

    def _sector_reply(self, holdings: list[dict]) -> str:
        if not holdings:
            return "I cannot summarize sectors yet because your portfolio is empty."

        counts: dict[str, int] = {}
        for item in holdings:
            sector = item["sector"] or "Unassigned"
            counts[sector] = counts.get(sector, 0) + 1

        ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
        summary = ", ".join(f"{name}: {count}" for name, count in ranked[:6])
        top_name, top_count = ranked[0]
        return f"Your portfolio sectors are {summary}. Your largest sector is {top_name} with {top_count} stock(s)."

    def _insights_reply(self, user, text: str) -> str:
        insights = StocksPortfolioService().portfolio_insights(user)
        if "risk" in text:
            risk_breakdown = insights.get("risk_breakdown") or {}
            return (
                "Your portfolio risk breakdown is "
                f"low: {risk_breakdown.get('low', 0)}, "
                f"medium: {risk_breakdown.get('medium', 0)}, "
                f"high: {risk_breakdown.get('high', 0)}."
            )

        if any(phrase in text for phrase in {"top gainer", "best performer", "top performer"}):
            top_gainer = (insights.get("top_gainers") or [None])[0]
            if not top_gainer:
                return "I could not find a top gainer right now."
            return (
                f"Your top gainer right now is {top_gainer['symbol']} at "
                f"{top_gainer['change_pct']}% with risk marked as {top_gainer['risk_category']}."
            )

        if any(phrase in text for phrase in {"top loser", "worst performer"}):
            top_loser = (insights.get("top_losers") or [None])[0]
            if not top_loser:
                return "I could not find a top loser right now."
            return (
                f"Your top loser right now is {top_loser['symbol']} at "
                f"{top_loser['change_pct']}% with risk marked as {top_loser['risk_category']}."
            )

        top_gainer = (insights.get("top_gainers") or [None])[0]
        top_loser = (insights.get("top_losers") or [None])[0]
        parts = []
        if top_gainer:
            parts.append(f"top gainer: {top_gainer['symbol']} ({top_gainer['change_pct']}%)")
        if top_loser:
            parts.append(f"top loser: {top_loser['symbol']} ({top_loser['change_pct']}%)")
        if not parts:
            return "I could not summarize your current movers right now."
        return "Here is your current portfolio snapshot: " + ", ".join(parts) + "."

    def _compare_reply(self, user, text: str, holdings: list[dict]) -> str:
        symbols = self._extract_symbols(text, holdings)
        if len(symbols) < 2:
            if len(holdings) >= 2:
                if any(phrase in text for phrase in {"top stocks", "my stocks", "best stocks", "top two"}):
                    symbols = [holdings[0]["symbol"], holdings[1]["symbol"]]
                else:
                    sample = [item["symbol"] for item in holdings[:4]]
                    return f"Tell me the two portfolio symbols you want to compare, for example: compare {sample[0]} and {sample[1]}."
            return "Add at least two portfolio stocks first, then ask me to compare two symbols."

        first, second = symbols[:2]
        try:
            result = StockComparisonService().compare_portfolio_stocks(user, first, second, "6m")
        except Exception:
            return f"I could not compare {first} and {second} right now."

        stock_a = result.get("stockA") or {}
        stock_b = result.get("stockB") or {}
        insights = result.get("insights") or []
        leading_symbol = first if (stock_a.get("return_pct") or 0) >= (stock_b.get("return_pct") or 0) else second
        insight_line = insights[0] if insights else f"{leading_symbol} is currently leading over the selected period."
        return (
            f"Comparison for {first} vs {second}: "
            f"{first} return {stock_a.get('return_pct')}%, volatility {stock_a.get('volatility')}%. "
            f"{second} return {stock_b.get('return_pct')}%, volatility {stock_b.get('volatility')}%. "
            f"{insight_line}"
        )

    def _forecast_reply(self, text: str, holdings: list[dict]) -> str:
        symbols = self._extract_symbols(text, holdings)
        if not symbols:
            return "Tell me which portfolio stock you want a forecast for, for example: forecast TCS."

        symbol = symbols[0]
        try:
            forecast = StockForecastingService().forecast(symbol=symbol, horizon="3M")
        except Exception:
            return f"I could not generate a forecast for {symbol} right now."

        if forecast.get("error"):
            return f"I could not generate a forecast for {symbol}: {forecast['error']}."

        prediction = forecast.get("prediction")
        historical = forecast.get("historical") or []
        if prediction is None or not historical:
            return f"I could not generate a forecast for {symbol} right now."

        current_price = historical[-1]["price"]
        direction = "up" if prediction >= current_price else "down"
        return (
            f"For {symbol}, the latest available price is {round(float(current_price), 2)} and the short forecast points {direction} "
            f"to about {round(float(prediction), 2)} over the selected horizon."
        )

    def _extract_symbols(self, text: str, holdings: list[dict]) -> list[str]:
        symbol_map = {item["symbol"].upper(): item for item in holdings}
        found: list[str] = []

        for symbol, item in symbol_map.items():
            if re.search(rf"\b{re.escape(symbol.lower())}\b", text.lower()):
                found.append(symbol)
                continue

            if item["name"]:
                normalized_name = re.sub(r"[^a-z0-9]+", " ", item["name"].lower()).strip()
                if normalized_name and normalized_name in re.sub(r"[^a-z0-9]+", " ", text.lower()):
                    found.append(symbol)

        if found:
            return list(dict.fromkeys(found))

        token_matches = re.findall(r"\b[A-Za-z][A-Za-z0-9.&-]{1,14}\b", text.upper())
        return [token for token in token_matches if token in symbol_map]

    def _default_reply(self, holdings: list[dict]) -> str:
        if holdings:
            sample = ", ".join(item["symbol"] for item in holdings[:4])
            return (
                "I can help with your portfolio after login. Ask things like: "
                f"'What is in my portfolio?', 'How many stocks do I have?', 'Compare {sample}', "
                "'What is my risk breakdown?', or 'Forecast <symbol>'."
            )
        return (
            "I can help with your portfolio after login. Ask me about your holdings, sectors, comparison, risk, or forecast."
        )

    def _rag_reply(self, message: str, history: list[dict]) -> dict | None:
        if not message:
            return None
        try:
            rag_pipeline = get_assistant_rag_pipeline()
            return rag_pipeline.ask(message=message, history=history)
        except Exception:
            logger.exception("Assistant RAG pipeline failed; falling back to deterministic assistant.")
            return None
