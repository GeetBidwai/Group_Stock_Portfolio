from django.urls import path

from apps.commodities_module.commodity_views import CorrelationView, GoldView, SilverView
from apps.commodities_module.views import GoldSilverCorrelationView

urlpatterns = [
    path("gold-silver-correlation", GoldSilverCorrelationView.as_view()),
    path("gold/", GoldView.as_view()),
    path("silver/", SilverView.as_view()),
    path("correlation/", CorrelationView.as_view()),
]
