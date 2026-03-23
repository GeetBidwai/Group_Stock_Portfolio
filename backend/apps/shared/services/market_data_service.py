from django.conf import settings

from apps.shared.data_providers.yfinance_provider import YFinanceMarketDataProvider


class MarketDataService:
    def __init__(self):
        if settings.MARKET_DATA_PROVIDER != "yfinance":
            raise ValueError(f"Unsupported market data provider: {settings.MARKET_DATA_PROVIDER}")
        self.provider = YFinanceMarketDataProvider()

    def search_indian_stocks(self, query: str) -> list[dict]:
        return self.provider.search_indian_stocks(query)

    def get_ticker_snapshot(self, symbol: str) -> dict:
        return self.provider.get_ticker_snapshot(symbol)

    def get_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> list[dict]:
        return self.provider.get_history(symbol, period, interval)
