from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextChunk:
    chunk_id: str
    text: str
    metadata: dict


def chunk_text(
    *,
    text: str,
    title: str,
    source: str,
    base_id: str,
    chunk_size_words: int = 400,
    overlap_words: int = 50,
) -> list[TextChunk]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []

    words = cleaned.split(" ")
    if chunk_size_words <= 0:
        chunk_size_words = 400
    if overlap_words < 0:
        overlap_words = 0
    if overlap_words >= chunk_size_words:
        overlap_words = max(0, chunk_size_words // 4)

    chunks: list[TextChunk] = []
    start = 0
    chunk_number = 0
    total_words = len(words)
    step = max(1, chunk_size_words - overlap_words)

    while start < total_words:
        end = min(total_words, start + chunk_size_words)
        chunk_words = words[start:end]
        if not chunk_words:
            break
        chunk_text_value = " ".join(chunk_words).strip()
        if chunk_text_value:
            chunks.append(
                TextChunk(
                    chunk_id=f"{base_id}-{chunk_number}",
                    text=chunk_text_value,
                    metadata={
                        "title": title,
                        "source": source,
                        "word_start": start,
                        "word_end": end,
                    },
                )
            )
            chunk_number += 1

        if end >= total_words:
            break
        start += step

    return chunks


def chunk_documents(
    documents: list[dict],
    *,
    chunk_size_words: int = 400,
    overlap_words: int = 50,
) -> list[TextChunk]:
    output: list[TextChunk] = []
    for index, document in enumerate(documents):
        title = str(document.get("title") or f"Doc {index + 1}")
        source = str(document.get("source") or "knowledge_base")
        text = str(document.get("content") or "")
        base_id = str(document.get("id") or f"doc-{index + 1}")
        output.extend(
            chunk_text(
                text=text,
                title=title,
                source=source,
                base_id=base_id,
                chunk_size_words=chunk_size_words,
                overlap_words=overlap_words,
            )
        )
    return output
