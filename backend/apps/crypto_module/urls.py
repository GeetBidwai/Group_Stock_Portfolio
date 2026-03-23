from django.urls import path

from apps.crypto_module.views import BTCHourlyForecastView

urlpatterns = [path("btcusd-hourly", BTCHourlyForecastView.as_view())]
