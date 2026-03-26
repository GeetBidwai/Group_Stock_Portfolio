from __future__ import annotations

import logging
import os
from functools import lru_cache

import requests


logger = logging.getLogger(__name__)


@lru_cache(maxsize=2048)
def _embed_single_cached(
    api_key: str,
    model: str,
    text: str,
    timeout_seconds: int,
) -> tuple[float, ...] | None:
    if not api_key or not text:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"
    params = {"key": api_key}
    payload = {"content": {"parts": [{"text": text}]}}
    try:
        response = requests.post(url, params=params, json=payload, timeout=timeout_seconds)
        if response.status_code >= 400:
            logger.warning("Gemini embedding call failed with status=%s", response.status_code)
            return None
        body = response.json()
        values = body.get("embedding", {}).get("values") or []
        if not values:
            return None
        return tuple(float(value) for value in values)
    except requests.RequestException:
        logger.warning("Gemini embedding request failed", exc_info=True)
        return None


class GeminiEmbeddingService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004").strip()
        self.timeout_seconds = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "12"))

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.available:
            return []

        vectors: list[list[float]] = []
        for raw_text in texts:
            text = (raw_text or "").strip()
            if not text:
                vectors.append([])
                continue

            vector = _embed_single_cached(
                self.api_key,
                self.model,
                text,
                self.timeout_seconds,
            )
            vectors.append(list(vector) if vector else [])
        return vectors
