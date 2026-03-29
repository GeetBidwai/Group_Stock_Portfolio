from rest_framework import serializers

from apps.quality_stocks_module.models import QualityStock


class QualitySnapshotRequestSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField(min_value=1)


class QualityGenerateRequestSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField(min_value=1)
    stock_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)


class QualitySectorSnapshotRequestSerializer(serializers.Serializer):
    sector_name = serializers.CharField(max_length=120)


class QualitySectorGenerateRequestSerializer(serializers.Serializer):
    sector_name = serializers.CharField(max_length=120)
    stock_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)


class QualityStockListSerializer(serializers.ModelSerializer):
    portfolio_name = serializers.CharField(source="portfolio.name", read_only=True)
    stock_symbol = serializers.CharField(source="stock.symbol", read_only=True)
    stock_name = serializers.SerializerMethodField()
    predicted_price = serializers.SerializerMethodField()
    explanation = serializers.SerializerMethodField()

    class Meta:
        model = QualityStock
        fields = (
            "id",
            "portfolio",
            "portfolio_name",
            "stock",
            "stock_symbol",
            "stock_name",
            "ai_rating",
            "buy_signal",
            "predicted_price",
            "explanation",
            "generated_at",
        )

    def get_stock_name(self, obj):
        return obj.stock.company_name or obj.stock.symbol

    def get_predicted_price(self, obj):
        metrics = (obj.report_json or {}).get("metrics") or {}
        return metrics.get("predicted_price")

    def get_explanation(self, obj):
        report_json = obj.report_json or {}
        return report_json.get("explanation") or report_json.get("summary")


class QualityStockDetailSerializer(serializers.ModelSerializer):
    portfolio_name = serializers.CharField(source="portfolio.name", read_only=True)
    stock_symbol = serializers.CharField(source="stock.symbol", read_only=True)
    stock_name = serializers.SerializerMethodField()

    class Meta:
        model = QualityStock
        fields = (
            "id",
            "portfolio",
            "portfolio_name",
            "stock",
            "stock_symbol",
            "stock_name",
            "ai_rating",
            "buy_signal",
            "report_json",
            "graphs_data",
            "generated_at",
        )

    def get_stock_name(self, obj):
        return obj.stock.company_name or obj.stock.symbol
