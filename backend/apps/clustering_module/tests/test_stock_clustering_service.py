from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.clustering_module.stock_clustering_service import StockClusteringService
from apps.portfolio_module.models import PortfolioStock, PortfolioType


class StockClusteringServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cluster-user", password="secret123")

    def test_returns_empty_when_user_has_no_portfolio_stocks(self):
        result = StockClusteringService().cluster(self.user)

        self.assertEqual(result, [])

    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._cluster_feature_frame")
    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._build_feature_frame")
    def test_uses_all_portfolio_symbols_without_market_fallback(self, mock_build_frame, mock_cluster_frame):
        portfolio_type = PortfolioType.objects.create(user=self.user, name="Core")
        PortfolioStock.objects.create(user=self.user, portfolio_type=portfolio_type, symbol="ACC")
        PortfolioStock.objects.create(user=self.user, portfolio_type=portfolio_type, symbol="BAJAJ-AUTO")

        mock_build_frame.return_value = object()
        mock_cluster_frame.return_value = [{"stock": "ACC", "x": 0.0, "y": 0.0, "cluster": 0, "sector": "Unknown"}]

        StockClusteringService().cluster(self.user)

        symbols = mock_build_frame.call_args.args[0]
        self.assertEqual(symbols, ["ACC", "BAJAJ-AUTO"])
