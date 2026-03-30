from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path


class AssistantKnowledgeService:
    MIN_MATCH_SCORE = 0.58

    def __init__(self):
        self._knowledge_items = self._load_knowledge_items()

    def answer(self, message: str, context: dict | None = None) -> str | None:
        normalized_message = self._normalize(message)
        if not normalized_message:
            return None

        message_tokens = set(normalized_message.split())
        best_item = None
        best_score = 0.0

        for item in self._knowledge_items:
            item_score = max(
                (self._score_question(normalized_message, message_tokens, question) for question in item["questions"]),
                default=0.0,
            )
            if item_score > best_score:
                best_item = item
                best_score = item_score

        if not best_item or best_score < self.MIN_MATCH_SCORE:
            return None

        return self._render_template(best_item["answer"], context or {})

    def _score_question(self, normalized_message: str, message_tokens: set[str], question: str) -> float:
        question_tokens = set(question.split())
        if not question_tokens:
            return 0.0

        overlap_score = len(message_tokens & question_tokens) / len(question_tokens)
        containment_bonus = 0.2 if question in normalized_message or normalized_message in question else 0.0
        return min(overlap_score + containment_bonus, 1.0)

    def _render_template(self, template: str, context: dict) -> str:
        def replace(match):
            key = match.group(1)
            value = context.get(key)
            if value not in (None, ""):
                return str(value)
            return self._fallback_value(key)

        return re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", replace, template)

    def _fallback_value(self, key: str) -> str:
        fallback_map = {
            "username": "there",
            "portfolio_count": "0",
            "portfolio_symbols": "no stocks yet",
            "top_sector": "Unassigned",
            "risk_low_count": "0",
            "risk_medium_count": "0",
            "risk_high_count": "0",
            "top_gainer_symbol": "N/A",
            "top_gainer_change_pct": "0",
            "top_loser_symbol": "N/A",
            "top_loser_change_pct": "0",
        }
        return fallback_map.get(key, "not available")

    def _load_knowledge_items(self) -> list[dict]:
        return list(_load_knowledge_items())

    def _normalize(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


@lru_cache(maxsize=1)
def _load_knowledge_items() -> tuple[dict, ...]:
    data_dir = Path(__file__).resolve().parent / "data"
    file_paths = [data_dir / "knowledge_base.json", data_dir / "tailored_faqs.json"]
    items: list[dict] = []

    for file_path in file_paths:
        if not file_path.exists():
            continue
        raw_items = json.loads(file_path.read_text(encoding="utf-8"))
        for raw_item in raw_items:
            normalized_item = _normalize_item(raw_item)
            if normalized_item:
                items.append(normalized_item)

    return tuple(items)


def _normalize_item(raw_item: dict) -> dict | None:
    answer = str(raw_item.get("answer") or "").strip()
    questions = raw_item.get("questions") or []
    content = str(raw_item.get("content") or "").strip()

    if not answer and content.startswith("Question:") and "\nAnswer:" in content:
        question_part, answer_part = content.split("\nAnswer:", 1)
        answer = answer_part.strip()
        questions = [question_part.replace("Question:", "").strip()]

    if not answer:
        return None

    normalized_questions = []
    for question in questions:
        normalized = re.sub(r"[^a-z0-9]+", " ", str(question or "").lower()).strip()
        if normalized:
            normalized_questions.append(normalized)

    if not normalized_questions:
        title = str(raw_item.get("title") or "").strip()
        normalized_title = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
        if normalized_title:
            normalized_questions.append(normalized_title)

    if not normalized_questions:
        return None

    return {
        "questions": tuple(dict.fromkeys(normalized_questions)),
        "answer": answer,
    }
