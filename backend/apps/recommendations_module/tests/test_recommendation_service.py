from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from apps.recommendations_module.services.recommendation_service import RecommendationService


class RecommendationServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.service = RecommendationService()

    def test_generate_recommendations_returns_fresh_payload(self):
        with patch.object(
            RecommendationService,
            "_fetch_recommendation_rows",
            return_value=self._sample_rows(14),
        ):
            payload = self.service.generate_recommendations()

        self.assertIn("top_buy", payload)
        self.assertIn("bottom_buy", payload)
        self.assertFalse(payload.get("is_fallback", False))
        self.assertGreaterEqual(payload.get("universe_size", 0), 10)
        self.assertTrue(cache.get(self.service.PRIMARY_CACHE_KEY))
        self.assertTrue(cache.get(self.service.LAST_GOOD_CACHE_KEY))

    def test_generate_recommendations_uses_last_good_on_failure(self):
        last_good_payload = {
            "top_buy": [{"symbol": "RELIANCE.NS", "name": "Reliance", "price": 123.45, "change_percent": 1.2, "reason": "High Momentum"}],
            "bottom_buy": [{"symbol": "ITC.NS", "name": "ITC", "price": 456.78, "change_percent": -0.9, "reason": "Undervalued Opportunity"}],
            "updated_at": "2026-03-27T10:00:00+00:00",
            "universe_size": 15,
            "top_stocks": [],
            "bottom_stocks": [],
            "is_fallback": False,
        }
        cache.set(self.service.LAST_GOOD_CACHE_KEY, last_good_payload, 300)

        with patch.object(
            RecommendationService,
            "_fetch_recommendation_rows",
            side_effect=RuntimeError("upstream failure"),
        ):
            payload = self.service.generate_recommendations()

        self.assertTrue(payload.get("is_fallback"))
        self.assertEqual(payload.get("top_buy"), last_good_payload["top_buy"])
        self.assertEqual(payload.get("bottom_buy"), last_good_payload["bottom_buy"])
        self.assertIn("message", payload)

    def test_generate_recommendations_raises_if_no_fallback_available(self):
        with (
            patch.object(
                RecommendationService,
                "_fetch_recommendation_rows",
                side_effect=RuntimeError("upstream failure"),
            ),
            patch.object(
                RecommendationService,
                "_fetch_recommendation_rows_from_local_cache",
                return_value=[],
            ),
            patch.object(
                RecommendationService,
                "_load_last_good_payload",
                return_value=None,
            ),
        ):
            with self.assertRaises(RuntimeError):
                self.service.generate_recommendations()

    def _sample_rows(self, count: int) -> list[dict]:
        rows = []
        for index in range(count):
            rows.append(
                {
                    "symbol": f"STOCK{index}.NS",
                    "name": f"Stock {index}",
                    "price": 100.0 + index,
                    "change_percent": float(index) / 10.0,
                    "five_day_change_percent": -1.0 if index % 2 == 0 else 1.0,
                    "avg_volume": 800_000.0 + (index * 1_000),
                    "volume_cv": 0.2,
                    "down_days": 2,
                }
            )
        return rows
