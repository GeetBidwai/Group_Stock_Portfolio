from dataclasses import dataclass
from pathlib import Path
import json
from time import time

import pandas as pd
import requests
import yfinance as yf
from django.conf import settings
from yfinance.exceptions import YFRateLimitError

from apps.shared.contracts.market_data import MarketDataProvider


@dataclass
class YFinanceMarketDataProvider(MarketDataProvider):
    default_suffix: str = ".NS"
    symbol_aliases: dict = None
    snapshot_ttl_seconds: int = 900
    history_ttl_seconds: dict = None

    def __post_init__(self):
        if self.symbol_aliases is None:
            self.symbol_aliases = {
                "SBI": "SBIN",
            }
        if self.history_ttl_seconds is None:
            self.history_ttl_seconds = {
                "1h": 900,
                "1d": 21600,
                "1wk": 86400,
            }
        cache_dir = Path(settings.BASE_DIR) / ".yfinance-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_cache_dir = cache_dir / "snapshots"
        self.snapshot_cache_dir.mkdir(parents=True, exist_ok=True)
        self.history_cache_dir = cache_dir / "history"
        self.history_cache_dir.mkdir(parents=True, exist_ok=True)
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
        except YFRateLimitError:
            raise
        except Exception:
            return pd.DataFrame()

    def get_ticker_snapshot(self, symbol: str) -> dict:
        cached_payload = self._load_cached_snapshot(symbol, max_age_seconds=self.snapshot_ttl_seconds)
        if cached_payload is not None:
            return cached_payload

        selected_symbol = self._normalize_symbol(symbol)
        info = {}
        history = pd.DataFrame()
        chart_meta = {}

        try:
            for candidate in self._candidate_symbols(symbol):
                ticker = yf.Ticker(candidate)
                try:
                    candidate_info = ticker.info or {}
                except YFRateLimitError:
                    raise
                except Exception:
                    candidate_info = {}
                candidate_history = self._safe_history(ticker, period="1y", interval="1d")
                if candidate_info or not candidate_history.empty:
                    selected_symbol = candidate
                    info = candidate_info
                    history = candidate_history
                    break
        except YFRateLimitError:
            cached_payload = self._load_cached_snapshot(symbol)
            if cached_payload is not None:
                return cached_payload
            history = pd.DataFrame(self._load_cached_history(symbol, period="1y", interval="1d") or [])

        if history.empty:
            chart_payload = self._fetch_chart_payload(symbol, period="1y", interval="1d")
            if chart_payload is not None:
                selected_symbol = chart_payload["symbol"]
                chart_meta = chart_payload["meta"]
                history = pd.DataFrame(chart_payload["history"])

        latest_close = None
        if history is not None and not history.empty and "Close" in history:
            try:
                latest_close = float(history["Close"].dropna().iloc[-1])
            except Exception:
                latest_close = None

        trailing_pe = info.get("trailingPE") or info.get("forwardPE")
        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or chart_meta.get("regularMarketPrice")
            or chart_meta.get("previousClose")
            or latest_close
        )
        trailing_eps = info.get("trailingEps")
        if trailing_pe is None and current_price and trailing_eps:
            try:
                trailing_pe = float(current_price) / float(trailing_eps)
            except Exception:
                trailing_pe = None

        payload = {
            "symbol": selected_symbol,
            "name": info.get("shortName") or info.get("longName") or chart_meta.get("shortName") or symbol.upper(),
            "sector": info.get("sector"),
            "current_price": current_price,
            "trailing_pe": trailing_pe,
            "eps": trailing_eps,
            "market_cap": info.get("marketCap"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "currency": info.get("currency") or chart_meta.get("currency"),
            "history": self._history_frame_to_records(history),
        }
        if self._has_usable_snapshot(payload):
            self._store_snapshot(payload, symbol)
            self._store_history(symbol, period="1y", interval="1d", records=payload["history"])
            return payload

        cached_payload = self._load_cached_snapshot(symbol)
        if cached_payload is not None:
            return cached_payload
        return payload

    def get_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> list[dict]:
        cached_history = self._load_cached_history(symbol, period, interval, max_age_seconds=self._history_ttl(interval))
        if cached_history:
            return cached_history

        for candidate in self._candidate_symbols(symbol):
            ticker = yf.Ticker(candidate)
            try:
                history = self._safe_history(ticker, period=period, interval=interval)
            except YFRateLimitError:
                cached_history = self._load_cached_history(symbol, period, interval)
                if cached_history:
                    return cached_history
                cached_snapshot = self._load_cached_snapshot(symbol)
                if cached_snapshot is not None:
                    return cached_snapshot.get("history", [])
                break
            if not history.empty:
                records = self._history_frame_to_records(history)
                self._store_history(symbol, period, interval, records)
                return records

        chart_payload = self._fetch_chart_payload(symbol, period, interval)
        if chart_payload is not None:
            records = chart_payload["history"]
            self._store_history(symbol, period, interval, records)
            return records

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
        open_col = "Open" if "Open" in frame.columns else "open"
        high_col = "High" if "High" in frame.columns else "high"
        low_col = "Low" if "Low" in frame.columns else "low"
        close_col = "Close" if "Close" in frame.columns else "close"
        volume_col = "Volume" if "Volume" in frame.columns else "volume"
        return [
            {
                "date": str(row[date_col]),
                "open": float(row[open_col]),
                "high": float(row[high_col]),
                "low": float(row[low_col]),
                "close": float(row[close_col]),
                "volume": float(row[volume_col]),
            }
            for _, row in frame.iterrows()
        ]

    def _snapshot_cache_path(self, symbol: str) -> Path:
        normalized = symbol.upper().strip().replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.snapshot_cache_dir / f"{normalized}.json"

    def _history_cache_path(self, symbol: str, period: str, interval: str) -> Path:
        normalized_symbol = symbol.upper().strip().replace("/", "_").replace("\\", "_").replace(":", "_")
        normalized_period = period.strip().replace("/", "_")
        normalized_interval = interval.strip().replace("/", "_")
        return self.history_cache_dir / f"{normalized_symbol}__{normalized_period}__{normalized_interval}.json"

    def _store_snapshot(self, payload: dict, symbol: str):
        cache_candidates = {symbol.upper().strip(), str(payload.get("symbol", "")).upper().strip()}
        for candidate in [item for item in cache_candidates if item]:
            try:
                self._snapshot_cache_path(candidate).write_text(json.dumps(payload), encoding="utf-8")
            except Exception:
                continue

    def _load_cached_snapshot(self, symbol: str, max_age_seconds: int | None = None) -> dict | None:
        for candidate in self._candidate_symbols(symbol):
            path = self._snapshot_cache_path(candidate)
            if not path.exists():
                continue
            try:
                if max_age_seconds is not None and (time() - path.stat().st_mtime) > max_age_seconds:
                    continue
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
        return None

    def _store_history(self, symbol: str, period: str, interval: str, records: list[dict]):
        if not records:
            return
        for candidate in self._candidate_symbols(symbol):
            path = self._history_cache_path(candidate, period, interval)
            try:
                path.write_text(json.dumps(records), encoding="utf-8")
            except Exception:
                continue

    def _load_cached_history(self, symbol: str, period: str, interval: str, max_age_seconds: int | None = None) -> list[dict]:
        for candidate in self._candidate_symbols(symbol):
            path = self._history_cache_path(candidate, period, interval)
            if not path.exists():
                continue
            try:
                if max_age_seconds is not None and (time() - path.stat().st_mtime) > max_age_seconds:
                    continue
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
        return []

    def _history_ttl(self, interval: str) -> int:
        return self.history_ttl_seconds.get(interval, 21600)

    def _fetch_chart_payload(self, symbol: str, period: str, interval: str) -> dict | None:
        headers = {"User-Agent": "Mozilla/5.0"}
        for candidate in self._candidate_symbols(symbol):
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{candidate}"
            try:
                response = requests.get(
                    url,
                    params={"range": period, "interval": interval, "includePrePost": "false"},
                    headers=headers,
                    timeout=15,
                )
                if response.status_code != 200:
                    continue
                data = response.json()
                result = ((data.get("chart") or {}).get("result") or [None])[0]
                if not result:
                    continue
                records = self._chart_result_to_records(result)
                if not records:
                    continue
                return {
                    "symbol": candidate,
                    "meta": result.get("meta") or {},
                    "history": records,
                }
            except Exception:
                continue
        return None

    def _chart_result_to_records(self, result: dict) -> list[dict]:
        timestamps = result.get("timestamp") or []
        indicators = result.get("indicators") or {}
        quotes = indicators.get("quote") or []
        if not timestamps or not quotes:
            return []

        quote = quotes[0] or {}
        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        volumes = quote.get("volume") or []

        frame = pd.DataFrame(
            {
                "timestamp": timestamps,
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
            }
        )
        frame = frame.dropna(subset=["timestamp", "close"]).reset_index(drop=True)
        if frame.empty:
            return []

        frame["date"] = pd.to_datetime(frame["timestamp"], unit="s", utc=True).astype(str)
        for column in ["open", "high", "low", "close", "volume"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame["open"] = frame["open"].fillna(frame["close"])
        frame["high"] = frame["high"].fillna(frame["close"])
        frame["low"] = frame["low"].fillna(frame["close"])
        frame["volume"] = frame["volume"].fillna(0)

        return [
            {
                "date": row["date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
            for _, row in frame.iterrows()
        ]

    def _has_usable_snapshot(self, payload: dict) -> bool:
        return bool(
            payload.get("current_price") is not None
            or payload.get("trailing_pe") is not None
            or payload.get("history")
        )
