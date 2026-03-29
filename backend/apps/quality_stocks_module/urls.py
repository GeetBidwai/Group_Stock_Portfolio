from django.urls import path

from apps.quality_stocks_module.views import (
    QualityStocksDetailView,
    QualityStocksGenerateView,
    QualityStocksListView,
    QualityStocksRerunView,
    QualityStocksSectorGenerateView,
    QualityStocksSectorSnapshotView,
    QualityStocksSnapshotView,
)


urlpatterns = [
    path("", QualityStocksListView.as_view()),
    path("snapshot/", QualityStocksSnapshotView.as_view()),
    path("sector-snapshot/", QualityStocksSectorSnapshotView.as_view()),
    path("generate/", QualityStocksGenerateView.as_view()),
    path("sector-generate/", QualityStocksSectorGenerateView.as_view()),
    path("<int:pk>/", QualityStocksDetailView.as_view()),
    path("<int:pk>/rerun/", QualityStocksRerunView.as_view()),
]
