"""In-memory sliding-window rate limiter (Redis-backed later)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    def allow(self, key: str, *, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Return (allowed, remaining)."""
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False, 0
            bucket.append(now)
            remaining = max(limit - len(bucket), 0)
            return True, remaining


rate_limiter = InMemoryRateLimiter()
