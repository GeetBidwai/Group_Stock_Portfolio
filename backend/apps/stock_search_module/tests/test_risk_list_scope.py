from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.portfolio_module.models import PortfolioStock, PortfolioType
from apps.stock_search_module.models import StockReference


class StockRiskListScopeTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="risk-user", password="secret123")
        self.client.force_authenticate(user=self.user)

        portfolio_type = PortfolioType.objects.create(user=self.user, name="Core")
        PortfolioStock.objects.create(
            user=self.user,
            portfolio_type=portfolio_type,
            symbol="TCS",
            company_name="Tata Consultancy Services",
        )

        StockReference.objects.create(symbol="TCS", name="Tata Consultancy Services", risk_category="Medium", is_active=True)
        StockReference.objects.create(symbol="INFY", name="Infosys", risk_category="Low", is_active=True)

    def test_portfolio_scope_returns_only_portfolio_symbols(self):
        response = self.client.get("/api/stocks/risk/?scope=portfolio")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["symbol"], "TCS")

    def test_tracked_scope_returns_full_reference_list(self):
        response = self.client.get("/api/stocks/risk/?scope=tracked")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual({item["symbol"] for item in payload}, {"TCS", "INFY"})

    @patch("apps.stocks_module.services.RiskCategorizationService.classify", return_value={"risk_category": "low"})
    def test_portfolio_scope_falls_back_to_live_risk_when_reference_missing(self, _mock_classify):
        StockReference.objects.filter(symbol="TCS").delete()

        response = self.client.get("/api/stocks/risk/?scope=portfolio")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload[0]["risk"], "Low")
