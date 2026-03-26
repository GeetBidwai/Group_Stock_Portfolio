from __future__ import annotations

import logging
import os
import time

import requests


logger = logging.getLogger(__name__)


class OllamaLLMService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3").strip()
        self.timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "18"))
        self.max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))

    def generate_response(self, prompt: str) -> str | None:
        if not prompt.strip():
            return None

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        }

        attempt = 0
        while attempt <= self.max_retries:
            try:
                response = requests.post(url, json=payload, timeout=self.timeout_seconds)
                if response.status_code >= 400:
                    logger.warning("Ollama response status=%s on attempt=%s", response.status_code, attempt + 1)
                else:
                    body = response.json()
                    answer = str(body.get("response") or "").strip()
                    if answer:
                        return answer
            except requests.RequestException:
                logger.warning("Ollama request failed on attempt=%s", attempt + 1, exc_info=True)

            attempt += 1
            if attempt <= self.max_retries:
                time.sleep(min(0.75 * attempt, 2.0))

        return None
