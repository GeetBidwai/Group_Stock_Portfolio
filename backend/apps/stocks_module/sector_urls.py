from django.urls import path

from apps.stocks_module.views import SectorCatalogListView


urlpatterns = [path("", SectorCatalogListView.as_view())]

