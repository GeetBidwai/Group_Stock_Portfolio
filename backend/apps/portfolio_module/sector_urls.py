from django.urls import path
from .views import SectorListCreateView   # ⚠️ use relative import

urlpatterns = [
    path("", SectorListCreateView.as_view()),
]