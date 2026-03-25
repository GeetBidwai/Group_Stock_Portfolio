from __future__ import annotations

import os
from threading import Lock
from time import time


class FinBERTSentimentClient:
    _pipeline = None
    _lock = Lock()
    _unavailable_until = 0.0

    def __init__(self):
        self.enabled = os.getenv("FINBERT_ENABLED", "true").lower() == "true"
        self.model_name = os.getenv("FINBERT_MODEL_NAME", "ProsusAI/finbert").strip() or "ProsusAI/finbert"
        self.cache_dir = os.getenv("FINBERT_CACHE_DIR", "").strip() or None
        self.local_files_only = os.getenv("FINBERT_LOCAL_FILES_ONLY", "false").lower() == "true"
        self.retry_cooldown_seconds = int(os.getenv("FINBERT_RETRY_COOLDOWN_SECONDS", "600"))

    def is_configured(self) -> bool:
        return self.enabled

    def get_sentiment(self, text: str) -> dict:
        if not self.is_configured():
            raise RuntimeError("FinBERT is disabled.")

        pipeline = self._get_pipeline()
        results = pipeline(text, truncation=True, top_k=None)
        if not results:
            raise RuntimeError("FinBERT returned no sentiment scores.")

        scores = {str(item["label"]).lower(): float(item["score"]) for item in results}
        positive_score = scores.get("positive", 0.0)
        negative_score = scores.get("negative", 0.0)
        neutral_score = scores.get("neutral", 0.0)

        signed_score = max(min(positive_score - negative_score, 1.0), -1.0)
        if neutral_score >= max(positive_score, negative_score):
            label = "Neutral"
        elif positive_score >= negative_score:
            label = "Positive"
        else:
            label = "Negative"

        return {
            "label": label,
            "score": signed_score,
        }

    def _get_pipeline(self):
        if time() < self.__class__._unavailable_until:
            raise RuntimeError("FinBERT is temporarily unavailable.")

        if self.__class__._pipeline is not None:
            return self.__class__._pipeline

        with self.__class__._lock:
            if time() < self.__class__._unavailable_until:
                raise RuntimeError("FinBERT is temporarily unavailable.")

            if self.__class__._pipeline is not None:
                return self.__class__._pipeline

            try:
                from transformers import pipeline  # type: ignore
            except Exception as exc:
                raise RuntimeError("Transformers is not installed for FinBERT.") from exc

            pipeline_kwargs = {
                "task": "text-classification",
                "model": self.model_name,
                "tokenizer": self.model_name,
                "top_k": None,
                "device": -1,
                "local_files_only": self.local_files_only,
            }
            if self.cache_dir:
                pipeline_kwargs["model_kwargs"] = {"cache_dir": self.cache_dir}

            try:
                self.__class__._pipeline = pipeline(
                    pipeline_kwargs.pop("task"),
                    **pipeline_kwargs,
                )
                return self.__class__._pipeline
            except Exception as exc:
                self.__class__._unavailable_until = time() + self.retry_cooldown_seconds
                raise RuntimeError("FinBERT could not be initialized.") from exc
