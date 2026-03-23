from abc import ABC, abstractmethod


class MarketDataProvider(ABC):
    @abstractmethod
    def search_indian_stocks(self, query: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_ticker_snapshot(self, symbol: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> list[dict]:
        raise NotImplementedError
