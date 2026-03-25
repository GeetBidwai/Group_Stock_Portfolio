from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import yfinance as yf
from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.risk_module.services import RiskCategorizationService
from apps.shared.services.market_data_service import MarketDataService
from apps.stocks_module.models import PortfolioEntry, Sector, Stock


class StocksPricingService:
    CACHE_TIMEOUT_SECONDS = 900
    MAX_WORKERS = 10

    def get_stocks_with_prices(self, sector: Sector) -> list[dict]:
        stocks = list(sector.stocks.filter(is_active=True).order_by("symbol"))
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            price_payloads = list(executor.map(lambda item: self._snapshot_for_stock(item, sector.market.code), stocks))
        return price_payloads

    def _snapshot_for_stock(self, stock: Stock, market_code: str) -> dict:
        cache_key = f"stocks-module:price:{market_code}:{stock.symbol}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            ticker_symbol = self._ticker_symbol(stock.symbol, market_code)
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.fast_info or {}
        except Exception:
            info = {}

        current_price = None
        currency = None
        try:
            current_price = info.get("lastPrice") or info.get("regularMarketPrice")
            currency = info.get("currency")
        except Exception:
            current_price = None
            currency = None

        if current_price is None:
            try:
                history = ticker.history(period="5d", interval="1d")
                if not history.empty and "Close" in history:
                    current_price = float(history["Close"].dropna().iloc[-1])
            except Exception:
                current_price = None

        payload = {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "exchange": stock.exchange,
            "sector_id": stock.sector_id,
            "sector_name": stock.sector.name if stock.sector else None,
            "market_code": market_code,
            "current_price": round(float(current_price), 2) if current_price is not None else None,
            "currency": currency or ("INR" if market_code == "IN" else "USD"),
        }
        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

    def _ticker_symbol(self, symbol: str, market_code: str) -> str:
        normalized_symbol = symbol.upper().strip()
        if market_code == "IN" and "." not in normalized_symbol:
            return f"{normalized_symbol}.NS"
        return normalized_symbol


class StocksPortfolioService:
    INSIGHTS_CACHE_TIMEOUT_SECONDS = 300

    @transaction.atomic
    def add_to_portfolio(self, user, stock_id: int) -> dict:
        stock = (
            Stock.objects.select_related("sector__market")
            .filter(id=stock_id, is_active=True)
            .first()
        )
        if not stock:
            raise ValidationError("Selected stock was not found.")

        if stock.sector_id is None:
            raise ValidationError("Selected stock is not mapped to a sector.")

        if PortfolioEntry.objects.filter(user=user, stock=stock).exists():
            raise ValidationError("This stock is already present in your portfolio.")

        entry = PortfolioEntry.objects.create(
            user=user,
            stock=stock,
            sector=stock.sector,
        )
        return {
            "message": "Stock added to portfolio.",
            "portfolio_entry_id": entry.id,
            "sector_id": stock.sector.id,
            "sector_name": stock.sector.name,
            "stock_id": stock.id,
            "symbol": stock.symbol,
        }

    @transaction.atomic
    def remove_from_portfolio(self, user, entry_id: int) -> dict:
        entry = (
            PortfolioEntry.objects.select_related("stock", "sector")
            .filter(id=entry_id, user=user)
            .first()
        )
        if not entry:
            raise ValidationError("Selected portfolio stock was not found.")

        symbol = entry.stock.symbol
        sector_name = entry.sector.name
        entry.delete()
        return {
            "message": "Stock removed from portfolio.",
            "symbol": symbol,
            "sector_name": sector_name,
        }

    def grouped_portfolio(self, user) -> list[dict]:
        entries = list(
            PortfolioEntry.objects.filter(user=user)
            .select_related("stock", "sector", "sector__market")
            .order_by("sector__name", "stock__symbol")
        )
        grouped = {}
        for entry in entries:
            key = entry.sector_id
            if key not in grouped:
                grouped[key] = {
                    "sector": {
                        "id": entry.sector.id,
                        "name": entry.sector.name,
                        "market": entry.sector.market.name,
                        "market_code": entry.sector.market.code,
                    },
                    "items": [],
                }
            grouped[key]["items"].append(
                {
                    "id": entry.id,
                    "stock_id": entry.stock.id,
                    "symbol": entry.stock.symbol,
                    "name": entry.stock.name,
                    "exchange": entry.stock.exchange,
                    "added_at": entry.added_at,
                }
            )
        return list(grouped.values())

    def portfolio_insights(self, user) -> dict:
        cache_key = f"stocks-module:portfolio-insights:{user.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        entries = list(
            PortfolioEntry.objects.filter(user=user)
            .select_related("stock", "sector", "sector__market")
            .order_by("sector__name", "stock__symbol")
        )
        if not entries:
            payload = {
                "risk_breakdown": {"low": 0, "medium": 0, "high": 0},
                "top_gainers": [],
                "top_losers": [],
            }
            cache.set(cache_key, payload, self.INSIGHTS_CACHE_TIMEOUT_SECONDS)
            return payload

        market_data = MarketDataService()
        risk_service = RiskCategorizationService()
        risk_breakdown = {"low": 0, "medium": 0, "high": 0}
        movers = []

        for entry in entries:
            symbol = entry.stock.symbol
            market_symbol = self._market_symbol(entry.stock)

            try:
                risk_payload = risk_service.classify(market_symbol)
                risk_category = risk_payload.get("risk_category", "medium")
            except Exception:
                risk_category = "medium"
            if risk_category not in risk_breakdown:
                risk_category = "medium"
            risk_breakdown[risk_category] += 1

            try:
                snapshot = market_data.get_ticker_snapshot(market_symbol)
            except Exception:
                snapshot = {}

            history = snapshot.get("history") or []
            current_price = snapshot.get("current_price")
            previous_close = None
            if len(history) >= 2:
                previous_close = history[-2].get("close")
            elif history:
                previous_close = history[-1].get("open")

            change_pct = None
            if current_price is not None and previous_close not in (None, 0):
                try:
                    change_pct = ((float(current_price) - float(previous_close)) / float(previous_close)) * 100
                except Exception:
                    change_pct = None

            movers.append(
                {
                    "entry_id": entry.id,
                    "symbol": symbol,
                    "name": entry.stock.name,
                    "sector_name": entry.sector.name,
                    "current_price": round(float(current_price), 2) if current_price is not None else None,
                    "change_pct": round(float(change_pct), 2) if change_pct is not None else None,
                    "risk_category": risk_category,
                }
            )

        ranked_movers = [item for item in movers if item["change_pct"] is not None]
        ranked_movers.sort(key=lambda item: item["change_pct"], reverse=True)
        payload = {
            "risk_breakdown": risk_breakdown,
            "top_gainers": ranked_movers[:3],
            "top_losers": list(reversed(ranked_movers[-3:])),
        }
        cache.set(cache_key, payload, self.INSIGHTS_CACHE_TIMEOUT_SECONDS)
        return payload

    def _market_symbol(self, stock: Stock) -> str:
        symbol = stock.symbol.upper().strip()
        if stock.sector and stock.sector.market.code == "IN" and "." not in symbol:
            return f"{symbol}.NS"
        return symbol
