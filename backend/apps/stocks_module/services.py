from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from django.core.cache import cache
from django.db.models import Count, Max
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.risk_module.services import RiskCategorizationService
from apps.shared.services.market_data_service import MarketDataService
from apps.stock_search_module.models import StockReference
from apps.stocks_module.models import PortfolioEntry, Sector, Stock
from apps.portfolio_module.models import PortfolioStock


class StocksPricingService:
    CACHE_TIMEOUT_SECONDS = 900
    SECTOR_CACHE_TIMEOUT_SECONDS = 300
    MAX_WORKERS = 4

    def get_stocks_with_prices(self, sector: Sector) -> list[dict]:
        sector_cache_key = f"stocks-module:sector:{sector.id}:prices"
        sector_cached = cache.get(sector_cache_key)
        if sector_cached is not None:
            return sector_cached

        stocks = list(sector.stocks.filter(is_active=True).order_by("symbol"))
        if not stocks:
            cache.set(sector_cache_key, [], self.SECTOR_CACHE_TIMEOUT_SECONDS)
            return []

        if len(stocks) == 1:
            items = [self._snapshot_for_stock(stocks[0], sector.market.code)]
        else:
            worker_count = min(self.MAX_WORKERS, len(stocks))
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                items = list(executor.map(lambda item: self._snapshot_for_stock(item, sector.market.code), stocks))

        cache.set(sector_cache_key, items, self.SECTOR_CACHE_TIMEOUT_SECONDS)
        return items

    def _snapshot_for_stock(self, stock: Stock, market_code: str) -> dict:
        cache_key = f"stocks-module:price:{market_code}:{stock.symbol}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        market_data = MarketDataService()
        try:
            snapshot = market_data.get_ticker_snapshot(self._ticker_symbol(stock.symbol, market_code))
        except Exception:
            snapshot = {}

        current_price = snapshot.get("current_price")
        currency = snapshot.get("currency")
        history = snapshot.get("history") or []
        if current_price is None and history:
            current_price = history[-1].get("close")

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

    def _holdings_signature(self, user) -> str:
        manual_queryset = PortfolioStock.objects.filter(user=user)
        grouped_queryset = PortfolioEntry.objects.filter(user=user)

        manual_meta = manual_queryset.aggregate(count=Count("id"), latest=Max("created_at"))
        grouped_meta = grouped_queryset.aggregate(count=Count("id"), latest=Max("added_at"))

        def iso(value):
            if isinstance(value, datetime):
                return value.isoformat()
            return "none"

        return ":".join(
            [
                str(manual_meta.get("count") or 0),
                iso(manual_meta.get("latest")),
                str(grouped_meta.get("count") or 0),
                iso(grouped_meta.get("latest")),
            ]
        )

    def _insights_cache_key(self, user) -> str:
        return f"stocks-module:portfolio-insights:v3:{user.id}:{self._holdings_signature(user)}"

    def _portfolio_risk_cache_key(self, user) -> str:
        return f"stocks-module:portfolio-risk:v1:{user.id}:{self._holdings_signature(user)}"

    def _clear_user_caches(self, user_id: int):
        # Signature-based cache keys refresh automatically when holdings change.
        return None

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

    def portfolio_risk_items(self, user) -> list[dict]:
        cache_key = self._portfolio_risk_cache_key(user)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        holdings = self._portfolio_holdings(user)
        if not holdings:
            cache.set(cache_key, [], self.INSIGHTS_CACHE_TIMEOUT_SECONDS)
            return []

        symbols = [item["symbol"] for item in holdings]
        reference_map = {
            row.symbol.upper(): row
            for row in StockReference.objects.filter(symbol__in=symbols, is_active=True).only("symbol", "name", "risk_category", "exchange")
        }
        risk_service = RiskCategorizationService()
        items = []

        for holding in holdings:
            reference = reference_map.get(holding["symbol"])
            stored_risk = (getattr(reference, "risk_category", "") or "").strip().lower()
            risk = stored_risk if stored_risk in {"low", "medium", "high"} else None

            market_symbol = holding["market_symbol"] or self._market_symbol_from_reference(holding["symbol"], reference)
            if risk is None and market_symbol:
                try:
                    risk_payload = risk_service.classify(market_symbol)
                    live_risk = (risk_payload.get("risk_category") or "").strip().lower()
                    risk = live_risk if live_risk in {"low", "medium", "high"} else None
                except Exception:
                    risk = None

            items.append(
                {
                    "symbol": holding["symbol"],
                    "stock_name": holding["stock_name"] or getattr(reference, "name", None) or holding["symbol"],
                    "market_symbol": market_symbol or holding["symbol"],
                    "risk": risk.title() if risk else "Unknown",
                }
            )

        cache.set(cache_key, items, self.INSIGHTS_CACHE_TIMEOUT_SECONDS)
        return items

    def _portfolio_holdings(self, user) -> list[dict]:
        manual = list(
            PortfolioStock.objects.filter(user=user)
            .select_related("portfolio_type")
            .order_by("symbol")
        )
        grouped = list(
            PortfolioEntry.objects.filter(user=user)
            .select_related("stock", "sector", "sector__market")
            .order_by("stock__symbol")
        )

        holdings: dict[str, dict] = {}

        for item in manual:
            symbol = item.symbol.upper()
            holdings[symbol] = {
                "symbol": symbol,
                "stock_name": item.company_name or symbol,
                "market_symbol": self._default_market_symbol(symbol),
            }

        for item in grouped:
            symbol = item.stock.symbol.upper()
            market_symbol = self._market_symbol(item.stock)
            if symbol in holdings:
                if not holdings[symbol].get("market_symbol"):
                    holdings[symbol]["market_symbol"] = market_symbol
                if not holdings[symbol].get("stock_name"):
                    holdings[symbol]["stock_name"] = item.stock.name or symbol
                continue
            holdings[symbol] = {
                "symbol": symbol,
                "stock_name": item.stock.name or symbol,
                "market_symbol": market_symbol,
            }

        return list(holdings.values())

    def _default_market_symbol(self, symbol: str) -> str:
        normalized = symbol.upper().strip()
        if "." in normalized or "=" in normalized or "^" in normalized:
            return normalized
        return f"{normalized}.NS"

    def _market_symbol_from_reference(self, symbol: str, reference: StockReference | None) -> str:
        if reference and (reference.exchange or "").strip().upper() == "NSE":
            return self._default_market_symbol(symbol)
        return symbol.upper().strip()

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
        cache_key = self._insights_cache_key(user)
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
        risk_breakdown = {"low": 0, "medium": 0, "high": 0}
        movers = []
        risk_items = {
            item["symbol"]: item
            for item in self.portfolio_risk_items(user)
        }

        for item in risk_items.values():
            normalized_risk = (item.get("risk") or "").strip().lower()
            if normalized_risk in risk_breakdown:
                risk_breakdown[normalized_risk] += 1

        for entry in entries:
            symbol = entry.stock.symbol
            market_symbol = self._market_symbol(entry.stock)
            risk_category = (risk_items.get(symbol, {}).get("risk") or "").strip().lower()
            if risk_category not in {"low", "medium", "high"}:
                risk_category = "unknown"

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
        ranked_gainers = [item for item in sorted(ranked_movers, key=lambda item: item["change_pct"], reverse=True) if item["change_pct"] > 0]
        ranked_losers = [item for item in sorted(ranked_movers, key=lambda item: item["change_pct"]) if item["change_pct"] < 0]
        top_gainers = ranked_gainers[:1]
        primary_gainer_id = top_gainers[0]["entry_id"] if top_gainers else None
        top_losers = [item for item in ranked_losers if item["entry_id"] != primary_gainer_id][:1]
        payload = {
            "risk_breakdown": risk_breakdown,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
        }
        cache.set(cache_key, payload, self.INSIGHTS_CACHE_TIMEOUT_SECONDS)
        return payload

    def _market_symbol(self, stock: Stock) -> str:
        symbol = stock.symbol.upper().strip()
        if stock.sector and stock.sector.market.code == "IN" and "." not in symbol:
            return f"{symbol}.NS"
        return symbol
