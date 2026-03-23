from rest_framework import response, views

from apps.crypto_module.services import BTCForecastService


class BTCHourlyForecastView(views.APIView):
    def get(self, request):
        return response.Response(BTCForecastService().hourly_forecast())
