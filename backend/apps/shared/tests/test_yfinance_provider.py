from django.test import SimpleTestCase

from apps.shared.data_providers.yfinance_provider import YFinanceMarketDataProvider


class YFinanceMarketDataProviderTests(SimpleTestCase):
    def test_candidate_symbols_include_nse_variant_for_hyphenated_symbols(self):
        provider = YFinanceMarketDataProvider()

        candidates = provider._candidate_symbols("BAJAJ-AUTO")

        self.assertIn("BAJAJ-AUTO.NS", candidates)
