from django.core.cache import cache
from rest_framework import generics, permissions, response, throttling, views

from apps.portfolio_module.models import PortfolioStock
from apps.risk_module.services import RiskCategorizationService
from apps.stock_search_module.pagination import StockSearchPagination
from apps.stock_search_module.models import StockReference
from apps.stock_search_module.serializers import StockReferenceSerializer, StockSearchQuerySerializer
from apps.stock_search_module.services import StockSearchService
from apps.shared.services.market_data_service import MarketDataService
from apps.stocks_module.models import PortfolioEntry
from apps.stocks_module.services import StocksPortfolioService


class StockSearchThrottle(throttling.UserRateThrottle):
    rate = "30/min"


class StockSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StockReferenceSerializer
    pagination_class = StockSearchPagination
    throttle_classes = [StockSearchThrottle]

    def get_queryset(self):
        query_serializer = StockSearchQuerySerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)
        query = query_serializer.validated_data["q"]
        return StockSearchService().get_queryset(query)


class StockRiskListView(views.APIView):
    CACHE_TIMEOUT_SECONDS = 300

    def get(self, request):
        scope = str(request.query_params.get("scope") or "tracked").strip().lower()
        if scope not in {"tracked", "portfolio"}:
            scope = "tracked"

        cache_key = f"stocks:risk:list:v2:{scope}:{request.user.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return response.Response(cached)

        market_data = MarketDataService()
        if scope == "portfolio":
            portfolio_service = StocksPortfolioService()
            stocks = portfolio_service.portfolio_risk_items(request.user)
        else:
            stocks = [
                {
                    "symbol": stock.symbol,
                    "stock_name": stock.name,
                    "risk": stock.risk_category or "Unknown",
                }
                for stock in StockReference.objects.filter(is_active=True).only("symbol", "name", "risk_category")
            ]

        payload = []
        for stock in stocks:
            snapshot = market_data.provider.get_cached_ticker_snapshot(stock["symbol"]) or {}
            price = snapshot.get("current_price")
            if price is None:
                history = snapshot.get("history") or []
                if history:
                    price = history[-1].get("close")

            payload.append(
                {
                    "stock_name": stock["stock_name"],
                    "symbol": stock["symbol"],
                    "price": round(float(price), 2) if price is not None else None,
                    "risk": stock["risk"],
                }
            )

        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return response.Response(payload)

    def _resolve_risk_label(self, symbol: str, stored_risk: str | None, risk_service: RiskCategorizationService) -> str:
        normalized_stored = (stored_risk or "").strip()
        if normalized_stored:
            return normalized_stored.title()

        try:
            live_risk = (risk_service.classify(symbol).get("risk_category") or "").strip()
        except Exception:
            live_risk = ""

        return live_risk.title() if live_risk else "Unknown"

    def _portfolio_stocks_payload(self, user) -> list[dict]:
        return StocksPortfolioService().portfolio_risk_items(user)
