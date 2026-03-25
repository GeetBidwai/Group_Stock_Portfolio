from django.urls import path

from apps.stocks_module.views import (
    AddStockToPortfolioView,
    PortfolioGroupedView,
    PortfolioInsightsView,
    RemoveStockFromPortfolioView,
)


urlpatterns = [
    path("", PortfolioGroupedView.as_view()),
    path("add/", AddStockToPortfolioView.as_view()),
    path("insights/", PortfolioInsightsView.as_view()),
    path("entries/<int:entry_id>/", RemoveStockFromPortfolioView.as_view()),
]
