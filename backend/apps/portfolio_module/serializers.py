from rest_framework import serializers
from apps.portfolio_module.models import PortfolioStock, PortfolioType, Sector


#  NEW: Sector Serializer
class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ("id", "name")


#  UPDATED: PortfolioTypeSerializer
class PortfolioTypeSerializer(serializers.ModelSerializer):
    # show sector name in response
    sector_name = serializers.CharField(source="sector.name", read_only=True)

    class Meta:
        model = PortfolioType
        fields = ("id", "name", "description", "sector", "sector_name", "created_at")

    def create(self, validated_data):
        return PortfolioType.objects.create(
            user=self.context["request"].user,
            **validated_data
        )


#  SAME: PortfolioStockSerializer (no change)
class PortfolioStockSerializer(serializers.ModelSerializer):
    portfolio_type_name = serializers.CharField(source="portfolio_type.name", read_only=True)

    class Meta:
        model = PortfolioStock
        fields = (
            "id",
            "portfolio_type",
            "portfolio_type_name",
            "symbol",
            "company_name",
            "quantity",
            "average_buy_price",
            "created_at",
        )

    def validate(self, attrs):
        user = self.context["request"].user
        exists = PortfolioStock.objects.filter(
            user=user,
            portfolio_type=attrs["portfolio_type"],
            symbol=attrs["symbol"].upper(),
        ).exists()
        if self.instance is None and exists:
            raise serializers.ValidationError("This stock already exists in the selected portfolio.")
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["symbol"] = validated_data["symbol"].upper()
        return super().create(validated_data)