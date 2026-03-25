from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory

from apps.auth_module.models import TelegramLinkSession, User
from apps.auth_module.views import TelegramLinkSignupCompleteView


@override_settings(
    TELEGRAM_BOT_USERNAME="otp_provider_bot",
    TELEGRAM_WEBHOOK_SECRET="secret-123",
    TELEGRAM_SIGNUP_LINK_EXPIRY_SECONDS=900,
)
class TelegramSignupLinkingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()

    def test_create_link_session(self):
        response = self.client.post("/api/auth/signup/telegram-link/session", {}, format="json")
        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        self.assertIn("session_token", response.data)
        self.assertIn("deep_link", response.data)
        self.assertTrue(
            TelegramLinkSession.objects.filter(token=response.data["session_token"], status="pending").exists()
        )

    @patch("apps.shared.services.telegram_notification_service.requests.post")
    def test_webhook_links_session(self, mocked_post):
        session = TelegramLinkSession.objects.create(
            token="link-token-123456",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        response = self.client.post(
            "/api/auth/telegram/webhook",
            {
                "message": {
                    "text": "/start link-token-123456",
                    "chat": {"id": 1092192986, "type": "private"},
                    "from": {"id": 1092192986, "username": "Geetbidwai"},
                }
            },
            format="json",
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="secret-123",
        )
        self.assertEqual(response.status_code, 200)
        session.refresh_from_db()
        self.assertEqual(session.status, "linked")
        self.assertEqual(session.telegram_chat_id, "1092192986")
        self.assertEqual(session.telegram_username, "Geetbidwai")
        mocked_post.assert_called()

    def test_status_marks_expired_session(self):
        session = TelegramLinkSession.objects.create(
            token="expired-token-123456",
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        response = self.client.get(f"/api/auth/signup/telegram-link/status/{session.token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "expired")

    @patch("apps.shared.services.telegram_notification_service.requests.post")
    def test_complete_signup_with_linked_session(self, mocked_post):
        session = TelegramLinkSession.objects.create(
            token="complete-token-123456",
            status="linked",
            telegram_chat_id="1092192986",
            telegram_username="Geetbidwai",
            telegram_user_id=1092192986,
            linked_at=timezone.now(),
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        request = self.factory.post(
            "/api/auth/signup/telegram-link/complete",
            {
                "session_token": session.token,
                "username": "linkeduser",
                "email": "linked@example.com",
                "password": "StrongPass123!",
                "first_name": "Linked",
                "last_name": "User",
                "mobile_number": "9322428116",
            },
            format="json",
        )
        response = TelegramLinkSignupCompleteView.as_view()(request)
        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        user = User.objects.get(username="linkeduser")
        self.assertEqual(user.profile.telegram_chat_id, "1092192986")
        self.assertEqual(user.profile.telegram_username, "Geetbidwai")
        self.assertEqual(user.profile.mobile_number, "9322428116")
        session.refresh_from_db()
        self.assertEqual(session.status, "consumed")
        self.assertIsNotNone(session.consumed_at)

    def test_cannot_complete_reused_session(self):
        session = TelegramLinkSession.objects.create(
            token="used-token-123456",
            status="consumed",
            telegram_chat_id="1092192986",
            expires_at=timezone.now() + timedelta(minutes=10),
            consumed_at=timezone.now(),
        )
        request = self.factory.post(
            "/api/auth/signup/telegram-link/complete",
            {
                "session_token": session.token,
                "username": "anotheruser",
                "email": "another@example.com",
                "password": "StrongPass123!",
                "mobile_number": "9999999999",
            },
            format="json",
        )
        response = TelegramLinkSignupCompleteView.as_view()(request)
        self.assertEqual(response.status_code, 400, getattr(response, "data", None))
