from rest_framework import serializers


class StockForecastSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    model = serializers.ChoiceField(choices=["ARIMA", "RNN"])
    horizon = serializers.ChoiceField(choices=["3M", "6M", "1Y"])


class PortfolioForecastSerializer(serializers.Serializer):
    portfolio_type_id = serializers.IntegerField(required=False)
