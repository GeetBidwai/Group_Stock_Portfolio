from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.stocks_module.models import Market, PortfolioEntry, Sector, Stock
from apps.stocks_module.sector_mapping import INDIA_NIFTY_SECTORS, map_india_sector, normalize_code
from apps.stocks_module.workbook_parser import parse_stock_workbook


class Command(BaseCommand):
    help = "Seed India and USA sectors/stocks into stocks_module from the provided workbook."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Absolute path to the Excel workbook.")
        parser.add_argument(
            "--replace-existing",
            action="store_true",
            help="Replace existing stocks_module market/sector/stock catalog data before loading the workbook.",
        )

    def handle(self, *args, **options):
        workbook_path = options["path"]
        replace_existing = options["replace_existing"]
        workbook_rows = parse_stock_workbook(workbook_path)
        if not workbook_rows:
            raise CommandError("No stock rows were parsed from the workbook.")

        with transaction.atomic():
            if replace_existing:
                if PortfolioEntry.objects.exists():
                    raise CommandError(
                        "Cannot replace catalog data while PortfolioEntry rows exist. Clear those entries first."
                    )
                Stock.objects.all().delete()
                Sector.objects.all().delete()
                Market.objects.all().delete()

            created_markets = 0
            created_sectors = 0
            created_stocks = 0
            updated_stocks = 0

            market_names = {"IN": "India", "US": "USA"}
            markets = {}
            for market_code, market_name in market_names.items():
                market, market_created = Market.objects.get_or_create(
                    code=market_code,
                    defaults={"name": market_name},
                )
                if not market_created and market.name != market_name:
                    market.name = market_name
                    market.save(update_fields=["name"])
                if market_created:
                    created_markets += 1
                markets[market_code] = market

            sectors = {}
            for sector_name in INDIA_NIFTY_SECTORS:
                sector, sector_created = Sector.objects.get_or_create(
                    market=markets["IN"],
                    code=normalize_code(sector_name),
                    defaults={"name": sector_name},
                )
                if sector_created:
                    created_sectors += 1
                sectors[("IN", sector_name)] = sector

            seen_stock_ids = set()
            seen_sector_keys = set()

            for row in workbook_rows:
                if row.market_code == "IN":
                    target_sector_name = map_india_sector(row.source_sector, row.symbol)
                    if not target_sector_name:
                        # Keep rows even when a source sector is not in the Nifty mapping.
                        # This avoids silently dropping valid symbols such as "Capital Goods".
                        target_sector_name = row.source_sector
                else:
                    target_sector_name = row.source_sector

                market = markets[row.market_code]
                sector_key = (row.market_code, target_sector_name)
                sector = sectors.get(sector_key)
                if sector is None:
                    sector, sector_created = Sector.objects.get_or_create(
                        market=market,
                        code=normalize_code(target_sector_name),
                        defaults={"name": target_sector_name},
                    )
                    if sector_created:
                        created_sectors += 1
                    sectors[sector_key] = sector
                seen_sector_keys.add(sector_key)

                exchange = "NSE" if row.market_code == "IN" else "NASDAQ"
                stock = (
                    Stock.objects.select_related("sector", "sector__market")
                    .filter(symbol=row.symbol, sector__market=market)
                    .order_by("id")
                    .first()
                )

                if stock is None:
                    stock = Stock.objects.create(
                        sector=sector,
                        symbol=row.symbol,
                        name=row.company_name,
                        exchange=exchange,
                        is_active=True,
                    )
                    created_stocks += 1
                else:
                    dirty_fields = []
                    if stock.sector_id != sector.id:
                        stock.sector = sector
                        dirty_fields.append("sector")
                    if stock.name != row.company_name:
                        stock.name = row.company_name
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

            if replace_existing:
                Stock.objects.exclude(id__in=seen_stock_ids).update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete. "
                f"Markets: {created_markets}, "
                f"Sectors: {created_sectors}, "
                f"Stocks created: {created_stocks}, "
                f"Stocks updated: {updated_stocks}"
            )
        )
