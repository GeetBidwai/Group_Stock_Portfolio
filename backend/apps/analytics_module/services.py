import numpy as np

from apps.portfolio_module.models import PortfolioStock
from apps.shared.services.market_data_service import MarketDataService
from apps.shared.services.valuation_service import ValuationService


class StockAnalyticsService:
    def __init__(self):
        self.market_data = MarketDataService()
        self.valuation = ValuationService()

    def get_stock_analytics(self, symbol: str) -> dict:
        snapshot = self.market_data.get_ticker_snapshot(symbol)
        intrinsic_value = self.valuation.compute_intrinsic_value(snapshot.get("eps"), snapshot.get("trailing_pe"))
        discount = self.valuation.compute_discount_percentage(snapshot.get("current_price"), intrinsic_value)
        history = snapshot.get("history", [])
        latest_point = history[-1] if history else {}
        return {
            **snapshot,
            "intrinsic_value": intrinsic_value,
            "discount_percentage": discount,
            "opportunity_signal": self.valuation.opportunity_signal(discount),
            "latest_open": latest_point.get("open"),
            "latest_close": latest_point.get("close"),
            "price_series": [{"date": point["date"], "open": point["open"], "close": point["close"]} for point in history],
        }


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
