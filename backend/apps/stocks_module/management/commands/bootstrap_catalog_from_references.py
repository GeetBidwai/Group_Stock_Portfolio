from django.core.management.base import BaseCommand
from django.db import transaction

from apps.stock_search_module.models import StockReference
from apps.stocks_module.models import Market, Sector, Stock
from apps.stocks_module.sector_mapping import INDIA_NIFTY_SECTORS, map_india_sector, normalize_code


class Command(BaseCommand):
    help = "Populate stocks_module markets/sectors/stocks from stock_search_module.StockReference data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace-existing",
            action="store_true",
            help="Replace existing stocks_module catalog rows before rebuilding from StockReference.",
        )
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Mark existing stocks as inactive when they are not present in the StockReference source.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        replace_existing = options["replace_existing"]
        deactivate_missing = options["deactivate_missing"]

        references = list(
            StockReference.objects.filter(is_active=True)
            .exclude(symbol__isnull=True)
            .exclude(symbol__exact="")
            .order_by("symbol")
        )

        if not references:
            self.stdout.write(self.style.WARNING("No active StockReference rows found. Nothing to import."))
            return

        if replace_existing:
            Stock.objects.all().delete()
            Sector.objects.all().delete()
            Market.objects.all().delete()

        created_markets = 0
        created_sectors = 0
        created_stocks = 0
        updated_stocks = 0

        india_market, india_created = Market.objects.get_or_create(code="IN", defaults={"name": "India"})
        us_market, us_created = Market.objects.get_or_create(code="US", defaults={"name": "USA"})
        created_markets += int(india_created) + int(us_created)

        india_sectors = {}
        for sector_name in INDIA_NIFTY_SECTORS:
            sector, sector_created = Sector.objects.get_or_create(
                market=india_market,
                code=normalize_code(sector_name),
                defaults={"name": sector_name},
            )
            india_sectors[sector_name] = sector
            created_sectors += int(sector_created)

        seen_stock_ids = set()

        for reference in references:
            normalized_symbol = reference.symbol.strip().upper()
            market = self._market_for_reference(reference)
            if market.code == "IN":
                sector_name = map_india_sector(reference.sector or "", normalized_symbol)
                if not sector_name:
                    continue
                sector = india_sectors[sector_name]
                exchange = reference.exchange or "NSE"
            else:
                source_sector = (reference.sector or "General").strip() or "General"
                sector, sector_created = Sector.objects.get_or_create(
                    market=market,
                    code=normalize_code(source_sector),
                    defaults={"name": source_sector},
                )
                created_sectors += int(sector_created)
                exchange = reference.exchange or "NASDAQ"

            stock = (
                Stock.objects.select_related("sector", "sector__market")
                .filter(symbol=normalized_symbol, sector__market=market)
                .order_by("id")
                .first()
            )

            if stock is None:
                stock = Stock.objects.create(
                    sector=sector,
                    symbol=normalized_symbol,
                    name=reference.name or normalized_symbol,
                    exchange=exchange,
                    is_active=True,
                )
                created_stocks += 1
            else:
                dirty_fields = []
                if stock.sector_id != sector.id:
                    stock.sector = sector
                    dirty_fields.append("sector")
                if stock.name != (reference.name or normalized_symbol):
                    stock.name = reference.name or normalized_symbol
                    dirty_fields.append("name")
                if stock.exchange != exchange:
                    stock.exchange = exchange
                    dirty_fields.append("exchange")
                if not stock.is_active:
                    stock.is_active = True
                    dirty_fields.append("is_active")
                if dirty_fields:
                    stock.save(update_fields=dirty_fields)
                    updated_stocks += 1

            seen_stock_ids.add(stock.id)

        if deactivate_missing and seen_stock_ids:
            Stock.objects.exclude(id__in=seen_stock_ids).update(is_active=False)

        india_sector_count = Sector.objects.filter(market=india_market).count()
        india_stock_count = Stock.objects.filter(sector__market=india_market, is_active=True).count()
        us_stock_count = Stock.objects.filter(sector__market=us_market, is_active=True).count()

        self.stdout.write(
            self.style.SUCCESS(
                "Catalog bootstrap complete. "
                f"Markets created: {created_markets}, "
                f"Sectors created: {created_sectors}, "
                f"Stocks created: {created_stocks}, "
                f"Stocks updated: {updated_stocks}, "
                f"India sectors now: {india_sector_count}, "
                f"India stocks now: {india_stock_count}, "
                f"US stocks now: {us_stock_count}"
            )
        )

    def _market_for_reference(self, reference: StockReference) -> Market:
        exchange = (reference.exchange or "").strip().upper()
        symbol = reference.symbol.strip().upper()
        if exchange in {"NSE", "BSE"}:
            return Market.objects.get(code="IN")
        if exchange in {"NASDAQ", "NYSE", "AMEX"}:
            return Market.objects.get(code="US")

        if any(char == "." for char in symbol) and symbol.endswith(".NS"):
            return Market.objects.get(code="IN")
        return Market.objects.get(code="IN" if self._looks_indian_symbol(symbol) else "US")

    def _looks_indian_symbol(self, symbol: str) -> bool:
        return symbol.isupper() and len(symbol) <= 15
