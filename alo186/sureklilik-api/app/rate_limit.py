from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import HTTPException, Request, status

from .config import settings
from .security import hash_client_value


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, *, limit: int, window_seconds: int, now: float | None = None) -> RateLimitResult:
        current = time.monotonic() if now is None else float(now)
        threshold = current - window_seconds
        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] <= threshold:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = max(1, int(window_seconds - (current - bucket[0])))
                return RateLimitResult(False, 0, retry_after)
            bucket.append(current)
            remaining = max(0, limit - len(bucket))
            return RateLimitResult(True, remaining, 0)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


global_limiter = SlidingWindowLimiter()
auth_limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def rate_key(request: Request, namespace: str, identity: str | None = None) -> str:
    raw = f"{namespace}:{client_ip(request)}:{identity or ''}"
    return hash_client_value(raw) or raw


def check_global_rate(request: Request) -> RateLimitResult:
    return global_limiter.check(
        rate_key(request, "global"),
        limit=settings.global_rate_limit,
        window_seconds=60,
    )


def enforce_auth_rate(request: Request, identity: str | None = None) -> None:
    result = auth_limiter.check(
        rate_key(request, "auth", (identity or "").strip().lower()),
        limit=settings.auth_rate_limit,
        window_seconds=settings.rate_limit_window_seconds,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla kimlik doğrulama denemesi. Daha sonra tekrar deneyin.",
            headers={"Retry-After": str(result.retry_after)},
        )
