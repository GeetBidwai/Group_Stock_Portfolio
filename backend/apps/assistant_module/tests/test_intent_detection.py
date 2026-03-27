from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.assistant_module.intent_detection import IntentDetectionService


class IntentDetectionServiceTests(APITestCase):
    def setUp(self):
        self.service = IntentDetectionService()

    def test_detects_portfolio_summary(self):
        result = self.service.detect("How is my portfolio?")
        self.assertEqual(result["intent"], "portfolio_summary")
        self.assertEqual(result["entities"], {})

    def test_detects_compare_stocks(self):
        result = self.service.detect("Compare TCS and Infosys")
        self.assertEqual(result["intent"], "compare_stocks")
        self.assertEqual(result["entities"]["stocks"], ["TCS", "Infosys"])

    def test_detects_crypto(self):
        result = self.service.detect("Predict bitcoin price")
        self.assertEqual(result["intent"], "crypto")
        self.assertEqual(result["entities"]["stock"], "BTC")

    def test_detects_forecast_with_timeframe(self):
        result = self.service.detect("Forecast TCS for 3 months")
        self.assertEqual(result["intent"], "forecast")
        self.assertEqual(result["entities"]["stock"], "TCS")
        self.assertEqual(result["entities"]["timeframe"], "3 months")


class PersonalAssistantChatToneTests(APITestCase):
    def test_small_talk_how_are_you_is_handled(self):
        from apps.assistant_module.services import PersonalAssistantService

        response = PersonalAssistantService()._direct_reply(user=None, message="how are you", holdings=[])
        self.assertIn("doing well", response.lower())

    def test_compare_reply_handles_symbol_format_variants(self):
        from apps.assistant_module.services import PersonalAssistantService

        holdings = [
            {"symbol": "ACC", "name": "ACC Ltd.", "sector": "Cement"},
            {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Ltd.", "sector": "Auto"},
        ]

        symbols = PersonalAssistantService()._extract_symbols("Compare ACC and Bajaj auto", holdings)
        self.assertEqual(symbols, ["ACC", "BAJAJ-AUTO"])


class DetectIntentApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="tester", password="secret123")

    def test_detect_intent_endpoint_returns_strict_shape(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/assistant/detect-intent/", {"message": "Compare TCS and Infosys"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "intent": "compare_stocks",
                "entities": {
                    "stocks": ["TCS", "Infosys"],
                },
            },
        )
