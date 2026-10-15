"""Embedding provider abstraction — mock vectors now, real models later."""

from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

from app.core.config import get_settings

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic bag-of-hashed-tokens vectors (no external API / pgvector)."""

    def __init__(self, *, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    @property
    def model_name(self) -> str:
        return f"mock-hash-v1-d{self.dimensions}"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = TOKEN_RE.findall(text.lower())
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign
        # L2 normalize for cosine similarity
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    provider = getattr(settings, "embedding_provider", "mock")
    if str(provider).lower() == "mock":
        return MockEmbeddingProvider()
    return MockEmbeddingProvider()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True))
