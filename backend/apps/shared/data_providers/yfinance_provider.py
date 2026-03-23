from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf
from django.conf import settings

from apps.shared.contracts.market_data import MarketDataProvider


@dataclass
class YFinanceMarketDataProvider(MarketDataProvider):
    default_suffix: str = ".NS"

    def __post_init__(self):
        cache_dir = Path(settings.BASE_DIR) / ".yfinance-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            yf.set_tz_cache_location(str(cache_dir))
        except Exception:
            pass

    def _normalize_symbol(self, symbol: str) -> str:
        symbol = symbol.upper().strip()
        if "." in symbol or "=" in symbol or "-" in symbol or "^" in symbol:
            return symbol
        return f"{symbol}{self.default_suffix}"

    def search_indian_stocks(self, query: str) -> list[dict]:
        query = query.strip()
        if not query:
            return []
        candidates = [query.upper(), f"{query.upper()}.NS", f"{query.upper()}.BO"]
        results = []
        for candidate in dict.fromkeys(candidates):
            try:
                ticker = yf.Ticker(candidate)
                info = ticker.info or {}
                history = ticker.history(period="5d")
                if history.empty and not info:
                    continue
                results.append(
                    {
                        "symbol": candidate,
                        "name": info.get("shortName", candidate),
                        "exchange": info.get("exchange", "NSE/BSE"),
                        "currency": info.get("currency", "INR"),
                    }
                )
            except Exception:
                continue
        return results

    def _candidate_symbols(self, symbol: str) -> list[str]:
        normalized = self._normalize_symbol(symbol)
        base_symbol = symbol.upper().strip()
        candidates = [normalized, base_symbol]
        if "." not in base_symbol and "=" not in base_symbol and "-" not in base_symbol and "^" not in base_symbol:
            candidates.extend([f"{base_symbol}.NS", f"{base_symbol}.BO"])
        return list(dict.fromkeys([candidate for candidate in candidates if candidate]))

    def _safe_history(self, ticker, period: str, interval: str) -> pd.DataFrame:
        try:
            return ticker.history(period=period, interval=interval)
        except Exception:
            return pd.DataFrame()

    def get_ticker_snapshot(self, symbol: str) -> dict:
        selected_symbol = self._normalize_symbol(symbol)
        info = {}
        history = pd.DataFrame()

        for candidate in self._candidate_symbols(symbol):
            ticker = yf.Ticker(candidate)
            try:
                candidate_info = ticker.info or {}
            except Exception:
                candidate_info = {}
            candidate_history = self._safe_history(ticker, period="1y", interval="1d")
            if candidate_info or not candidate_history.empty:
                selected_symbol = candidate
                info = candidate_info
                history = candidate_history
                break

        return {
            "symbol": selected_symbol,
            "name": info.get("shortName", symbol.upper()),
            "sector": info.get("sector"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "trailing_pe": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "market_cap": info.get("marketCap"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "history": self._history_frame_to_records(history),
        }

    def get_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> list[dict]:
        for candidate in self._candidate_symbols(symbol):
            ticker = yf.Ticker(candidate)
            history = self._safe_history(ticker, period=period, interval=interval)
            if not history.empty:
                return self._history_frame_to_records(history)
        return []

    def _history_frame_to_records(self, history: pd.DataFrame) -> list[dict]:
        if history is None or history.empty:
            return []
        frame = history.reset_index()
        date_col = frame.columns[0]
        return [
            {
                "date": str(row[date_col]),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
            }
            for _, row in frame.iterrows()
        ]
