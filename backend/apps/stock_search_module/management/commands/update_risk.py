from django.core.management.base import BaseCommand

from apps.shared.services.market_data_service import MarketDataService
from apps.shared.services.risk_service import RiskService
from apps.stock_search_module.models import StockReference


class Command(BaseCommand):
    help = "Precompute stock risk categories using historical volatility."

    def handle(self, *args, **options):
        market_data = MarketDataService()
        risk_service = RiskService()

        stocks = list(StockReference.objects.filter(is_active=True).only("id", "symbol", "risk_category"))
        updated = []

        for stock in stocks:
            history = market_data.get_history(stock.symbol, period="1y", interval="1d")
            prices = [point["close"] for point in history if point.get("close") is not None]
            volatility = risk_service.calculate_volatility(prices)
            stock.risk_category = risk_service.categorize_risk(volatility)
            updated.append(stock)

            # Warm the local snapshot cache so the read-only API can serve a price without fresh network work.
            try:
                market_data.get_ticker_snapshot(stock.symbol)
            except Exception:
                pass

        if updated:
            StockReference.objects.bulk_update(updated, ["risk_category"])
        self.stdout.write(self.style.SUCCESS(f"Updated risk category for {len(updated)} stocks."))
