import os

import requests


class DatabricksSentimentClient:
    def __init__(self):
        self.endpoint = os.getenv("DATABRICKS_SENTIMENT_URL", "").strip()
        self.token = os.getenv("DATABRICKS_TOKEN", "").strip()
        self.timeout = int(os.getenv("DATABRICKS_TIMEOUT_SECONDS", "10"))

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.token)

    def get_sentiment(self, text: str) -> dict:
        if not self.is_configured():
            raise RuntimeError("Databricks sentiment endpoint is not configured.")

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"text": text},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        label = payload.get("label") or payload.get("sentiment")
        score = payload.get("score")

        if label is None or score is None:
            raise RuntimeError("Databricks sentiment response is missing label or score.")

        return {
            "label": str(label).title(),
            "score": float(score),
        }

