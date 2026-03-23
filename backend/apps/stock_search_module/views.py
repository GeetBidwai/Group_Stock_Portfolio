from rest_framework import generics, permissions, throttling

from apps.stock_search_module.pagination import StockSearchPagination
from apps.stock_search_module.serializers import StockReferenceSerializer, StockSearchQuerySerializer
from apps.stock_search_module.services import StockSearchService


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
