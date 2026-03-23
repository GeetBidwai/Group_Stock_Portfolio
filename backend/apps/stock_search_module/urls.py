from django.urls import path

from apps.stock_search_module.views import StockSearchView
from apps.analytics_module.views import StockAnalyticsView

urlpatterns = [
    path("search", StockSearchView.as_view()),
    path("<str:symbol>/analytics", StockAnalyticsView.as_view()),
]
