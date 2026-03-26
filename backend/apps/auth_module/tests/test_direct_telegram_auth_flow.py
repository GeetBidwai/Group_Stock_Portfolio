from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.auth_module.models import PasswordResetOTP, User


@override_settings(
    TELEGRAM_BOT_TOKEN="test-bot-token",
    TELEGRAM_OTP_EXPIRY_SECONDS=300,
    TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS=60,
    PASSWORD_RESET_TOKEN_EXPIRY_SECONDS=600,
)
class DirectTelegramAuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_requires_telegram_chat_id_and_persists_contact_fields(self):
        response = self.client.post(
            "/api/auth/signup",
            {
                "username": "directuser",
                "email": "direct@example.com",
                "password": "StrongPass123!",
                "first_name": "Direct",
                "last_name": "User",
                "mobile_number": "9876543210",
                "telegram_chat_id": "1092192986",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        user = User.objects.get(username="directuser")
        self.assertEqual(user.phone_number, "9876543210")
        self.assertEqual(user.telegram_chat_id, 1092192986)
        self.assertEqual(user.profile.mobile_number, "9876543210")
        self.assertEqual(user.profile.telegram_chat_id, "1092192986")

    @override_settings(TELEGRAM_BOT_TOKEN="", DEBUG=False)
    def test_request_otp_returns_validation_error_when_bot_is_not_configured(self):
        user = User.objects.create_user(
            username="notokenuser",
            email="notoken@example.com",
            password="OldPass123!",
            phone_number="9123456789",
            telegram_chat_id=6181873958,
        )
        user.profile.mobile_number = "9123456789"
        user.profile.telegram_chat_id = "6181873958"
        user.profile.save(update_fields=["mobile_number", "telegram_chat_id"])

        response = self.client.post(
            "/api/auth/request-otp",
            {"phone_number": "9123456789", "telegram_chat_id": "6181873958"},
            format="json",
        )

        self.assertEqual(response.status_code, 400, getattr(response, "data", None))
        self.assertIn("Telegram OTP service is not configured", str(response.data))

    @override_settings(TELEGRAM_BOT_TOKEN="", DEBUG=True)
    def test_request_otp_returns_debug_preview_when_bot_is_not_configured_in_debug(self):
        user = User.objects.create_user(
            username="debugotpuser",
            email="debugotp@example.com",
            password="OldPass123!",
            phone_number="9234567890",
            telegram_chat_id=6181873958,
        )
        user.profile.mobile_number = "9234567890"
        user.profile.telegram_chat_id = "6181873958"
        user.profile.save(update_fields=["mobile_number", "telegram_chat_id"])

        response = self.client.post(
            "/api/auth/request-otp",
            {"phone_number": "9234567890", "telegram_chat_id": "6181873958"},
            format="json",
        )

        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.assertEqual(response.data["delivery_method"], "debug_preview")
        self.assertEqual(len(response.data["otp_preview"]), 6)

    @patch("apps.shared.services.telegram_notification_service.requests.post")
    def test_request_verify_and_reset_password_with_phone_and_chat_id(self, mocked_post):
        user = User.objects.create_user(
            username="otpuser",
            email="otp@example.com",
            password="OldPass123!",
            phone_number="9876543210",
            telegram_chat_id=1092192986,
        )
        user.profile.mobile_number = "9876543210"
        user.profile.telegram_chat_id = "1092192986"
        user.profile.save(update_fields=["mobile_number", "telegram_chat_id"])

        request_response = self.client.post(
            "/api/auth/request-otp",
            {"phone_number": "9876543210", "telegram_chat_id": "1092192986"},
            format="json",
        )
        self.assertEqual(request_response.status_code, 200, getattr(request_response, "data", None))
        self.assertEqual(request_response.data["phone_number"], "9876543210")
        mocked_post.assert_called()

        otp_record = PasswordResetOTP.objects.get(user=user)
        verify_response = self.client.post(
            "/api/auth/verify-otp",
            {"phone_number": "9876543210", "otp_code": "000000"},
            format="json",
        )
        self.assertEqual(verify_response.status_code, 400)

        with patch("apps.auth_module.services.OTPService.hash_code", return_value=otp_record.otp_hash):
            verify_response = self.client.post(
                "/api/auth/verify-otp",
                {"phone_number": "9876543210", "otp_code": "123456"},
                format="json",
            )
        self.assertEqual(verify_response.status_code, 200, getattr(verify_response, "data", None))
        self.assertTrue(verify_response.data["verified"])

        reset_response = self.client.post(
            "/api/auth/reset-password",
            {"phone_number": "9876543210", "new_password": "NewPass123!"},
            format="json",
        )
        self.assertEqual(reset_response.status_code, 200, getattr(reset_response, "data", None))
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPass123!"))

    @patch("apps.shared.services.telegram_notification_service.requests.post")
    def test_request_otp_accepts_mobile_with_country_code_prefix(self, mocked_post):
        user = User.objects.create_user(
            username="countryprefixuser",
            email="countryprefix@example.com",
            password="OldPass123!",
            phone_number="919322428116",
            telegram_chat_id=6181873958,
        )
        user.profile.mobile_number = "919322428116"
        user.profile.telegram_chat_id = "6181873958"
        user.profile.save(update_fields=["mobile_number", "telegram_chat_id"])

        response = self.client.post(
            "/api/auth/request-otp",
            {"phone_number": "9322428116", "telegram_chat_id": "6181873958"},
            format="json",
        )

        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.assertEqual(response.data["phone_number"], "919322428116")
        mocked_post.assert_called()
