import numpy as np
from django.core.cache import cache

from apps.portfolio_module.models import PortfolioStock
from apps.shared.services.market_data_service import MarketDataService
from apps.shared.services.valuation_service import ValuationService


class StockAnalyticsService:
    CACHE_TIMEOUT_SECONDS = 900

    def __init__(self):
        self.market_data = MarketDataService()
        self.valuation = ValuationService()

    def get_stock_analytics(self, symbol: str) -> dict:
        cache_key = f"stock-analytics:{symbol.upper()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        snapshot = self.market_data.get_ticker_snapshot(symbol)
        intrinsic_value = self.valuation.compute_intrinsic_value(snapshot.get("eps"), snapshot.get("trailing_pe"))
        discount = self.valuation.compute_discount_percentage(snapshot.get("current_price"), intrinsic_value)
        history = snapshot.get("history", [])
        latest_point = history[-1] if history else {}
        payload = {
            **snapshot,
            "intrinsic_value": intrinsic_value,
            "discount_percentage": discount,
            "opportunity_signal": self.valuation.opportunity_signal(discount),
            "latest_open": latest_point.get("open"),
            "latest_close": latest_point.get("close"),
            "price_series": [{"date": point["date"], "open": point["open"], "close": point["close"]} for point in history],
        }
        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload


class PortfolioPEComparisonService:
    def compare_for_user(self, user) -> dict:
        service = StockAnalyticsService()
        stocks = PortfolioStock.objects.filter(user=user)
        series = []
        for stock in stocks:
            analytics = service.get_stock_analytics(stock.symbol)
            series.append({"symbol": stock.symbol, "portfolio": stock.portfolio_type.name, "pe_ratio": analytics.get("trailing_pe")})
        valid = [item["pe_ratio"] for item in series if item["pe_ratio"] is not None]
        average = round(float(np.mean(valid)), 2) if valid else None
        return {"items": series, "portfolio_average_pe": average}


class PortfolioStockAnalyticsService:
    CACHE_TIMEOUT_SECONDS = 300

    def summarize_portfolio(self, user, portfolio_type_id: int) -> dict:
        cache_key = f"portfolio-stock-analytics:{user.id}:{portfolio_type_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        service = StockAnalyticsService()
        stocks = list(
            PortfolioStock.objects.filter(user=user, portfolio_type_id=portfolio_type_id)
            .select_related("portfolio_type")
            .order_by("symbol")
        )

        items = []
        for stock in stocks:
            analytics = service.get_stock_analytics(stock.symbol)
            items.append(
                {
                    "id": stock.id,
                    "portfolio_type": stock.portfolio_type_id,
                    "symbol": stock.symbol,
                    "company_name": stock.company_name or analytics.get("name") or stock.symbol,
                    "quantity": stock.quantity,
                    "average_buy_price": stock.average_buy_price,
                    "current_price": analytics.get("current_price"),
                    "trailing_pe": analytics.get("trailing_pe"),
                }
            )

        pe_items = [
            {"symbol": item["symbol"], "pe_ratio": item["trailing_pe"]}
            for item in items
            if item.get("trailing_pe") is not None
        ]
        valid_pe_values = [item["pe_ratio"] for item in pe_items if item["pe_ratio"] is not None]
        payload = {
            "items": items,
            "pe_items": pe_items,
            "portfolio_average_pe": round(float(np.mean(valid_pe_values)), 2) if valid_pe_values else None,
        }
        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload
