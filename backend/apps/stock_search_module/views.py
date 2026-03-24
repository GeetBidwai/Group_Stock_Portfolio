from django.core.cache import cache
from rest_framework import generics, permissions, response, throttling, views

from apps.stock_search_module.pagination import StockSearchPagination
from apps.stock_search_module.models import StockReference
from apps.stock_search_module.serializers import StockReferenceSerializer, StockSearchQuerySerializer
from apps.stock_search_module.services import StockSearchService
from apps.shared.services.market_data_service import MarketDataService


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
        cache_key = "stocks:risk:list"
        cached = cache.get(cache_key)
        if cached is not None:
            return response.Response(cached)

        market_data = MarketDataService()
        stocks = StockReference.objects.filter(is_active=True).only("symbol", "name", "risk_category")
        payload = []
        for stock in stocks:
            snapshot = market_data.provider.get_cached_ticker_snapshot(stock.symbol) or {}
            price = snapshot.get("current_price")
            if price is None:
                history = snapshot.get("history") or []
                if history:
                    price = history[-1].get("close")

            payload.append(
                {
                    "stock_name": stock.name,
                    "symbol": stock.symbol,
                    "price": round(float(price), 2) if price is not None else None,
                    "risk": stock.risk_category or "Unknown",
                }
            )

        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return response.Response(payload)
