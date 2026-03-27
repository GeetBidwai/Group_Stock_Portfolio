from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf
from django.core.cache import cache


@dataclass(frozen=True)
class UniverseStock:
    symbol: str
    name: str


class RecommendationService:
    CACHE_TIMEOUT_SECONDS = 300
    MAX_RESULTS = 10
    MIN_AVG_VOLUME = 500_000
    MAX_VOLUME_CV_FOR_VALUE = 0.45

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

    def generate_recommendations(self) -> dict:
        cache_key = "recommendations:payload:v2"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        rows = self._fetch_recommendation_rows()
        if not rows:
            raise RuntimeError("Unable to fetch recommendations")

        top_buy = self._build_top_buy(rows)
        bottom_buy = self._build_bottom_buy(rows)

        payload = {
            "top_buy": top_buy,
            "bottom_buy": bottom_buy,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "universe_size": len(rows),
            # Backward-compatible keys for existing RecommendationPage.
            "top_stocks": self._to_legacy_items(top_buy),
            "bottom_stocks": self._to_legacy_items(bottom_buy),
        }
        cache.set(cache_key, payload, self.CACHE_TIMEOUT_SECONDS)
        return payload

    def _fetch_recommendation_rows(self) -> list[dict]:
        tickers = [item.symbol for item in self.STOCK_UNIVERSE]
        universe_by_symbol = {item.symbol: item for item in self.STOCK_UNIVERSE}

        frame = yf.download(
            tickers=tickers,
            period="5d",
            interval="1d",
            progress=False,
            group_by="ticker",
            auto_adjust=False,
            threads=True,
        )
        if frame is None or frame.empty:
            return []

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
        return frame if symbol == self.STOCK_UNIVERSE[0].symbol else pd.DataFrame()

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
