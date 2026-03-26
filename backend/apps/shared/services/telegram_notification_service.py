import requests
from django.conf import settings


class TelegramNotificationService:
    def bot_api_url(self, method: str) -> str:
        return f"{settings.TELEGRAM_BOT_API_URL}/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"

    def ensure_configured(self) -> None:
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

    def send_message(self, chat_id: str, message: str) -> None:
        self.ensure_configured()
        url = self.bot_api_url("sendMessage")
        response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
        response.raise_for_status()

    def send_otp(self, chat_id: str, message: str) -> None:
        self.send_message(chat_id, message)

    def get_me(self) -> dict:
        self.ensure_configured()
        response = requests.get(self.bot_api_url("getMe"), timeout=10)
        response.raise_for_status()
        return response.json()
