from django.urls import path

from apps.stocks_module.views import (
    MarketListView,
    MarketSectorListView,
    SectorStockListView,
    StockCatalogListView,
)


urlpatterns = [
    path("", StockCatalogListView.as_view()),
    path("markets/", MarketListView.as_view()),
    path("markets/<str:code>/sectors/", MarketSectorListView.as_view()),
    path("sectors/<int:id>/stocks/", SectorStockListView.as_view()),
]
