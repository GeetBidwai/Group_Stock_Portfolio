from django.urls import path

from apps.clustering_module.views import PortfolioClusteringView

urlpatterns = [path("clustering", PortfolioClusteringView.as_view())]
