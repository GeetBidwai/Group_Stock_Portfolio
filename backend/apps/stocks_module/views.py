from django.db.models import Case, IntegerField, Value, When
from rest_framework import generics, permissions, response, views

from apps.portfolio_module.models import Sector as PortfolioSector
from apps.portfolio_module.serializers import SectorSerializer as PortfolioSectorSerializer
from apps.stocks_module.models import Market, Sector, Stock
from apps.stocks_module.sector_mapping import INDIA_NIFTY_SECTORS
from apps.stocks_module.serializers import (
    AddToPortfolioSerializer,
    MarketSerializer,
    SectorSerializer,
    StockSerializer,
    UnifiedSectorSerializer,
)
from apps.stocks_module.services import StocksPortfolioService, StocksPricingService


class MarketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MarketSerializer

    def get_queryset(self):
        return Market.objects.annotate(
            sort_order=Case(
                When(code="IN", then=Value(0)),
                When(code="US", then=Value(1)),
                default=Value(99),
                output_field=IntegerField(),
            )
        ).order_by("sort_order", "name")


class MarketSectorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SectorSerializer

    def get_queryset(self):
        queryset = Sector.objects.select_related("market").filter(
            market__code__iexact=self.kwargs["code"]
        )
        if self.kwargs["code"].upper() == "IN":
            return _ordered_india_sectors(queryset)
        return queryset.order_by("name")


class SectorStockListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id: int):
        sector = Sector.objects.select_related("market").filter(id=id).first()
        if not sector:
            return response.Response({"error": "Sector not found."}, status=404)
        items = StocksPricingService().get_stocks_with_prices(sector)
        return response.Response(
            {
                "sector": {"id": sector.id, "name": sector.name, "market_code": sector.market.code},
                "items": items,
            }
        )


class AddStockToPortfolioView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToPortfolioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = StocksPortfolioService().add_to_portfolio(request.user, serializer.validated_data["stock_id"])
        return response.Response(payload, status=201)


class RemoveStockFromPortfolioView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, entry_id: int):
        payload = StocksPortfolioService().remove_from_portfolio(request.user, entry_id)
        return response.Response(payload, status=200)


class SectorCatalogListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnifiedSectorSerializer

    def get_queryset(self):
        market_name = (self.request.query_params.get("market") or "").strip()
        if market_name:
            normalized = market_name.lower()
            market_codes = []
            if normalized in {"india", "in"}:
                market_codes.append("IN")
            if normalized in {"usa", "us", "united states"}:
                market_codes.append("US")
            queryset = Sector.objects.select_related("market").filter(market__code__in=market_codes)
            if market_codes == ["IN"]:
                return _ordered_india_sectors(queryset)
            return queryset.order_by("name")
        return PortfolioSector.objects.all().order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = PortfolioSectorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return response.Response(PortfolioSectorSerializer(instance).data, status=201)


class StockCatalogListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StockSerializer

    def get_queryset(self):
        sector_id = self.request.query_params.get("sector_id")
        queryset = Stock.objects.select_related("sector", "sector__market").filter(is_active=True)
        if sector_id:
            queryset = queryset.filter(sector_id=sector_id)
        return queryset.order_by("symbol")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        sector_id = request.query_params.get("sector_id")
        if not sector_id:
            return response.Response({"items": self.get_serializer(queryset, many=True).data})

        sector = Sector.objects.select_related("market").filter(id=sector_id).first()
        items = StocksPricingService().get_stocks_with_prices(sector) if sector else []
        return response.Response(
            {
                "sector": {
                    "id": sector.id,
                    "name": sector.name,
                    "market": sector.market.name,
                    "market_code": sector.market.code,
                } if sector else None,
                "items": items,
            }
        )


class PortfolioGroupedView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response(StocksPortfolioService().grouped_portfolio(request.user))


class PortfolioInsightsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response(StocksPortfolioService().portfolio_insights(request.user))


def _ordered_india_sectors(queryset):
    ordering_cases = [
        When(name=name, then=Value(index))
        for index, name in enumerate(INDIA_NIFTY_SECTORS)
    ]
    return queryset.annotate(
        sort_order=Case(
            *ordering_cases,
            default=Value(len(INDIA_NIFTY_SECTORS)),
            output_field=IntegerField(),
        )
    ).order_by("sort_order", "name")
