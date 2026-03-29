from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.portfolio_module.models import PortfolioStock, PortfolioType
from apps.quality_stocks_module.models import QualityStock


class QualityStocksApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="quality-user", password="secret123")
        self.client.force_authenticate(user=self.user)
        self.portfolio = PortfolioType.objects.create(user=self.user, name="Core")
        self.stock = PortfolioStock.objects.create(
            user=self.user,
            portfolio_type=self.portfolio,
            symbol="TCS",
            company_name="Tata Consultancy Services",
        )

    @patch("apps.quality_stocks_module.views.QualityStocksService.snapshot")
    def test_snapshot_returns_payload(self, mock_snapshot):
        mock_snapshot.return_value = [
            {"id": self.stock.id, "stock_name": "Tata Consultancy Services", "symbol": "TCS", "score": 8.1, "signal": "BUY", "reason": "Projected upside"}
        ]

        response = self.client.post("/api/quality-stocks/snapshot/", {"portfolio_id": self.portfolio.id}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["symbol"], "TCS")

    @patch("apps.quality_stocks_module.views.QualityStocksService.sector_snapshot")
    def test_sector_snapshot_returns_payload(self, mock_sector_snapshot):
        mock_sector_snapshot.return_value = [
            {"stock_id": 101, "company": "Tata Consultancy Services", "symbol": "TCS", "quality_score": 8.1, "signal": "BUY"}
        ]

        response = self.client.post("/api/quality-stocks/sector-snapshot/", {"sector_name": "Nifty Auto"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["symbol"], "TCS")

    @patch("apps.quality_stocks_module.views.QualityStocksService.generate_sector_reports")
    def test_sector_generate_returns_saved_reports(self, mock_generate_sector_reports):
        report = QualityStock.objects.create(
            user=self.user,
            portfolio=self.portfolio,
            stock=self.stock,
            ai_rating=7.8,
            buy_signal="BUY",
            report_json={"summary": "Good"},
            graphs_data={},
        )
        mock_generate_sector_reports.return_value = [report]

        response = self.client.post(
            "/api/quality-stocks/sector-generate/",
            {"sector_name": "Nifty Auto", "stock_ids": [77]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["stock_symbol"], "TCS")

    def test_list_filters_to_user_portfolio(self):
        QualityStock.objects.create(
            user=self.user,
            portfolio=self.portfolio,
            stock=self.stock,
            ai_rating=7.8,
            buy_signal="BUY",
            report_json={"summary": "Good"},
            graphs_data={},
        )

        response = self.client.get(f"/api/quality-stocks/?portfolio_id={self.portfolio.id}")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["stock_symbol"], "TCS")

    def test_detail_and_delete_use_request_user(self):
        report = QualityStock.objects.create(
            user=self.user,
            portfolio=self.portfolio,
            stock=self.stock,
            ai_rating=7.8,
            buy_signal="BUY",
            report_json={"summary": "Good"},
            graphs_data={},
        )

        detail_response = self.client.get(f"/api/quality-stocks/{report.id}/")
        self.assertEqual(detail_response.status_code, 200)

        delete_response = self.client.delete(f"/api/quality-stocks/{report.id}/")
        self.assertEqual(delete_response.status_code, 204)
