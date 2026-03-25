from django.db import migrations


CATALOG = {
    "IN": {
        "name": "India",
        "sectors": {
            "technology": {
                "name": "Technology",
                "stocks": [
                    ("TCS", "Tata Consultancy Services", "NSE"),
                    ("INFY", "Infosys", "NSE"),
                    ("WIPRO", "Wipro", "NSE"),
                    ("HCLTECH", "HCL Technologies", "NSE"),
                ],
            },
            "banking": {
                "name": "Banking",
                "stocks": [
                    ("HDFCBANK", "HDFC Bank", "NSE"),
                    ("ICICIBANK", "ICICI Bank", "NSE"),
                    ("SBIN", "State Bank of India", "NSE"),
                    ("AXISBANK", "Axis Bank", "NSE"),
                ],
            },
            "consumer": {
                "name": "Consumer",
                "stocks": [
                    ("ITC", "ITC", "NSE"),
                    ("HINDUNILVR", "Hindustan Unilever", "NSE"),
                    ("ASIANPAINT", "Asian Paints", "NSE"),
                    ("TITAN", "Titan Company", "NSE"),
                ],
            },
        },
    },
    "US": {
        "name": "United States",
        "sectors": {
            "technology": {
                "name": "Technology",
                "stocks": [
                    ("AAPL", "Apple", "NASDAQ"),
                    ("MSFT", "Microsoft", "NASDAQ"),
                    ("NVDA", "NVIDIA", "NASDAQ"),
                    ("GOOGL", "Alphabet", "NASDAQ"),
                ],
            },
            "finance": {
                "name": "Finance",
                "stocks": [
                    ("JPM", "JPMorgan Chase", "NYSE"),
                    ("BAC", "Bank of America", "NYSE"),
                    ("GS", "Goldman Sachs", "NYSE"),
                    ("WFC", "Wells Fargo", "NYSE"),
                ],
            },
            "healthcare": {
                "name": "Healthcare",
                "stocks": [
                    ("JNJ", "Johnson & Johnson", "NYSE"),
                    ("PFE", "Pfizer", "NYSE"),
                    ("MRK", "Merck", "NYSE"),
                    ("ABBV", "AbbVie", "NYSE"),
                ],
            },
        },
    },
}


def seed_catalog(apps, schema_editor):
    Market = apps.get_model("stocks_module", "Market")
    Sector = apps.get_model("stocks_module", "Sector")
    Stock = apps.get_model("stocks_module", "Stock")

    for market_code, market_payload in CATALOG.items():
        market, _ = Market.objects.get_or_create(code=market_code, defaults={"name": market_payload["name"]})
        for sector_code, sector_payload in market_payload["sectors"].items():
            sector, _ = Sector.objects.get_or_create(
                market=market,
                code=sector_code,
                defaults={"name": sector_payload["name"]},
            )
            for symbol, name, exchange in sector_payload["stocks"]:
                Stock.objects.get_or_create(
                    sector=sector,
                    symbol=symbol,
                    defaults={"name": name, "exchange": exchange, "is_active": True},
                )


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [("stocks_module", "0001_initial")]

    operations = [migrations.RunPython(seed_catalog, noop)]
