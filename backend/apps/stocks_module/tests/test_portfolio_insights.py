from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.stocks_module.models import Market, PortfolioEntry, Sector, Stock
from apps.stocks_module.services import StocksPortfolioService
from apps.stock_search_module.models import StockReference


class StocksPortfolioServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="portfolio-user", password="secret123")
        self.market, _ = Market.objects.get_or_create(code="IN", defaults={"name": "India"})
        self.sector = Sector.objects.create(market=self.market, code="AUTO-TEST", name="Auto Test")

    def _create_stock(self, symbol: str, name: str) -> Stock:
        return Stock.objects.create(sector=self.sector, symbol=symbol, name=name, exchange="NSE", is_active=True)

    @patch("apps.stocks_module.services.MarketDataService.get_ticker_snapshot")
    @patch("apps.stocks_module.services.RiskCategorizationService.classify")
    def test_portfolio_insights_returns_distinct_gainer_and_loser(self, mock_classify, mock_snapshot):
        stock_one = self._create_stock("ACC", "ACC Ltd.")
        stock_two = self._create_stock("MOTHERSON", "Samvardhana Motherson")
        PortfolioEntry.objects.create(user=self.user, stock=stock_one, sector=self.sector)
        PortfolioEntry.objects.create(user=self.user, stock=stock_two, sector=self.sector)

        mock_classify.return_value = {"risk_category": "medium"}
        mock_snapshot.side_effect = [
            {"current_price": 110, "history": [{"open": 100, "close": 100}, {"open": 100, "close": 100}]},
            {"current_price": 90, "history": [{"open": 100, "close": 100}, {"open": 100, "close": 100}]},
        ]

        payload = StocksPortfolioService().portfolio_insights(self.user)

        self.assertEqual(payload["risk_breakdown"], {"low": 0, "medium": 2, "high": 0})
        self.assertEqual(payload["top_gainers"][0]["symbol"], "ACC")
        self.assertEqual(payload["top_losers"][0]["symbol"], "MOTHERSON")

    @patch("apps.stocks_module.services.MarketDataService.get_ticker_snapshot")
    @patch("apps.stocks_module.services.RiskCategorizationService.classify", side_effect=Exception("risk unavailable"))
    def test_portfolio_insights_falls_back_to_reference_risk_when_live_risk_fails(self, _mock_classify, mock_snapshot):
        stock_one = self._create_stock("ACC", "ACC Ltd.")
        stock_two = self._create_stock("INFY", "Infosys")
        stock_three = self._create_stock("ITC", "ITC")
        PortfolioEntry.objects.create(user=self.user, stock=stock_one, sector=self.sector)
        PortfolioEntry.objects.create(user=self.user, stock=stock_two, sector=self.sector)
        PortfolioEntry.objects.create(user=self.user, stock=stock_three, sector=self.sector)

        StockReference.objects.create(symbol="ACC", name="ACC Ltd.", risk_category="Low", is_active=True)
        StockReference.objects.create(symbol="INFY", name="Infosys", risk_category="High", is_active=True)
        StockReference.objects.create(symbol="ITC", name="ITC", risk_category="Medium", is_active=True)

        mock_snapshot.side_effect = [
            {"current_price": 110, "history": [{"open": 100, "close": 100}, {"open": 100, "close": 100}]},
            {"current_price": 90, "history": [{"open": 100, "close": 100}, {"open": 100, "close": 100}]},
            {"current_price": 100, "history": [{"open": 100, "close": 100}, {"open": 100, "close": 100}]},
        ]

        payload = StocksPortfolioService().portfolio_insights(self.user)

        self.assertEqual(payload["risk_breakdown"], {"low": 1, "medium": 1, "high": 1})
        self.assertEqual([item["symbol"] for item in payload["top_gainers"]], ["ACC"])
        self.assertEqual([item["symbol"] for item in payload["top_losers"]], ["INFY"])

    @patch("apps.stocks_module.services.MarketDataService.get_ticker_snapshot", return_value={"current_price": 100, "history": [{"open": 100, "close": 100}, {"open": 100, "close": 100}]})
    @patch("apps.stocks_module.services.RiskCategorizationService.classify", return_value={"risk_category": "medium"})
    def test_add_to_portfolio_invalidates_cached_insights(self, _mock_classify, _mock_snapshot):
        stock_one = self._create_stock("ACC", "ACC Ltd.")
        stock_two = self._create_stock("INFY", "Infosys")
        service = StocksPortfolioService()

        service.add_to_portfolio(self.user, stock_one.id)
        first_payload = service.portfolio_insights(self.user)
        self.assertEqual(first_payload["risk_breakdown"]["medium"], 1)

        service.add_to_portfolio(self.user, stock_two.id)
        second_payload = service.portfolio_insights(self.user)
        self.assertEqual(second_payload["risk_breakdown"]["medium"], 2)
