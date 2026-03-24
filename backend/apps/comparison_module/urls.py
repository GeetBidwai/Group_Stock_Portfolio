from django.urls import path

from apps.comparison_module.views import PortfolioStockOptionsView, StockComparisonView

urlpatterns = [
    path("compare", StockComparisonView.as_view()),
    path("stocks/", PortfolioStockOptionsView.as_view()),
]
