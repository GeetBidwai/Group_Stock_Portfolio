from __future__ import annotations

import json
import logging
import math
import os
from pathlib import Path

from django.conf import settings


logger = logging.getLogger(__name__)

try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None


class AssistantVectorStore:
    COLLECTION_NAME = "assistant_project_kb"
    MEMORY_CACHE_FILE = "assistant_vectors.json"

    def __init__(self):
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "").strip()
        if persist_dir:
            self.persist_dir = Path(persist_dir)
        else:
            self.persist_dir = Path(settings.BASE_DIR) / ".chroma"
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._use_chroma = chromadb is not None
        self._client = None
        self._collection = None
        self._memory_docs: list[dict] = []
        self._memory_path = self.persist_dir / self.MEMORY_CACHE_FILE

        if self._use_chroma:
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            self._collection = self._client.get_or_create_collection(name=self.COLLECTION_NAME)
        else:
            self._load_memory_store()
            logger.warning("ChromaDB is unavailable. Assistant RAG vector store is using memory fallback.")

    def count(self) -> int:
        if self._use_chroma and self._collection is not None:
            return int(self._collection.count())
        return len(self._memory_docs)

    def clear(self):
        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(where={})
            except Exception:
                logger.warning("Chroma collection clear failed; recreating collection.", exc_info=True)
                if self._client is not None:
                    try:
                        self._client.delete_collection(name=self.COLLECTION_NAME)
                    except Exception:
                        logger.warning("Chroma collection delete failed during reset.", exc_info=True)
                    self._collection = self._client.get_or_create_collection(name=self.COLLECTION_NAME)
            return
        self._memory_docs = []
        self._persist_memory_store()

    def add_documents(self, documents: list[dict], embeddings: list[list[float]]) -> int:
        if not documents:
            return 0

        valid_items: list[dict] = []
        for document, embedding in zip(documents, embeddings):
            if not embedding:
                continue
            valid_items.append(
                {
                    "id": str(document["id"]),
                    "text": str(document["text"]),
                    "metadata": dict(document.get("metadata") or {}),
                    "embedding": [float(value) for value in embedding],
                }
            )

        if not valid_items:
            return 0

        if self._use_chroma and self._collection is not None:
            self._collection.upsert(
                ids=[item["id"] for item in valid_items],
                documents=[item["text"] for item in valid_items],
                metadatas=[item["metadata"] for item in valid_items],
                embeddings=[item["embedding"] for item in valid_items],
            )
            return len(valid_items)

        # In-memory fallback when chromadb package is unavailable.
        existing = {item["id"]: item for item in self._memory_docs}
        for item in valid_items:
            existing[item["id"]] = item
        self._memory_docs = list(existing.values())
        self._persist_memory_store()
        return len(valid_items)

    def similarity_search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        if not query_embedding:
            return []

        top_k = max(1, int(top_k))
        if self._use_chroma and self._collection is not None:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            documents = (results.get("documents") or [[]])[0]
            metadatas = (results.get("metadatas") or [[]])[0]
            distances = (results.get("distances") or [[]])[0]
            output: list[dict] = []
            for text, metadata, distance in zip(documents, metadatas, distances):
                output.append(
                    {
                        "text": text or "",
                        "metadata": metadata or {},
                        "score": float(distance if distance is not None else 1.0),
                    }
                )
            return output

        scored: list[dict] = []
        for item in self._memory_docs:
            score = _cosine_distance(query_embedding, item.get("embedding") or [])
            scored.append(
                {
                    "text": item.get("text") or "",
                    "metadata": item.get("metadata") or {},
                    "score": score,
                }
            )
        scored.sort(key=lambda row: row["score"])
        return scored[:top_k]

    def _load_memory_store(self):
        if not self._memory_path.exists():
            self._memory_docs = []
            return
        try:
            raw = json.loads(self._memory_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                self._memory_docs = [item for item in raw if isinstance(item, dict)]
            else:
                self._memory_docs = []
        except Exception:
            logger.warning("Failed to load assistant vector memory store", exc_info=True)
            self._memory_docs = []

    def _persist_memory_store(self):
        try:
            self._memory_path.parent.mkdir(parents=True, exist_ok=True)
            self._memory_path.write_text(json.dumps(self._memory_docs), encoding="utf-8")
        except Exception:
            logger.warning("Failed to persist assistant vector memory store", exc_info=True)


def _cosine_distance(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 1.0
    if len(a) != len(b):
        return 1.0

    dot = 0.0
    a_norm = 0.0
    b_norm = 0.0
    for av, bv in zip(a, b):
        dot += av * bv
        a_norm += av * av
        b_norm += bv * bv
    if a_norm == 0 or b_norm == 0:
        return 1.0
    cosine_similarity = dot / (math.sqrt(a_norm) * math.sqrt(b_norm))
    return 1.0 - max(-1.0, min(1.0, cosine_similarity))
