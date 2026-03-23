from django.urls import path

from apps.comparison_module.views import StockComparisonView

urlpatterns = [path("compare", StockComparisonView.as_view())]
