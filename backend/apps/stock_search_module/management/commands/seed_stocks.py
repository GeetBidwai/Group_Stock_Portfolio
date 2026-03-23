import time

import yfinance as yf
from django.core.management.base import BaseCommand

from apps.stock_search_module.models import StockReference


NIFTY_100_SYMBOLS = [
    "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "AMBUJACEM", "APOLLOHOSP", "ASIANPAINT",
    "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BANKBARODA", "BEL", "BERGEPAINT",
    "BHARTIARTL", "BHEL", "BIOCON", "BPCL", "BRITANNIA", "CANBK", "CHOLAFIN", "CIPLA", "COALINDIA",
    "DABUR", "DIVISLAB", "DLF", "DRREDDY", "EICHERMOT", "GAIL", "GODREJCP", "GRASIM", "HAVELLS", "HCLTECH",
    "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI",
    "IDBI", "IDFCFIRSTB", "IEX", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IRCTC", "ITC",
    "JINDALSTEL", "JIOFIN", "JSWENERGY", "JSWSTEEL", "KOTAKBANK", "LT", "LODHA", "LTIM", "M&M", "MARICO",
    "MARUTI", "MCDOWELL-N", "MOTHERSON", "NAUKRI", "NESTLEIND", "NHPC", "NTPC", "ONGC", "PAGEIND",
    "PAYTM", "PEL", "PIDILITIND", "PNB", "POLICYBZR", "POWERGRID", "RECLTD", "RELIANCE", "SAIL", "SBI",
    "SBICARD", "SBILIFE", "SHREECEM", "SIEMENS", "SRF", "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATAPOWER",
    "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT", "TVSMOTOR", "ULTRACEMCO", "VBL", "VEDL",
    "WIPRO", "ZOMATO",
]


class Command(BaseCommand):
    help = "Populate StockReference with Nifty 100 and equivalent Indian large-cap stocks using yfinance."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Number of stocks to process from the predefined NSE large-cap universe.",
        )
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Update existing records as well as creating missing ones.",
        )

    def handle(self, *args, **options):
        limit = max(1, options["limit"])
        refresh = options["refresh"]
        symbols = NIFTY_100_SYMBOLS[:limit]
        added_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE(f"Seeding {len(symbols)} NSE stocks into StockReference..."))

        for index, base_symbol in enumerate(symbols, start=1):
            nse_symbol = f"{base_symbol}.NS"
            try:
                existing = StockReference.objects.filter(symbol=base_symbol).first()
                if existing and not refresh:
                    self.stdout.write(self.style.SUCCESS(f"Added {existing.symbol}"))
                    continue

                payload = self._fetch_stock_payload(base_symbol, nse_symbol)
                if payload is None:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f"Skipped {base_symbol} (missing market data)"))
                    continue

                stock, created = StockReference.objects.update_or_create(
                    symbol=payload["symbol"],
                    defaults=payload,
                )

                if created:
                    added_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Added {stock.symbol}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated {stock.symbol}"))

            except Exception as exc:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Skipped {base_symbol} ({exc})"))

            if index % 5 == 0:
                time.sleep(0.2)
            else:
                time.sleep(0.1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed seeding. Added: {added_count}, Updated: {updated_count}, Skipped: {skipped_count}"
            )
        )

    def _fetch_stock_payload(self, base_symbol: str, nse_symbol: str) -> dict | None:
        ticker = yf.Ticker(nse_symbol)
        info = ticker.get_info()

        company_name = (
            info.get("shortName")
            or info.get("longName")
            or info.get("displayName")
            or base_symbol
        )
        sector = info.get("sector") or ""

        history = ticker.history(period="5d")
        if history.empty and not company_name:
            return None

        return {
            "symbol": base_symbol,
            "name": company_name,
            "sector": sector,
            "exchange": "NSE",
            "is_active": True,
        }
