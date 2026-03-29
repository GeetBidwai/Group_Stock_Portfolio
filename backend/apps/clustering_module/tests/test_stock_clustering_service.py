from unittest.mock import patch

import numpy as np
import pandas as pd
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.clustering_module.stock_clustering_service import StockClusteringService
from apps.portfolio_module.models import PortfolioStock, PortfolioType
from apps.stocks_module.models import Market, PortfolioEntry, Sector, Stock


class StockClusteringServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cluster-user", password="secret123")

    def test_returns_empty_when_user_has_no_portfolio_stocks(self):
        result = StockClusteringService().cluster(self.user)

        self.assertEqual(result, [])

    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._cluster_feature_frame")
    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._build_feature_frame")
    def test_uses_all_manual_portfolio_symbols_without_market_fallback(self, mock_build_frame, mock_cluster_frame):
        portfolio_type = PortfolioType.objects.create(user=self.user, name="Core")
        PortfolioStock.objects.create(user=self.user, portfolio_type=portfolio_type, symbol="ACC")
        PortfolioStock.objects.create(user=self.user, portfolio_type=portfolio_type, symbol="BAJAJ-AUTO")

        mock_build_frame.return_value = object()
        mock_cluster_frame.return_value = [{"stock": "ACC", "x": 0.0, "y": 0.0, "cluster": 0, "sector": "Unknown"}]

        StockClusteringService().cluster(self.user)

        stock_records = mock_build_frame.call_args.args[0]
        self.assertEqual(
            stock_records,
            [
                {"symbol": "ACC", "market_symbol": "ACC", "sector": "Unknown"},
                {"symbol": "BAJAJ-AUTO", "market_symbol": "BAJAJ-AUTO", "sector": "Unknown"},
            ],
        )

    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._cluster_feature_frame")
    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._build_feature_frame")
    def test_includes_grouped_portfolio_entries_when_no_portfolio_filter(self, mock_build_frame, mock_cluster_frame):
        portfolio_type = PortfolioType.objects.create(user=self.user, name="Core")
        PortfolioStock.objects.create(user=self.user, portfolio_type=portfolio_type, symbol="ACC")

        market, _ = Market.objects.get_or_create(code="IN", defaults={"name": "India"})
        sector = Sector.objects.create(market=market, code="BANK", name="Nifty Bank")
        stock = Stock.objects.create(sector=sector, symbol="SBIN", name="State Bank of India", exchange="NSE")
        PortfolioEntry.objects.create(user=self.user, stock=stock, sector=sector)

        mock_build_frame.return_value = object()
        mock_cluster_frame.return_value = [{"stock": "ACC", "x": 0.0, "y": 0.0, "cluster": 0, "sector": "Unknown"}]

        StockClusteringService().cluster(self.user)

        stock_records = mock_build_frame.call_args.args[0]
        self.assertEqual(
            stock_records,
            [
                {"symbol": "ACC", "market_symbol": "ACC", "sector": "Unknown"},
                {"symbol": "SBIN", "market_symbol": "SBIN.NS", "sector": "Nifty Bank"},
            ],
        )

    @patch("apps.clustering_module.stock_clustering_service.KMeans")
    @patch("apps.clustering_module.stock_clustering_service.StockClusteringService._reduce_dimensions")
    def test_clusters_on_scaled_features_before_projection(self, mock_reduce_dimensions, mock_kmeans):
        service = StockClusteringService()
        frame = pd.DataFrame(
            [
                {"stock": "ACC", "sector": "A", "daily_return": 0.1, "volatility": 0.2, "volume": 1000, "pe_ratio": 10, "market_cap": 10000},
                {"stock": "SBIN", "sector": "B", "daily_return": 0.2, "volatility": 0.3, "volume": 1200, "pe_ratio": 12, "market_cap": 12000},
                {"stock": "TCS", "sector": "C", "daily_return": 0.15, "volatility": 0.25, "volume": 1100, "pe_ratio": 20, "market_cap": 20000},
            ]
        )
        reduced = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        mock_reduce_dimensions.side_effect = [reduced]
        model = mock_kmeans.return_value
        model.fit_predict.return_value = [0, 1, 1]

        result = service._cluster_feature_frame(frame, method="pca", k=2)

        fit_arg = model.fit_predict.call_args.args[0]
        self.assertEqual(fit_arg.shape, (3, 5))
        self.assertEqual(len(result), 3)
