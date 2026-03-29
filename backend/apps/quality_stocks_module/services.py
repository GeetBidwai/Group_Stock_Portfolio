from __future__ import annotations

from django.core.cache import cache

from apps.analytics_module.services import StockAnalyticsService
from apps.forecasting_module.services import StockForecastingService
from apps.portfolio_module.models import PortfolioStock, PortfolioType, Sector as PortfolioSector
from apps.quality_stocks_module.models import QualityStock
from apps.sentiment_module.services.sentiment_service import SentimentAggregationService
from apps.stocks_module.models import PortfolioEntry


SIGNAL_WEIGHTS = {
    "BUY": 1.0,
    "HOLD": 0.0,
    "SELL": -1.0,
}


class QualityStocksService:
    SNAPSHOT_CACHE_TIMEOUT_SECONDS = 300

    def __init__(self):
        self.analytics_service = StockAnalyticsService()
        self.forecast_service = StockForecastingService()
        self.sentiment_service = SentimentAggregationService()

    def snapshot(self, user, portfolio_id: int) -> list[dict]:
        portfolio = self._get_portfolio(user, portfolio_id)
        if not portfolio:
            return []

        cache_key = f"quality-stocks:snapshot:{user.id}:{portfolio.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        stocks = list(
            PortfolioStock.objects.filter(user=user, portfolio_type=portfolio)
            .order_by("symbol")
        )
        items = [self._snapshot_item(stock) for stock in stocks]
        items = [item for item in items if item is not None]
        items.sort(key=lambda item: item["quality_score"], reverse=True)
        top_items = items[:3]
        cache.set(cache_key, top_items, self.SNAPSHOT_CACHE_TIMEOUT_SECONDS)
        return top_items

    def sector_snapshot(self, user, sector_name: str) -> list[dict]:
        normalized_sector = (sector_name or "").strip()
        if not normalized_sector:
            return []

        cache_key = f"quality-stocks:sector-snapshot:{user.id}:{normalized_sector.lower()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        entries = list(
            PortfolioEntry.objects.filter(user=user, sector__name=normalized_sector)
            .select_related("stock", "sector")
            .order_by("stock__symbol")
        )
        items = [
            self._snapshot_item_from_candidate(entry.id, entry.stock.symbol, entry.stock.name or entry.stock.symbol)
            for entry in entries
        ]
        items = [item for item in items if item is not None]
        items.sort(key=lambda item: item["quality_score"], reverse=True)
        top_items = items[:3]
        cache.set(cache_key, top_items, self.SNAPSHOT_CACHE_TIMEOUT_SECONDS)
        return top_items

    def generate_reports(self, user, portfolio_id: int, stock_ids: list[int]) -> list[QualityStock]:
        portfolio = self._get_portfolio(user, portfolio_id)
        if not portfolio:
            return []

        queryset = PortfolioStock.objects.filter(user=user, portfolio_type=portfolio, id__in=stock_ids).order_by("symbol")
        created_reports = []
        for stock in queryset:
            payload = self._build_report_payload(stock)
            report, _created = QualityStock.objects.update_or_create(
                portfolio=portfolio,
                stock=stock,
                defaults={
                    "user": user,
                    "ai_rating": payload["rating"],
                    "buy_signal": payload["signal"],
                    "report_json": payload["report_json"],
                    "graphs_data": payload["graphs_data"],
                },
            )
            created_reports.append(report)

        cache.delete(f"quality-stocks:snapshot:{user.id}:{portfolio.id}")
        return created_reports

    def generate_sector_reports(self, user, sector_name: str, entry_ids: list[int]) -> list[QualityStock]:
        normalized_sector = (sector_name or "").strip()
        if not normalized_sector:
            return []

        portfolio = self._get_or_create_sector_portfolio(user, normalized_sector)
        queryset = (
            PortfolioEntry.objects.filter(user=user, sector__name=normalized_sector, id__in=entry_ids)
            .select_related("stock", "sector")
            .order_by("stock__symbol")
        )

        created_reports = []
        for entry in queryset:
            mirror_stock = self._get_or_create_mirror_stock(user, portfolio, entry)
            payload = self._build_report_payload_for_symbol(entry.stock.symbol, entry.stock.name or entry.stock.symbol)
            report, _created = QualityStock.objects.update_or_create(
                portfolio=portfolio,
                stock=mirror_stock,
                defaults={
                    "user": user,
                    "ai_rating": payload["rating"],
                    "buy_signal": payload["signal"],
                    "report_json": payload["report_json"],
                    "graphs_data": payload["graphs_data"],
                },
            )
            created_reports.append(report)

        cache.delete(f"quality-stocks:sector-snapshot:{user.id}:{normalized_sector.lower()}")
        cache.delete(f"quality-stocks:snapshot:{user.id}:{portfolio.id}")
        return created_reports

    def rerun_report(self, user, report: QualityStock) -> QualityStock:
        payload = self._build_report_payload(report.stock)
        report.ai_rating = payload["rating"]
        report.buy_signal = payload["signal"]
        report.report_json = payload["report_json"]
        report.graphs_data = payload["graphs_data"]
        report.save(update_fields=["ai_rating", "buy_signal", "report_json", "graphs_data", "generated_at"])
        cache.delete(f"quality-stocks:snapshot:{user.id}:{report.portfolio_id}")
        return report

    def _get_portfolio(self, user, portfolio_id: int) -> PortfolioType | None:
        return PortfolioType.objects.filter(user=user, id=portfolio_id).first()

    def _get_or_create_sector_portfolio(self, user, sector_name: str) -> PortfolioType:
        portfolio_sector, _created = PortfolioSector.objects.get_or_create(name=sector_name)
        portfolio, created = PortfolioType.objects.get_or_create(
            user=user,
            name=sector_name,
            defaults={
                "description": "Auto-synced from sector portfolio for Quality Stocks.",
                "sector": portfolio_sector,
            },
        )
        updated_fields = []
        if portfolio.sector_id is None:
            portfolio.sector = portfolio_sector
            updated_fields.append("sector")
        if created and not portfolio.description:
            portfolio.description = "Auto-synced from sector portfolio for Quality Stocks."
            updated_fields.append("description")
        if updated_fields:
            portfolio.save(update_fields=updated_fields)
        return portfolio

    def _get_or_create_mirror_stock(self, user, portfolio: PortfolioType, entry: PortfolioEntry) -> PortfolioStock:
        stock, created = PortfolioStock.objects.get_or_create(
            user=user,
            portfolio_type=portfolio,
            symbol=entry.stock.symbol.upper(),
            defaults={
                "company_name": entry.stock.name or entry.stock.symbol,
                "quantity": 1,
            },
        )
        if not created and not stock.company_name and entry.stock.name:
            stock.company_name = entry.stock.name
            stock.save(update_fields=["company_name"])
        return stock

    def _normalize_market_symbol(self, symbol: str) -> str:
        normalized = (symbol or "").strip().upper()
        if not normalized:
            return normalized
        if "." in normalized or "=" in normalized or "^" in normalized:
            return normalized
        return f"{normalized}.NS"

    def _signal_from_opportunity(self, opportunity_signal: str | None) -> str:
        normalized = (opportunity_signal or "").strip().lower()
        if normalized in {"strong_upside", "moderate_upside"}:
            return "BUY"
        if normalized == "possibly_overvalued":
            return "SELL"
        return "HOLD"

    def _stock_inputs_for_symbol(self, symbol: str) -> dict:
        market_symbol = self._normalize_market_symbol(symbol)
        analytics = {}
        forecast = {}
        sentiment = {}

        try:
            analytics = self.analytics_service.get_stock_analytics(market_symbol)
        except Exception:
            analytics = {}

        try:
            forecast = self.forecast_service.forecast(market_symbol, horizon="3M")
        except Exception:
            forecast = {}

        try:
            sentiment = self.sentiment_service.analyze_stock(symbol)
        except Exception:
            sentiment = {"score": 0, "overall_sentiment": "Neutral"}

        current_price = float(analytics.get("current_price") or 0.0)
        predicted_price = forecast.get("prediction")
        if predicted_price is not None and current_price:
            try:
                expected_return = ((float(predicted_price) - current_price) / current_price) * 100
            except Exception:
                expected_return = float(analytics.get("discount_percentage") or 0.0)
        else:
            expected_return = float(analytics.get("discount_percentage") or 0.0)

        price_series = analytics.get("price_series") or []
        momentum = 0.0
        if len(price_series) >= 2:
            try:
                first_close = float(price_series[0].get("close") or 0.0)
                last_close = float(price_series[-1].get("close") or 0.0)
                if first_close:
                    momentum = ((last_close - first_close) / first_close) * 100
            except Exception:
                momentum = 0.0

        signal = self._signal_from_opportunity(analytics.get("opportunity_signal"))
        sentiment_score = float(sentiment.get("score") or 0.0)

        return {
            "analytics": analytics,
            "forecast": forecast,
            "sentiment": sentiment,
            "expected_return": expected_return,
            "sentiment_score": sentiment_score,
            "signal": signal,
            "momentum": momentum,
            "pe_ratio": analytics.get("trailing_pe"),
            "predicted_price": forecast.get("prediction"),
            "current_price": analytics.get("current_price"),
        }

    def _normalize_score(self, raw_score: float) -> float:
        bounded = max(min(raw_score, 20.0), -20.0)
        normalized = ((bounded + 20.0) / 40.0) * 10.0
        return round(max(0.0, min(10.0, normalized)), 2)

    def _signal_score(self, signal: str) -> float:
        return {"BUY": 1.0, "HOLD": 0.5, "SELL": 0.0}.get(signal, 0.5)

    def _momentum_score(self, history_items: list[dict]) -> float:
        closes = [float(point.get("close") or 0.0) for point in history_items if point.get("close") is not None]
        if len(closes) < 2:
            return 0.5

        last_close = closes[-1]
        thirty_index = max(0, len(closes) - 30)
        ninety_index = max(0, len(closes) - 90)
        base_30 = closes[thirty_index] or last_close
        base_90 = closes[ninety_index] or last_close

        trend_30 = ((last_close - base_30) / base_30) * 100 if base_30 else 0.0
        trend_90 = ((last_close - base_90) / base_90) * 100 if base_90 else 0.0
        blended = (trend_30 * 0.6) + (trend_90 * 0.4)
        normalized = (max(min(blended, 20.0), -20.0) + 20.0) / 40.0
        return round(max(0.0, min(1.0, normalized)), 4)

    def _pe_score(self, pe_ratio) -> float:
        try:
            pe_value = float(pe_ratio)
        except (TypeError, ValueError):
            return 0.5
        if pe_value <= 0:
            return 0.5
        return round(max(0.0, min(1.0, 1.0 - min(pe_value, 50.0) / 50.0)), 4)

    def _snapshot_quality_score(self, inputs: dict) -> tuple[float, dict]:
        expected_change_pct = max(min(float(inputs["expected_return"]), 20.0), -20.0)
        expected_component = (expected_change_pct + 20.0) / 40.0
        signal_component = self._signal_score(inputs["signal"])
        momentum_component = self._momentum_score(inputs["analytics"].get("price_series") or [])
        pe_component = self._pe_score(inputs.get("pe_ratio"))

        blended = (
            expected_component * 0.4 +
            signal_component * 0.2 +
            momentum_component * 0.2 +
            pe_component * 0.2
        )
        score = round(max(0.0, min(10.0, blended * 10.0)), 2)
        return score, {
            "expected_component": round(expected_component, 4),
            "signal_component": round(signal_component, 4),
            "momentum_component": round(momentum_component, 4),
            "pe_component": round(pe_component, 4),
        }

    def _stock_inputs(self, stock: PortfolioStock) -> dict:
        return self._stock_inputs_for_symbol(stock.symbol)

    def _snapshot_item(self, stock: PortfolioStock) -> dict | None:
        return self._snapshot_item_from_candidate(stock.id, stock.symbol, stock.company_name or stock.symbol)

    def _snapshot_item_from_candidate(self, candidate_id: int, symbol: str, company_name: str) -> dict | None:
        try:
            inputs = self._stock_inputs_for_symbol(symbol)
        except Exception:
            return None

        score, components = self._snapshot_quality_score(inputs)
        return {
            "stock_id": candidate_id,
            "symbol": symbol,
            "company": company_name or symbol,
            "price": inputs.get("current_price"),
            "predicted_price": inputs.get("predicted_price"),
            "expected_change_pct": round(float(inputs["expected_return"]), 2),
            "signal": inputs["signal"],
            "quality_score": score,
            "company_name": company_name or symbol,
            "reason": self._build_reason(inputs),
            "components": components,
        }

    def _build_reason(self, inputs: dict) -> str:
        parts = []
        if inputs["expected_return"] > 0:
            parts.append("projected upside")
        elif inputs["expected_return"] < 0:
            parts.append("forecast pressure")
        if inputs["sentiment_score"] > 0.15:
            parts.append("positive sentiment")
        elif inputs["sentiment_score"] < -0.15:
            parts.append("negative sentiment")
        if inputs["momentum"] > 0:
            parts.append("supportive momentum")
        elif inputs["momentum"] < 0:
            parts.append("weak momentum")
        if not parts:
            parts.append("mixed indicators")
        sentence = ", ".join(parts[:3])
        return sentence[:1].upper() + sentence[1:]

    def _build_report_payload(self, stock: PortfolioStock) -> dict:
        return self._build_report_payload_for_symbol(stock.symbol, stock.company_name or stock.symbol)

    def _build_report_payload_for_symbol(self, symbol: str, company_name: str) -> dict:
        inputs = self._stock_inputs_for_symbol(symbol)
        history_items = inputs["analytics"].get("price_series") or []
        closes = [float(point.get("close") or 0.0) for point in history_items if point.get("close") is not None]
        volatility = 0.0
        if len(closes) > 2:
            returns = []
            for previous, current in zip(closes[:-1], closes[1:]):
                if previous:
                    returns.append((current - previous) / previous)
            if returns:
                mean_return = sum(returns) / len(returns)
                variance = sum((item - mean_return) ** 2 for item in returns) / len(returns)
                volatility = variance ** 0.5

        pe_ratio = inputs.get("pe_ratio")
        pe_score = self._pe_score(pe_ratio)
        momentum_component = self._momentum_score(history_items)
        expected_component = (max(min(float(inputs["expected_return"]), 20.0), -20.0) + 20.0) / 40.0
        sentiment_component = (max(min(float(inputs["sentiment_score"]), 1.0), -1.0) + 1.0) / 2.0
        stability_component = 1.0 - max(min(volatility * 10.0, 1.0), 0.0)
        rating = round(
            max(
                0.0,
                min(
                    10.0,
                    (
                        expected_component * 0.25 +
                        sentiment_component * 0.15 +
                        momentum_component * 0.15 +
                        pe_score * 0.15 +
                        stability_component * 0.15 +
                        self._signal_score(inputs["signal"]) * 0.15
                    ) * 10.0,
                ),
            ),
            2,
        )

        analytics = inputs["analytics"]
        forecast = inputs["forecast"]
        sentiment = inputs["sentiment"]

        risks = []
        catalysts = []
        if inputs["expected_return"] < 0:
            risks.append("Forecast indicates limited upside in the current setup.")
        if inputs["sentiment_score"] < -0.15:
            risks.append("Recent sentiment signals are negative.")
        if inputs["momentum"] < 0:
            risks.append("Price momentum is currently soft.")
        if not risks:
            risks.append("No major near-term risk flag was detected from the current lightweight signals.")

        if inputs["expected_return"] > 0:
            catalysts.append("Model-based return outlook is positive.")
        if inputs["sentiment_score"] > 0.15:
            catalysts.append("Sentiment signal is supportive.")
        if inputs["momentum"] > 0:
            catalysts.append("Recent momentum is constructive.")
        if not catalysts:
            catalysts.append("Watch for fresh catalyst signals before a stronger conviction call.")

        explanation = self._build_summary(symbol, company_name, inputs)
        report_json = {
            "rating": rating,
            "signal": inputs["signal"],
            "summary": explanation,
            "explanation": explanation,
            "risks": risks,
            "catalysts": catalysts,
            "metrics": {
                "current_price": analytics.get("current_price"),
                "predicted_price": forecast.get("prediction"),
                "expected_return": round(float(inputs["expected_return"]), 2),
                "sentiment_score": round(float(inputs["sentiment_score"]), 4),
                "overall_sentiment": sentiment.get("overall_sentiment", "Neutral"),
                "momentum": round(float(inputs["momentum"]), 2),
                "trailing_pe": analytics.get("trailing_pe"),
                "market_cap": analytics.get("market_cap"),
                "volatility_beta_proxy": round(float(volatility), 4),
                "pe_score": pe_score,
                "momentum_score": momentum_component,
            },
        }
        graphs_data = {
            "history": analytics.get("price_series") or [],
            "forecast": forecast.get("predicted_series") or [],
        }
        return {
            "rating": rating,
            "signal": inputs["signal"],
            "report_json": report_json,
            "graphs_data": graphs_data,
        }

    def _build_summary(self, symbol: str, company_name: str, inputs: dict) -> str:
        signal_phrase = {
            "BUY": "leans positive",
            "HOLD": "looks balanced",
            "SELL": "leans cautious",
        }.get(inputs["signal"], "looks mixed")
        return (
            f"{company_name or symbol} {signal_phrase} based on expected return, sentiment, and momentum signals."
        )
