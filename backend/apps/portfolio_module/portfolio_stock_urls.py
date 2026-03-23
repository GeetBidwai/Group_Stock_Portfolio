from django.urls import path

from apps.portfolio_module.views import PortfolioStockDeleteView, PortfolioStockListCreateView

urlpatterns = [
    path("", PortfolioStockListCreateView.as_view()),
    path("<int:pk>", PortfolioStockDeleteView.as_view()),
]
