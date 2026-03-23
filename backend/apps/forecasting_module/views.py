from rest_framework import response, views

from apps.forecasting_module.serializers import PortfolioForecastSerializer, StockForecastSerializer
from apps.forecasting_module.services import PortfolioForecastService, StockForecastingService


class StockForecastView(views.APIView):
    def post(self, request):
        serializer = StockForecastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = StockForecastingService().forecast(
                serializer.validated_data["symbol"],
                model_name=serializer.validated_data["model"],
                horizon=serializer.validated_data["horizon"],
            )
            status_code = result.pop("error_status", 200)
            return response.Response(result, status=status_code)
        except Exception as exc:
            print("STOCK FORECAST VIEW ERROR:", str(exc))
            return response.Response({"error": str(exc)}, status=500)


class PortfolioForecastView(views.APIView):
    def post(self, request):
        serializer = PortfolioForecastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(PortfolioForecastService().next_day(request.user, serializer.validated_data.get("portfolio_type_id")))
