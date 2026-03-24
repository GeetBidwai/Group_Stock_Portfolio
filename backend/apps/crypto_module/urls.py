from django.urls import path

from apps.crypto_module.views import BTCForecastView, BTCHourlyForecastView

urlpatterns = [
    path("btcusd-hourly", BTCHourlyForecastView.as_view()),
    path("btc-forecast/", BTCForecastView.as_view()),
]
