from django.test import SimpleTestCase

from apps.commodities_module.commodity_service import CommodityAnalyticsService


class CommodityAnalyticsServiceTests(SimpleTestCase):
    def test_calculate_correlation_returns_value(self):
        service = CommodityAnalyticsService()

        gold_df = service._load_history_frame(service.GOLD_TICKER)
        silver_df = service._load_history_frame(service.SILVER_TICKER)

        self.assertGreaterEqual(len(gold_df), 2)
        self.assertGreaterEqual(len(silver_df), 2)
        correlation = service.calculate_correlation(gold_df, silver_df)
        self.assertIsInstance(correlation, float)

    def test_gold_unit_conversion_shape(self):
        service = CommodityAnalyticsService()
        converted = service._gold_to_inr_per_10g(3000.0, 83.0)
        self.assertGreater(converted, 0)

    def test_silver_unit_conversion_shape(self):
        service = CommodityAnalyticsService()
        converted = service._silver_to_inr_per_kg(35.0, 83.0)
        self.assertGreater(converted, 0)

    def test_forecast_steps_present(self):
        service = CommodityAnalyticsService()
        self.assertEqual(set(service.FORECAST_STEPS.keys()), {"3m", "6m", "1y"})
