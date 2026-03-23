from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.portfolio_module.models import PortfolioStock, PortfolioType, Sector
from apps.portfolio_module.serializers import (
    PortfolioStockSerializer,
    PortfolioTypeSerializer,
    SectorSerializer
)


# ✅ Portfolio Types
class PortfolioTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = PortfolioTypeSerializer

    def get_queryset(self):
        return PortfolioType.objects.filter(user=self.request.user)


class PortfolioTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioTypeSerializer

    def get_queryset(self):
        return PortfolioType.objects.filter(user=self.request.user)


# ✅ Portfolio Stocks
class PortfolioStockListCreateView(generics.ListCreateAPIView):
    serializer_class = PortfolioStockSerializer

    def get_queryset(self):
        return PortfolioStock.objects.filter(user=self.request.user).select_related("portfolio_type")


# ✅ Delete Stock
class PortfolioStockDeleteView(generics.DestroyAPIView):
    serializer_class = PortfolioStockSerializer

    def get_queryset(self):
        return PortfolioStock.objects.filter(user=self.request.user)


# ✅ NEW: Sector List + Create
class SectorListCreateView(generics.ListCreateAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [AllowAny]  # 👈 for testing
