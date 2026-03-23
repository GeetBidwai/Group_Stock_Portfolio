import numpy as np

from apps.portfolio_module.models import PortfolioStock
from apps.shared.services.market_data_service import MarketDataService


class PortfolioClusteringService:
    def cluster(self, user) -> dict:
        stocks = list(PortfolioStock.objects.filter(user=user))
        market_data = MarketDataService()
        feature_rows = []
        labels = []
        for stock in stocks:
            history = market_data.get_history(stock.symbol, period="6mo", interval="1d")
            closes = np.array([point["close"] for point in history if point.get("close") is not None])
            if closes.size < 3:
                continue
            returns = np.diff(closes) / closes[:-1]
            feature_rows.append([float(np.mean(returns)), float(np.std(returns)), float(closes[-1])])
            labels.append(stock.symbol)
        if len(feature_rows) < 2:
            return {"clusters": [], "interpretation": "Add at least two stocks with sufficient price history to cluster the portfolio."}
        n_clusters = min(3, len(feature_rows))
        from sklearn.cluster import KMeans

        model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        assignments = model.fit_predict(feature_rows)
        clusters = [{"symbol": symbol, "cluster": int(cluster)} for symbol, cluster in zip(labels, assignments)]
        return {"clusters": clusters, "interpretation": "Clusters group holdings with similar return, volatility, and price patterns."}
