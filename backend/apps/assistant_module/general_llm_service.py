from __future__ import annotations

import logging
import os
import time

import requests

from apps.assistant_module.rag.llm_service import OllamaLLMService


logger = logging.getLogger(__name__)


class GeneralLLMService:
    def __init__(self):
        self.grok_api_key = os.getenv("GROK_API_KEY", "").strip()
        self.grok_model = os.getenv("GROK_MODEL", "grok-2-latest").strip()
        self.grok_base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1").rstrip("/")
        self.grok_timeout_seconds = int(os.getenv("GROK_TIMEOUT_SECONDS", "20"))
        self.grok_max_retries = int(os.getenv("GROK_MAX_RETRIES", "1"))

    def answer(self, *, message: str, history: list[dict], user_context: dict) -> str | None:
        prompt = self._build_prompt(message=message, history=history, user_context=user_context)

        grok_answer = self._answer_with_grok(prompt)
        if grok_answer:
            return grok_answer

        return OllamaLLMService().generate_response(prompt)

    def _answer_with_grok(self, prompt: str) -> str | None:
        if not self.grok_api_key:
            return None

        url = f"{self.grok_base_url}/chat/completions"
        payload = {
            "model": self.grok_model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the Market Atlas in-app assistant. Answer clearly and briefly. "
                        "Do not invent portfolio holdings, live prices, or product features. "
                        "If the user asks for platform-specific or user-specific data that is not provided, "
                        "say you can guide them to the right module instead."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        attempt = 0
        while attempt <= self.grok_max_retries:
            try:
                response = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self.grok_timeout_seconds,
                )
                if response.status_code >= 400:
                    logger.warning("Grok response status=%s on attempt=%s", response.status_code, attempt + 1)
                else:
                    body = response.json()
                    choices = body.get("choices") or []
                    if choices:
                        message = choices[0].get("message") or {}
                        content = str(message.get("content") or "").strip()
                        if content:
                            return content
            except requests.RequestException:
                logger.warning("Grok request failed on attempt=%s", attempt + 1, exc_info=True)

            attempt += 1
            if attempt <= self.grok_max_retries:
                time.sleep(min(0.75 * attempt, 2.0))

        return None

    def _build_prompt(self, *, message: str, history: list[dict], user_context: dict) -> str:
        history_lines = []
        for item in history[-4:]:
            role = str(item.get("role") or "").strip()
            content = str(item.get("content") or "").strip()
            if role and content:
                history_lines.append(f"{role}: {content}")

        portfolio_symbols = user_context.get("portfolio_symbols") or "none"
        enabled_modules = user_context.get("enabled_modules") or "Stocks, Portfolio, Compare, Risk, Clustering, Forecast, Quality Stocks"

        return (
            "Platform: Market Atlas.\n"
            f"User: {user_context.get('username') or 'there'}.\n"
            f"Portfolio count: {user_context.get('portfolio_count', 0)}.\n"
            f"Portfolio symbols: {portfolio_symbols}.\n"
            f"Enabled modules: {enabled_modules}.\n"
            "Use this context only when directly relevant. Do not make up missing app data.\n"
            f"Recent chat:\n{chr(10).join(history_lines) if history_lines else 'No prior chat.'}\n"
            f"Current user message: {message}"
        )
