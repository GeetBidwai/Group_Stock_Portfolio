from django.urls import path

from apps.forecasting_module.views import PortfolioForecastView, StockForecastView

urlpatterns = [
    path("forecast", StockForecastView.as_view()),
    path("portfolio-forecast-next-day", PortfolioForecastView.as_view()),
]
