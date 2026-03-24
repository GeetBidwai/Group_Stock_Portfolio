from django.urls import path

from apps.analytics_module.views import PortfolioPEComparisonView, PortfolioStockAnalyticsView

urlpatterns = [
    path("pe-comparison", PortfolioPEComparisonView.as_view()),
    path("portfolio-stock-analytics", PortfolioStockAnalyticsView.as_view()),
]
