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

    def test_capability_question_is_not_misread_as_portfolio_list(self):
        from apps.assistant_module.services import PersonalAssistantService

        response = PersonalAssistantService()._direct_reply(
            user=None,
            message="Can I create my own portfolio here?",
            holdings=[{"symbol": "MOTHERSON", "name": "Samvardhana Motherson", "sector": "Auto"}],
        )
        self.assertIn("create and manage your own portfolio", response.lower())

    def test_portfolio_list_question_still_returns_holdings(self):
        from apps.assistant_module.services import PersonalAssistantService

        response = PersonalAssistantService()._direct_reply(
            user=None,
            message="What is in my portfolio?",
            holdings=[{"symbol": "MOTHERSON", "name": "Samvardhana Motherson", "sector": "Auto"}],
        )
        self.assertIn("you currently have 1 portfolio stocks", response.lower())

    def test_acknowledgement_message_gets_natural_reply(self):
        from apps.assistant_module.services import PersonalAssistantService

        response = PersonalAssistantService()._direct_reply(user=None, message="okay", holdings=[])
        self.assertIn("what would you like to explore next", response.lower())

    def test_portfolio_info_phrase_returns_portfolio_summary(self):
        from apps.assistant_module.services import PersonalAssistantService

        response = PersonalAssistantService()._direct_reply(
            user=None,
            message="I want information about my portfolio",
            holdings=[{"symbol": "MOTHERSON", "name": "Samvardhana Motherson", "sector": "Auto"}],
        )
        self.assertIn("you currently have 1 portfolio stocks", response.lower())

    def test_typo_in_portfolio_is_handled(self):
        from apps.assistant_module.services import PersonalAssistantService

        response = PersonalAssistantService()._direct_reply(
            user=None,
            message="show my portfilio",
            holdings=[{"symbol": "MOTHERSON", "name": "Samvardhana Motherson", "sector": "Auto"}],
        )
        self.assertIn("you currently have 1 portfolio stocks", response.lower())

    def test_typo_in_compare_is_handled(self):
        from apps.assistant_module.services import PersonalAssistantService

        holdings = [
            {"symbol": "ACC", "name": "ACC Ltd.", "sector": "Cement"},
            {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Ltd.", "sector": "Auto"},
        ]
        response = PersonalAssistantService()._direct_reply(
            user=None,
            message="compre ACC and Bajaj auto",
            holdings=holdings,
        )
        self.assertIn("recognized acc and bajaj-auto", response.lower())


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
