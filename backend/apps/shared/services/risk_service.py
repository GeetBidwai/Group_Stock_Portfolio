from __future__ import annotations

import numpy as np
from django.conf import settings


class RiskService:
    def calculate_volatility(self, prices: list[float] | np.ndarray) -> float | None:
        values = np.asarray(prices, dtype=float)
        if values.size < 2:
            return None

        returns = np.diff(values) / values[:-1]
        returns = returns[np.isfinite(returns)]
        if returns.size == 0:
            return None
        return float(np.std(returns))

    def categorize_risk(self, volatility: float | None, thresholds: dict | None = None) -> str:
        configured_thresholds = thresholds or getattr(settings, "RISK_THRESHOLDS", {"low": 0.01, "medium": 0.02})
        if volatility is None:
            return "Unknown"
        if volatility < configured_thresholds["low"]:
            return "Low"
        if volatility < configured_thresholds["medium"]:
            return "Medium"
        return "High"
