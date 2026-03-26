from __future__ import annotations

import json
import logging
from pathlib import Path

from django.conf import settings

from apps.assistant_module.utils.text_chunking import TextChunk, chunk_documents


logger = logging.getLogger(__name__)


class AssistantKnowledgeIndexer:
    CHUNK_SIZE_WORDS = 400
    CHUNK_OVERLAP_WORDS = 50

    def __init__(self):
        self.backend_dir = Path(settings.BASE_DIR)
        self.project_dir = self.backend_dir.parent
        self.assistant_dir = self.backend_dir / "apps" / "assistant_module"
        self.knowledge_base_path = self.assistant_dir / "data" / "knowledge_base.json"

    def load_documents(self) -> list[dict]:
        documents: list[dict] = []

        documents.extend(self._load_knowledge_base())
        documents.extend(
            self._load_file_documents(
                [
                    (self.project_dir / "README.md", "Project README"),
                    (self.project_dir / "docs" / "API.md", "API Guide"),
                    (self.project_dir / "docs" / "ModuleCustomizationGuide.md", "Module Customization"),
                ]
            )
        )

        seen: set[str] = set()
        deduped: list[dict] = []
        for item in documents:
            fingerprint = f"{item.get('title')}::{item.get('content')}"
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            deduped.append(item)
        return deduped

    def build_chunks(self) -> list[TextChunk]:
        documents = self.load_documents()
        return chunk_documents(
            documents,
            chunk_size_words=self.CHUNK_SIZE_WORDS,
            overlap_words=self.CHUNK_OVERLAP_WORDS,
        )

    def _load_knowledge_base(self) -> list[dict]:
        if not self.knowledge_base_path.exists():
            logger.warning("Assistant knowledge base file missing: %s", self.knowledge_base_path)
            return []

        try:
            payload = json.loads(self.knowledge_base_path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Failed to parse assistant knowledge base JSON")
            return []

        if not isinstance(payload, list):
            return []

        documents: list[dict] = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or f"Knowledge {index + 1}").strip()
            content = str(item.get("content") or "").strip()
            source = str(item.get("source") or "assistant_module/data/knowledge_base.json")
            if not content:
                continue
            documents.append(
                {
                    "id": str(item.get("id") or f"kb-{index + 1}"),
                    "title": title,
                    "content": content,
                    "source": source,
                }
            )
        return documents

    def _load_file_documents(self, files: list[tuple[Path, str]]) -> list[dict]:
        documents: list[dict] = []
        for path, title in files:
            if not path.exists():
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore").strip()
            except Exception:
                logger.warning("Unable to read assistant RAG source file: %s", path, exc_info=True)
                continue

            if not content:
                continue

            documents.append(
                {
                    "id": f"file-{path.name.lower().replace('.', '-')}",
                    "title": title,
                    "content": content,
                    "source": str(path),
                }
            )
        return documents
