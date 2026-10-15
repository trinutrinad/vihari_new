"""Text chunking helpers for RAG ingest."""

from __future__ import annotations

import re

WHITESPACE_RE = re.compile(r"\s+")
PARAGRAPH_RE = re.compile(r"\n\s*\n+")


def estimate_token_count(text: str) -> int:
    return max(len(WHITESPACE_RE.split(text.strip())), 1) if text.strip() else 0


def chunk_text(text: str, *, max_chars: int = 480, overlap: int = 60) -> list[str]:
    """Split text into overlapping chunks suitable for mock retrieval."""
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    paragraphs = [part.strip() for part in PARAGRAPH_RE.split(cleaned) if part.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            units.append(paragraph)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        buffer = ""
        for sentence in sentences:
            candidate = f"{buffer} {sentence}".strip() if buffer else sentence
            if len(candidate) <= max_chars:
                buffer = candidate
            else:
                if buffer:
                    units.append(buffer)
                if len(sentence) <= max_chars:
                    buffer = sentence
                else:
                    for start in range(0, len(sentence), max_chars - overlap):
                        units.append(sentence[start : start + max_chars].strip())
                    buffer = ""
        if buffer:
            units.append(buffer)

    chunks: list[str] = []
    for unit in units:
        if not chunks:
            chunks.append(unit)
            continue
        previous = chunks[-1]
        if len(previous) + 1 + len(unit) <= max_chars:
            chunks[-1] = f"{previous}\n\n{unit}"
        else:
            if overlap > 0 and len(previous) > overlap:
                prefix = previous[-overlap:].strip()
                merged = f"{prefix} {unit}".strip()
                chunks.append(merged[:max_chars])
            else:
                chunks.append(unit)
    return [chunk for chunk in chunks if chunk]
