from django.core.cache import cache
from django.db.models import Q

from apps.stock_search_module.models import StockReference

DEFAULT_STOCK_REFERENCE_DATA = [
    {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "Technology", "exchange": "NSE"},
    {"symbol": "INFY", "name": "Infosys", "sector": "Technology", "exchange": "NSE"},
    {"symbol": "WIPRO", "name": "Wipro", "sector": "Technology", "exchange": "NSE"},
    {"symbol": "HCLTECH", "name": "HCL Technologies", "sector": "Technology", "exchange": "NSE"},
    {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Financial Services", "exchange": "NSE"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Financial Services", "exchange": "NSE"},
    {"symbol": "SBI", "name": "State Bank of India", "sector": "Financial Services", "exchange": "NSE"},
    {"symbol": "ITC", "name": "ITC", "sector": "Consumer Goods", "exchange": "NSE"},
    {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Industrials", "exchange": "NSE"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Automobile", "exchange": "NSE"},
    {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Healthcare", "exchange": "NSE"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom", "exchange": "NSE"},
    {"symbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Consumer Goods", "exchange": "NSE"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Automobile", "exchange": "NSE"},
]


class StockSearchService:
    CACHE_TIMEOUT_SECONDS = 60

    def get_queryset(self, query: str):
        self._ensure_seed_data()
        normalized_query = query.strip()
        cache_key = f"stock_search_ids:{normalized_query.lower()}"
        cached_ids = cache.get(cache_key)

        if cached_ids is not None:
            preserved_order = {stock_id: index for index, stock_id in enumerate(cached_ids)}
            queryset = StockReference.objects.filter(id__in=cached_ids, is_active=True).only("symbol", "name")
            return sorted(queryset, key=lambda item: preserved_order.get(item.id, len(preserved_order)))

        queryset = list(
            StockReference.objects.filter(is_active=True)
            .filter(Q(symbol__icontains=normalized_query) | Q(name__icontains=normalized_query))
            .only("id", "symbol", "name")
            .order_by("symbol")[:10]
        )
        cache.set(cache_key, [stock.id for stock in queryset], self.CACHE_TIMEOUT_SECONDS)
        return queryset

    def _ensure_seed_data(self):
        if StockReference.objects.filter(is_active=True).exists():
            return

        StockReference.objects.bulk_create(
            [StockReference(is_active=True, **payload) for payload in DEFAULT_STOCK_REFERENCE_DATA],
            ignore_conflicts=True,
        )
