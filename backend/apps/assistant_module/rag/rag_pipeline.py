from __future__ import annotations

import logging
import os
import threading
from functools import lru_cache

from apps.assistant_module.rag.embedding_service import GeminiEmbeddingService
from apps.assistant_module.rag.indexer import AssistantKnowledgeIndexer
from apps.assistant_module.rag.llm_service import OllamaLLMService
from apps.assistant_module.rag.vector_store import AssistantVectorStore


logger = logging.getLogger(__name__)


class AssistantRAGPipeline:
    def __init__(self):
        self.enabled = os.getenv("ASSISTANT_RAG_ENABLED", "false").strip().lower() == "true"
        self.embedding_service = GeminiEmbeddingService()
        self.vector_store = AssistantVectorStore()
        self.llm_service = OllamaLLMService()
        self.indexer = AssistantKnowledgeIndexer()
        self._index_lock = threading.Lock()
        self._indexed = False

    def ask(self, *, message: str, history: list[dict] | None = None) -> dict | None:
        if not self.enabled:
            return None

        query = (message or "").strip()
        if not query:
            return None

        if not self.embedding_service.available:
            logger.warning("Assistant RAG unavailable: GEMINI_API_KEY missing.")
            return None

        if not self.ensure_index():
            return None

        query_vectors = self.embedding_service.embed_texts([query])
        if not query_vectors or not query_vectors[0]:
            return None

        results = self.vector_store.similarity_search(query_vectors[0], top_k=3)
        if not results:
            return {"reply": "I don't have enough information.", "mode": "rag"}

        context_blocks = []
        good_hits = 0
        for row in results:
            text = str(row.get("text") or "").strip()
            metadata = row.get("metadata") or {}
            title = str(metadata.get("title") or "Context")
            source = str(metadata.get("source") or "knowledge_base")
            distance = float(row.get("score") or 1.0)
            if text:
                context_blocks.append(
                    f"[Title: {title}] [Source: {source}] [Distance: {distance:.4f}]\n{text}"
                )
                if distance < 0.7:
                    good_hits += 1

        if not context_blocks or good_hits == 0:
            return {"reply": "I don't have enough information.", "mode": "rag"}

        prompt = self._build_prompt(
            question=query,
            history=history or [],
            context="\n\n".join(context_blocks),
        )
        llm_reply = self.llm_service.generate_response(prompt)
        if not llm_reply:
            return None
        return {"reply": llm_reply.strip(), "mode": "rag"}

    def ensure_index(self) -> bool:
        existing_count = self.vector_store.count()
        if existing_count > 0:
            self._indexed = True
            return True

        if self._indexed and self.vector_store.count() > 0:
            return True

        with self._index_lock:
            existing_count = self.vector_store.count()
            if existing_count > 0:
                self._indexed = True
                return True

            if self._indexed and self.vector_store.count() > 0:
                return True

            chunks = self.indexer.build_chunks()
            if not chunks:
                logger.warning("Assistant RAG indexing skipped: no chunks available.")
                return False

            documents = [
                {
                    "id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                }
                for chunk in chunks
            ]
            embeddings = self.embedding_service.embed_texts([item["text"] for item in documents])
            inserted = self.vector_store.add_documents(documents, embeddings)
            self._indexed = inserted > 0 and self.vector_store.count() > 0

            if not self._indexed:
                logger.warning("Assistant RAG indexing did not insert documents.")
            return self._indexed

    def reindex(self) -> dict:
        if not self.enabled:
            return {"ok": False, "message": "Assistant RAG is disabled.", "indexed_chunks": 0}
        if not self.embedding_service.available:
            return {"ok": False, "message": "GEMINI_API_KEY is not configured.", "indexed_chunks": 0}

        with self._index_lock:
            self.vector_store.clear()
            self._indexed = False
            chunks = self.indexer.build_chunks()
            documents = [
                {
                    "id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                }
                for chunk in chunks
            ]
            embeddings = self.embedding_service.embed_texts([item["text"] for item in documents])
            inserted = self.vector_store.add_documents(documents, embeddings)
            self._indexed = inserted > 0
            return {
                "ok": self._indexed,
                "message": "Reindex completed." if self._indexed else "No chunks indexed.",
                "indexed_chunks": inserted,
                "total_vectors": self.vector_store.count(),
            }

    def _build_prompt(self, *, question: str, history: list[dict], context: str) -> str:
        history_lines = []
        for row in history[-6:]:
            role = str(row.get("role") or "").strip().lower()
            content = str(row.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                history_lines.append(f"{role}: {content}")
        history_block = "\n".join(history_lines) if history_lines else "No prior conversation."

        return (
            "You are an intelligent assistant for the Stock Analytics Platform.\n"
            "Use ONLY the provided context to answer.\n"
            "If the answer is not in context, respond exactly: I don't have enough information.\n"
            "Never invent project features.\n\n"
            f"Conversation History:\n{history_block}\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )


@lru_cache(maxsize=1)
def get_assistant_rag_pipeline() -> AssistantRAGPipeline:
    return AssistantRAGPipeline()
