from django.urls import path

from apps.clustering_module.api.cluster_views import StockClusteringView

urlpatterns = [path("cluster-stocks/", StockClusteringView.as_view())]
