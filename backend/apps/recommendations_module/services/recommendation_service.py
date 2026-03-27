from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from pathlib import Path

import pandas as pd
import yfinance as yf
from django.conf import settings
from django.core.cache import cache

from apps.shared.services.market_data_service import MarketDataService


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UniverseStock:
    symbol: str
    name: str


class RecommendationService:
    PRIMARY_CACHE_KEY = "recommendations:payload:v2"
    LAST_GOOD_CACHE_KEY = "recommendations:payload:last_good:v2"
    CACHE_TIMEOUT_SECONDS = 300
    LAST_GOOD_CACHE_TIMEOUT_SECONDS = 21600
    FALLBACK_CACHE_TIMEOUT_SECONDS = 120
    MAX_RESULTS = 10
    MIN_ROWS_FOR_RECOMMENDATIONS = 10
    MIN_AVG_VOLUME = 500_000
    MAX_VOLUME_CV_FOR_VALUE = 0.45
    MAX_DOWNLOAD_RETRIES = 0
    CHUNK_SIZE = 25
    DOWNLOAD_TIMEOUT_SECONDS = 8

    STOCK_UNIVERSE: tuple[UniverseStock, ...] = (
        UniverseStock("RELIANCE.NS", "Reliance Industries"),
        UniverseStock("TCS.NS", "Tata Consultancy Services"),
        UniverseStock("HDFCBANK.NS", "HDFC Bank"),
        UniverseStock("BHARTIARTL.NS", "Bharti Airtel"),
        UniverseStock("ICICIBANK.NS", "ICICI Bank"),
        UniverseStock("INFY.NS", "Infosys"),
        UniverseStock("SBIN.NS", "State Bank of India"),
        UniverseStock("BAJFINANCE.NS", "Bajaj Finance"),
        UniverseStock("ITC.NS", "ITC"),
        UniverseStock("LT.NS", "Larsen & Toubro"),
        UniverseStock("HINDUNILVR.NS", "Hindustan Unilever"),
        UniverseStock("KOTAKBANK.NS", "Kotak Mahindra Bank"),
        UniverseStock("AXISBANK.NS", "Axis Bank"),
        UniverseStock("ASIANPAINT.NS", "Asian Paints"),
        UniverseStock("MARUTI.NS", "Maruti Suzuki"),
        UniverseStock("SUNPHARMA.NS", "Sun Pharmaceutical"),
        UniverseStock("TITAN.NS", "Titan Company"),
        UniverseStock("ULTRACEMCO.NS", "UltraTech Cement"),
        UniverseStock("NTPC.NS", "NTPC"),
        UniverseStock("POWERGRID.NS", "Power Grid Corporation"),
        UniverseStock("ONGC.NS", "ONGC"),
        UniverseStock("ADANIPORTS.NS", "Adani Ports"),
        UniverseStock("BAJAJFINSV.NS", "Bajaj Finserv"),
        UniverseStock("HCLTECH.NS", "HCL Technologies"),
        UniverseStock("WIPRO.NS", "Wipro"),
        UniverseStock("TECHM.NS", "Tech Mahindra"),
        UniverseStock("TATAMOTORS.NS", "Tata Motors"),
        UniverseStock("M&M.NS", "Mahindra & Mahindra"),
        UniverseStock("JSWSTEEL.NS", "JSW Steel"),
        UniverseStock("TATASTEEL.NS", "Tata Steel"),
        UniverseStock("COALINDIA.NS", "Coal India"),
        UniverseStock("INDUSINDBK.NS", "IndusInd Bank"),
        UniverseStock("DRREDDY.NS", "Dr Reddys Laboratories"),
        UniverseStock("CIPLA.NS", "Cipla"),
        UniverseStock("APOLLOHOSP.NS", "Apollo Hospitals"),
        UniverseStock("GRASIM.NS", "Grasim Industries"),
        UniverseStock("NESTLEIND.NS", "Nestle India"),
        UniverseStock("HEROMOTOCO.NS", "Hero MotoCorp"),
        UniverseStock("HDFCLIFE.NS", "HDFC Life"),
        UniverseStock("SBILIFE.NS", "SBI Life Insurance"),
        UniverseStock("EICHERMOT.NS", "Eicher Motors"),
        UniverseStock("ADANIENT.NS", "Adani Enterprises"),
        UniverseStock("BAJAJ-AUTO.NS", "Bajaj Auto"),
        UniverseStock("DIVISLAB.NS", "Divis Laboratories"),
        UniverseStock("HINDALCO.NS", "Hindalco Industries"),
        UniverseStock("BRITANNIA.NS", "Britannia Industries"),
        UniverseStock("TATACONSUM.NS", "Tata Consumer Products"),
        UniverseStock("SHRIRAMFIN.NS", "Shriram Finance"),
        UniverseStock("BPCL.NS", "BPCL"),
        UniverseStock("UPL.NS", "UPL"),
    )

    def __init__(self):
        self.reco_cache_dir = Path(settings.BASE_DIR) / ".recommendations-cache"
        self.reco_cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_good_file_path = self.reco_cache_dir / "last_good.json"

        # yfinance internally uses a tz cache DB. Ensure it points to a writable location.
        yf_cache_dir = Path(settings.BASE_DIR) / ".yfinance-cache"
        yf_cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            yf.set_tz_cache_location(str(yf_cache_dir))
        except Exception:
            logger.warning("Unable to set yfinance tz cache location.", exc_info=True)

    def generate_recommendations(self) -> dict:
        cached = cache.get(self.PRIMARY_CACHE_KEY)
        if cached is not None:
            return cached

        try:
            rows = self._fetch_recommendation_rows()
            if len(rows) < self.MIN_ROWS_FOR_RECOMMENDATIONS:
                cached_rows = self._fetch_recommendation_rows_from_local_cache()
                rows = self._merge_rows(rows, cached_rows)
            if len(rows) < self.MIN_ROWS_FOR_RECOMMENDATIONS:
                raise RuntimeError(
                    f"Insufficient recommendation rows: {len(rows)} (required {self.MIN_ROWS_FOR_RECOMMENDATIONS})"
                )

            top_buy = self._build_top_buy(rows)
            bottom_buy = self._build_bottom_buy(rows)

            payload = {
                "top_buy": top_buy,
                "bottom_buy": bottom_buy,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "universe_size": len(rows),
                "is_fallback": False,
                # Backward-compatible keys for existing RecommendationPage.
                "top_stocks": self._to_legacy_items(top_buy),
                "bottom_stocks": self._to_legacy_items(bottom_buy),
            }
            cache.set(self.PRIMARY_CACHE_KEY, payload, self.CACHE_TIMEOUT_SECONDS)
            cache.set(self.LAST_GOOD_CACHE_KEY, payload, self.LAST_GOOD_CACHE_TIMEOUT_SECONDS)
            self._store_last_good_payload(payload)
            return payload
        except Exception:
            logger.exception("Live recommendation generation failed.")
            fallback = cache.get(self.LAST_GOOD_CACHE_KEY) or self._load_last_good_payload()
            if fallback:
                fallback_payload = {
                    **fallback,
                    "is_fallback": True,
                    "message": "Live market data is temporarily unavailable. Showing the latest successful snapshot.",
                }
                cache.set(self.PRIMARY_CACHE_KEY, fallback_payload, self.FALLBACK_CACHE_TIMEOUT_SECONDS)
                logger.warning("Serving last known recommendation snapshot.")
                return fallback_payload
            raise RuntimeError("Unable to fetch recommendations")

    def _fetch_recommendation_rows(self) -> list[dict]:
        tickers = [item.symbol for item in self.STOCK_UNIVERSE]
        universe_by_symbol = {item.symbol: item for item in self.STOCK_UNIVERSE}

        frame = self._download_frame(tickers)
        if frame is not None and not frame.empty:
            return self._build_rows_from_frame(frame, tickers, universe_by_symbol)

        logger.warning("Bulk recommendation download returned no data; retrying in chunks.")
        rows: list[dict] = []
        for start in range(0, len(tickers), self.CHUNK_SIZE):
            batch = tickers[start:start + self.CHUNK_SIZE]
            batch_frame = self._download_frame(batch)
            if batch_frame is None or batch_frame.empty:
                logger.warning("Recommendation download failed for batch starting at index=%s", start)
                continue
            rows.extend(self._build_rows_from_frame(batch_frame, batch, universe_by_symbol))
        return rows

    def _fetch_recommendation_rows_from_local_cache(self) -> list[dict]:
        logger.warning("Attempting recommendation fallback from local yfinance cache.")
        market_data = MarketDataService()
        rows: list[dict] = []
        for stock in self.STOCK_UNIVERSE:
            snapshot = market_data.provider.get_cached_ticker_snapshot(stock.symbol) or {}
            history = snapshot.get("history") or []
            closes = [float(point.get("close")) for point in history if point.get("close") is not None]
            volumes = [float(point.get("volume")) for point in history if point.get("volume") is not None]

            closes = closes[-5:]
            volumes = volumes[-5:]
            if len(closes) < 3 or len(volumes) < 3:
                continue

            previous_close = closes[-2]
            latest_close = closes[-1]
            first_close = closes[0]
            if previous_close <= 0 or first_close <= 0:
                continue

            avg_volume = float(pd.Series(volumes).mean())
            if avg_volume < self.MIN_AVG_VOLUME:
                continue

            volume_std = float(pd.Series(volumes).std(ddof=0))
            volume_cv = volume_std / avg_volume if avg_volume > 0 else 999.0
            day_change_pct = ((latest_close - previous_close) / previous_close) * 100
            five_day_change_pct = ((latest_close - first_close) / first_close) * 100
            down_days = int((pd.Series(closes).diff().dropna() < 0).sum())

            rows.append(
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "price": round(latest_close, 2),
                    "change_percent": round(float(day_change_pct), 2),
                    "five_day_change_percent": round(float(five_day_change_pct), 2),
                    "avg_volume": avg_volume,
                    "volume_cv": round(float(volume_cv), 4),
                    "down_days": down_days,
                }
            )
        logger.warning("Local cache recommendation fallback produced %s rows.", len(rows))
        return rows

    def _download_frame(self, tickers: list[str]) -> pd.DataFrame:
        for attempt in range(self.MAX_DOWNLOAD_RETRIES + 1):
            try:
                frame = yf.download(
                    tickers=tickers,
                    period="5d",
                    interval="1d",
                    progress=False,
                    group_by="ticker",
                    auto_adjust=False,
                    threads=True,
                    timeout=self.DOWNLOAD_TIMEOUT_SECONDS,
                )
                if frame is not None and not frame.empty:
                    return frame
            except Exception:
                logger.warning(
                    "yfinance download attempt=%s failed for %s tickers.",
                    attempt + 1,
                    len(tickers),
                    exc_info=True,
                )
        return pd.DataFrame()

    def _build_rows_from_frame(
        self,
        frame: pd.DataFrame,
        tickers: list[str],
        universe_by_symbol: dict[str, UniverseStock],
    ) -> list[dict]:
        rows: list[dict] = []
        for symbol in tickers:
            stock_frame = self._extract_stock_frame(frame, symbol)
            if stock_frame.empty:
                continue

            clean = stock_frame.reindex(columns=["Close", "Volume"]).dropna()
            if len(clean) < 3:
                continue

            closes = pd.to_numeric(clean["Close"], errors="coerce").dropna()
            volumes = pd.to_numeric(clean["Volume"], errors="coerce").dropna()
            if len(closes) < 3 or len(volumes) < 3:
                continue

            previous_close = float(closes.iloc[-2])
            latest_close = float(closes.iloc[-1])
            first_close = float(closes.iloc[0])
            if previous_close <= 0 or first_close <= 0:
                continue

            avg_volume = float(volumes.mean())
            if avg_volume < self.MIN_AVG_VOLUME:
                continue

            volume_std = float(volumes.std(ddof=0))
            volume_cv = volume_std / avg_volume if avg_volume > 0 else 999.0

            day_change_pct = ((latest_close - previous_close) / previous_close) * 100
            five_day_change_pct = ((latest_close - first_close) / first_close) * 100
            down_days = int((closes.diff().dropna() < 0).sum())

            stock_meta = universe_by_symbol.get(symbol)
            rows.append(
                {
                    "symbol": symbol,
                    "name": stock_meta.name if stock_meta else symbol,
                    "price": round(latest_close, 2),
                    "change_percent": round(float(day_change_pct), 2),
                    "five_day_change_percent": round(float(five_day_change_pct), 2),
                    "avg_volume": avg_volume,
                    "volume_cv": round(float(volume_cv), 4),
                    "down_days": down_days,
                }
            )

        return rows

    def _extract_stock_frame(self, frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if isinstance(frame.columns, pd.MultiIndex):
            if symbol in frame.columns.get_level_values(0):
                return frame[symbol]
            if symbol in frame.columns.get_level_values(1):
                return frame.xs(symbol, axis=1, level=1)
            return pd.DataFrame()
        if {"Close", "Volume"}.issubset(set(frame.columns)):
            return frame
        return pd.DataFrame()

    def _merge_rows(self, primary_rows: list[dict], secondary_rows: list[dict]) -> list[dict]:
        merged: dict[str, dict] = {str(row.get("symbol")): row for row in primary_rows if row.get("symbol")}
        for row in secondary_rows:
            symbol = str(row.get("symbol") or "")
            if not symbol:
                continue
            if symbol not in merged:
                merged[symbol] = row
        return list(merged.values())

    def _store_last_good_payload(self, payload: dict) -> None:
        try:
            self.last_good_file_path.write_text(json.dumps(payload), encoding="utf-8")
        except Exception:
            logger.warning("Unable to persist last-good recommendations payload.", exc_info=True)

    def _load_last_good_payload(self) -> dict | None:
        if not self.last_good_file_path.exists():
            return None
        try:
            payload = json.loads(self.last_good_file_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            logger.warning("Unable to read last-good recommendations payload.", exc_info=True)
        return None

    def _build_top_buy(self, rows: list[dict]) -> list[dict]:
        ranked = sorted(rows, key=lambda row: row["change_percent"], reverse=True)
        return [
            {
                "symbol": row["symbol"],
                "name": row["name"],
                "price": row["price"],
                "change_percent": row["change_percent"],
                "reason": "High Momentum",
            }
            for row in ranked[: self.MAX_RESULTS]
        ]

    def _build_bottom_buy(self, rows: list[dict]) -> list[dict]:
        value_candidates = [
            row
            for row in rows
            if row["five_day_change_percent"] < 0
            and row["down_days"] >= 2
            and row["volume_cv"] <= self.MAX_VOLUME_CV_FOR_VALUE
        ]
        ranked_value = sorted(
            value_candidates,
            key=lambda row: (row["five_day_change_percent"], row["volume_cv"]),
        )

        if len(ranked_value) < self.MAX_RESULTS:
            existing = {row["symbol"] for row in ranked_value}
            fallback_pool = sorted(
                [row for row in rows if row["symbol"] not in existing],
                key=lambda row: row["five_day_change_percent"],
            )
            ranked_value.extend(fallback_pool[: self.MAX_RESULTS - len(ranked_value)])

        return [
            {
                "symbol": row["symbol"],
                "name": row["name"],
                "price": row["price"],
                "change_percent": row["change_percent"],
                "reason": "Undervalued Opportunity",
            }
            for row in ranked_value[: self.MAX_RESULTS]
        ]

    def _to_legacy_items(self, items: list[dict]) -> list[dict]:
        return [
            {
                "name": item["name"],
                "ticker": item["symbol"],
                "price": item["price"],
                "score": item["change_percent"],
                "reason": item["reason"],
            }
            for item in items
        ]
