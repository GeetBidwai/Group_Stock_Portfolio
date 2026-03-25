from __future__ import annotations

INDIA_NIFTY_SECTORS = [
    "Nifty Auto",
    "Nifty Bank",
    "Nifty Commodities",
    "Nifty CPSE",
    "Nifty Energy",
    "Nifty FMCG",
    "Nifty IT",
    "Nifty Media",
    "Nifty Metal",
    "Nifty MNC",
    "Nifty Pharma",
    "Nifty PSE",
    "Nifty PSU Bank",
    "Nifty Realty",
]

INDIA_SOURCE_TO_NIFTY = {
    "Automobile and Auto Compo": "Nifty Auto",
    "Chemicals": "Nifty Commodities",
    "Construction": "Nifty PSE",
    "Construction Materials": "Nifty Commodities",
    "Consumer Durables": "Nifty MNC",
    "Consumer Services": "Nifty Media",
    "Fast Moving Consumer Good": "Nifty FMCG",
    "Financial Services": "Nifty Bank",
    "Healthcare": "Nifty Pharma",
    "Information Technology": "Nifty IT",
    "Metals & Mining": "Nifty Metal",
    "Oil Gas & Consumable Fuel": "Nifty Energy",
    "Power": "Nifty Energy",
    "Realty": "Nifty Realty",
    "Services": "Nifty PSE",
    "Telecommunication": "Nifty Media",
    "Textiles": "Nifty MNC",
}

PSU_BANK_SYMBOLS = {
    "BANKBARODA",
    "BANKINDIA",
    "CANBK",
    "CENTRALBK",
    "INDIANB",
    "IOB",
    "MAHABANK",
    "PNB",
    "PSB",
    "SBIN",
    "UCOBANK",
    "UNIONBANK",
}

CPSE_SYMBOLS = {
    "BDL",
    "BEL",
    "BHEL",
    "BPCL",
    "COALINDIA",
    "COCHINSHIP",
    "CONCOR",
    "GAIL",
    "HAL",
    "IOC",
    "NHPC",
    "NLCINDIA",
    "NTPC",
    "NTPCGREEN",
    "OIL",
    "ONGC",
    "POWERGRID",
    "RVNL",
}

PSE_SYMBOLS = {
    "IRCTC",
    "NBCC",
    "NMDC",
    "RAILTEL",
    "SJVN",
}

MNC_SYMBOLS = {
    "ABB",
    "BOSCHLTD",
    "CUMMINSIND",
    "COLPAL",
    "HINDUNILVR",
    "NESTLEIND",
    "SIEMENS",
}

MEDIA_SYMBOLS = {
    "BHARTIARTL",
    "BHARTIHEXA",
    "IDEA",
    "INDUSTOWER",
    "NAUKRI",
    "TATACOMM",
}


def normalize_code(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace(".", " ")
        .replace("-", " ")
        .replace("  ", " ")
        .strip()
        .replace(" ", "_")
    )


def map_india_sector(source_sector: str, symbol: str) -> str | None:
    normalized_symbol = symbol.strip().upper()

    if normalized_symbol in PSU_BANK_SYMBOLS:
        return "Nifty PSU Bank"
    if normalized_symbol in CPSE_SYMBOLS:
        return "Nifty CPSE"
    if normalized_symbol in PSE_SYMBOLS:
        return "Nifty PSE"
    if normalized_symbol in MNC_SYMBOLS:
        return "Nifty MNC"
    if normalized_symbol in MEDIA_SYMBOLS:
        return "Nifty Media"

    return INDIA_SOURCE_TO_NIFTY.get(source_sector)
