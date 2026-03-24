from dataclasses import dataclass
from pathlib import Path
import json

import pandas as pd
import yfinance as yf
from django.conf import settings

from apps.shared.contracts.market_data import MarketDataProvider


@dataclass
class YFinanceMarketDataProvider(MarketDataProvider):
    default_suffix: str = ".NS"
    symbol_aliases: dict = None

    def __post_init__(self):
        if self.symbol_aliases is None:
            self.symbol_aliases = {
                "SBI": "SBIN",
            }
        cache_dir = Path(settings.BASE_DIR) / ".yfinance-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_cache_dir = cache_dir / "snapshots"
        self.snapshot_cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            yf.set_tz_cache_location(str(cache_dir))
        except Exception:
            pass

    def _normalize_symbol(self, symbol: str) -> str:
        symbol = symbol.upper().strip()
        symbol = self.symbol_aliases.get(symbol, symbol)
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
        raw_symbol = symbol.upper().strip()
        aliased_symbol = self.symbol_aliases.get(raw_symbol, raw_symbol)
        normalized = self._normalize_symbol(symbol)
        base_symbol = aliased_symbol
        candidates = [normalized, base_symbol]
        if "." not in base_symbol and "=" not in base_symbol and "-" not in base_symbol and "^" not in base_symbol:
            candidates.extend([f"{base_symbol}.NS", f"{base_symbol}.BO"])
        if aliased_symbol != raw_symbol:
            candidates.extend([raw_symbol, f"{raw_symbol}.NS", f"{raw_symbol}.BO"])
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

        latest_close = None
        if history is not None and not history.empty and "Close" in history:
            try:
                latest_close = float(history["Close"].dropna().iloc[-1])
            except Exception:
                latest_close = None

        trailing_pe = info.get("trailingPE") or info.get("forwardPE")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or latest_close
        trailing_eps = info.get("trailingEps")
        if trailing_pe is None and current_price and trailing_eps:
            try:
                trailing_pe = float(current_price) / float(trailing_eps)
            except Exception:
                trailing_pe = None

        payload = {
            "symbol": selected_symbol,
            "name": info.get("shortName", symbol.upper()),
            "sector": info.get("sector"),
            "current_price": current_price,
            "trailing_pe": trailing_pe,
            "eps": trailing_eps,
            "market_cap": info.get("marketCap"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "history": self._history_frame_to_records(history),
        }
        if self._has_usable_snapshot(payload):
            self._store_snapshot(payload, symbol)
            return payload

        cached_payload = self._load_cached_snapshot(symbol)
        if cached_payload is not None:
            return cached_payload
        return payload

    def get_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> list[dict]:
        for candidate in self._candidate_symbols(symbol):
            ticker = yf.Ticker(candidate)
            history = self._safe_history(ticker, period=period, interval=interval)
            if not history.empty:
                return self._history_frame_to_records(history)
        cached_snapshot = self._load_cached_snapshot(symbol)
        if cached_snapshot is not None:
            return cached_snapshot.get("history", [])
        return []

    def get_cached_ticker_snapshot(self, symbol: str) -> dict | None:
        return self._load_cached_snapshot(symbol)

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

    def _snapshot_cache_path(self, symbol: str) -> Path:
        normalized = symbol.upper().strip().replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.snapshot_cache_dir / f"{normalized}.json"

    def _store_snapshot(self, payload: dict, symbol: str):
        cache_candidates = {symbol.upper().strip(), str(payload.get("symbol", "")).upper().strip()}
        for candidate in [item for item in cache_candidates if item]:
            try:
                self._snapshot_cache_path(candidate).write_text(json.dumps(payload), encoding="utf-8")
            except Exception:
                continue

    def _load_cached_snapshot(self, symbol: str) -> dict | None:
        for candidate in self._candidate_symbols(symbol):
            path = self._snapshot_cache_path(candidate)
            if not path.exists():
                continue
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
        return None

    def _has_usable_snapshot(self, payload: dict) -> bool:
        return bool(
            payload.get("current_price") is not None
            or payload.get("trailing_pe") is not None
            or payload.get("history")
        )
