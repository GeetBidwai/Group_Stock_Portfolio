from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.auth_module.urls")),
    path("api/auth/", include("apps.auth_telegram.urls")),
    path("api/portfolio-types/", include("apps.portfolio_module.portfolio_type_urls")),
    path("api/portfolio-stocks/", include("apps.portfolio_module.portfolio_stock_urls")),
    path("api/sectors/", include("apps.stocks_module.sector_urls")),
    path("api/stocks/", include("apps.stock_search_module.urls")),
    path("api/stocks/", include("apps.stocks_module.urls")),
    path("api/portfolio/", include("apps.analytics_module.urls")),
    path("api/portfolio/", include("apps.comparison_module.urls")),
    path("api/stock/", include("apps.risk_module.urls")),
    path("api/portfolio/", include("apps.clustering_module.urls")),
    path("api/portfolio/", include("apps.stocks_module.portfolio_urls")),
    path("api/", include("apps.clustering_module.cluster_stock_urls")),
    path("api/stock/", include("apps.forecasting_module.urls")),
    path("api/sentiment/", include("apps.sentiment_module.urls")),
    path("api/recommendations/", include("apps.recommendations_module.urls")),
    path("api/commodities/", include("apps.commodities_module.urls")),
    path("api/crypto/", include("apps.crypto_module.urls")),
    path("api/assistant/", include("apps.assistant_module.urls")),
]
