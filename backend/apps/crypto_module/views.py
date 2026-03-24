from rest_framework import response, views

from apps.crypto_module.btc_forecast_service import BTCForecastAnalyticsService
from apps.crypto_module.services import BTCForecastService


class BTCHourlyForecastView(views.APIView):
    def get(self, request):
        return response.Response(BTCForecastService().hourly_forecast())


class BTCForecastView(views.APIView):
    def get(self, request):
        range_key = request.query_params.get("range", "3m")
        return response.Response(BTCForecastAnalyticsService().build_payload(range_key))
