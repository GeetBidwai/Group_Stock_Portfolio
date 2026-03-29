from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from django.core.cache import cache
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from apps.portfolio_module.models import PortfolioStock
from apps.stocks_module.models import PortfolioEntry
from apps.shared.services.market_data_service import MarketDataService


@dataclass
class StockClusterPoint:
    stock: str
    x: float
    y: float
    cluster: int
    sector: str


class StockClusteringService:
    DEFAULT_K = 3
    DEFAULT_METHOD = "pca"
    CACHE_TIMEOUT_SECONDS = 1800

    def __init__(self):
        self.market_data = MarketDataService()

    def cluster(self, user, method: str = "pca", k: int = 3, portfolio_id: int | None = None) -> list[dict]:
        normalized_method = method.lower() if method else self.DEFAULT_METHOD
        normalized_method = normalized_method if normalized_method in {"pca", "umap"} else self.DEFAULT_METHOD
        normalized_k = max(2, min(int(k or self.DEFAULT_K), 8))
        cache_key = f"cluster-stocks:{user.id}:{portfolio_id or 'all'}:{normalized_method}:{normalized_k}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            stock_records = self._select_stock_records(user, portfolio_id)
            if len(stock_records) < 2:
                return []

            feature_frame = self._build_feature_frame(stock_records)
            if len(feature_frame) < 2:
                return []

            points = self._cluster_feature_frame(feature_frame, normalized_method, normalized_k)
        except Exception:
            points = []

        cache.set(cache_key, points, self.CACHE_TIMEOUT_SECONDS)
        return points

    def _select_stock_records(self, user, portfolio_id: int | None) -> list[dict]:
        queryset = PortfolioStock.objects.filter(user=user).select_related("portfolio_type__sector")
        if portfolio_id:
            queryset = queryset.filter(portfolio_type_id=portfolio_id)

        records: list[dict] = []
        seen_symbols: set[str] = set()

        for item in queryset:
            symbol = (item.symbol or "").upper().strip()
            if not symbol or symbol in seen_symbols:
                continue
            seen_symbols.add(symbol)
            records.append(
                {
                    "symbol": symbol,
                    "market_symbol": symbol,
                    "sector": item.portfolio_type.sector.name if item.portfolio_type and item.portfolio_type.sector else "Unknown",
                }
            )

        if portfolio_id:
            return records

        grouped_entries = (
            PortfolioEntry.objects.filter(user=user)
            .select_related("stock", "sector", "sector__market")
            .order_by("stock__symbol")
        )
        for entry in grouped_entries:
            symbol = (entry.stock.symbol or "").upper().strip()
            if not symbol or symbol in seen_symbols:
                continue
            seen_symbols.add(symbol)
            market_code = (entry.sector.market.code or "").upper() if entry.sector and entry.sector.market else ""
            market_symbol = f"{symbol}.NS" if market_code == "IN" and "." not in symbol else symbol
            records.append(
                {
                    "symbol": symbol,
                    "market_symbol": market_symbol,
                    "sector": entry.sector.name if entry.sector else "Unknown",
                }
            )

        return records

    def _build_feature_frame(self, stock_records: list[dict]) -> pd.DataFrame:
        rows = []
        for stock_record in stock_records:
            row = self._build_feature_row(stock_record)
            if row is not None:
                rows.append(row)

        frame = pd.DataFrame(rows)
        if frame.empty:
            return frame

        numeric_columns = ["daily_return", "volatility", "volume", "pe_ratio", "market_cap"]
        for column in numeric_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
            median_value = float(frame[column].median()) if frame[column].notna().any() else 0.0
            frame[column] = frame[column].fillna(median_value)

        frame = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["daily_return", "volatility", "volume"])
        return frame.reset_index(drop=True)

    def _build_feature_row(self, stock_record: dict) -> dict | None:
        symbol = str(stock_record.get("symbol") or "").upper().strip()
        market_symbol = str(stock_record.get("market_symbol") or symbol).strip()
        snapshot = self.market_data.get_ticker_snapshot(market_symbol)
        history = pd.DataFrame(snapshot.get("history") or self.market_data.get_history(market_symbol, period="1y", interval="1d"))
        if history.empty:
            return None

        history["close"] = pd.to_numeric(history.get("close"), errors="coerce")
        history["volume"] = pd.to_numeric(history.get("volume"), errors="coerce")
        history = history.dropna(subset=["close", "volume"]).sort_values("date").reset_index(drop=True)
        if len(history) < 30:
            return None

        returns = history["close"].pct_change().replace([np.inf, -np.inf], np.nan).dropna()
        rolling_volatility = returns.rolling(window=20).std().dropna()
        if returns.empty:
            return None

        return {
            "stock": symbol,
            "sector": snapshot.get("sector") or stock_record.get("sector") or "Unknown",
            "daily_return": float(returns.tail(60).mean()),
            "volatility": float(rolling_volatility.tail(60).mean()) if not rolling_volatility.empty else float(returns.std()),
            "volume": float(history["volume"].tail(60).mean()),
            "pe_ratio": snapshot.get("trailing_pe"),
            "market_cap": snapshot.get("market_cap"),
        }

    def _cluster_feature_frame(self, frame: pd.DataFrame, method: str, k: int) -> list[dict]:
        feature_columns = ["daily_return", "volatility", "volume", "pe_ratio", "market_cap"]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(frame[feature_columns])

        effective_k = min(k, len(frame))
        if effective_k < 2:
            return []

        model = KMeans(n_clusters=effective_k, random_state=42, n_init="auto")
        assignments = model.fit_predict(scaled_features)

        reduced = self._reduce_dimensions(scaled_features, method)
        if reduced is None:
            reduced = self._reduce_dimensions(scaled_features, "pca")

        if len(frame) > effective_k:
            try:
                silhouette_score(scaled_features, assignments)
            except Exception:
                pass

        points = [
            StockClusterPoint(
                stock=str(row["stock"]),
                x=round(float(reduced[index][0]), 4),
                y=round(float(reduced[index][1]), 4),
                cluster=int(assignments[index]),
                sector=str(row["sector"]),
            )
            for index, (_, row) in enumerate(frame.iterrows())
        ]
        return [point.__dict__ for point in points]

    def _reduce_dimensions(self, scaled_features: np.ndarray, method: str) -> np.ndarray | None:
        if method == "umap":
            try:
                import umap

                reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=min(10, max(2, len(scaled_features) - 1)))
                return reducer.fit_transform(scaled_features)
            except Exception:
                return None

        reducer = PCA(n_components=2, random_state=42)
        return reducer.fit_transform(scaled_features)
