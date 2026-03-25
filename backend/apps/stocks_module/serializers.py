from rest_framework import serializers

from apps.portfolio_module.models import Sector as PortfolioSector
from apps.portfolio_module.serializers import SectorSerializer as PortfolioSectorSerializer
from apps.stocks_module.models import Market, PortfolioEntry, Sector, Stock


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ("id", "code", "name")


class SectorSerializer(serializers.ModelSerializer):
    market_code = serializers.CharField(source="market.code", read_only=True)

    class Meta:
        model = Sector
        fields = ("id", "market", "market_code", "code", "name")


class AddToPortfolioSerializer(serializers.Serializer):
    stock_id = serializers.IntegerField()


class StockSerializer(serializers.ModelSerializer):
    sector_name = serializers.CharField(source="sector.name", read_only=True)
    market_code = serializers.CharField(source="sector.market.code", read_only=True)

    class Meta:
        model = Stock
        fields = ("id", "symbol", "name", "exchange", "sector", "sector_name", "market_code")


class PortfolioEntrySerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="stock.symbol", read_only=True)
    stock_name = serializers.CharField(source="stock.name", read_only=True)
    exchange = serializers.CharField(source="stock.exchange", read_only=True)

    class Meta:
        model = PortfolioEntry
        fields = ("id", "symbol", "stock_name", "exchange", "added_at")


class UnifiedSectorSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if isinstance(instance, PortfolioSector):
            return PortfolioSectorSerializer(instance).data
        return SectorSerializer(instance).data
