from __future__ import annotations

import json
import logging
import re
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import Settings


logger = logging.getLogger("alo186.api")
_UUID_SEGMENT = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}$")
_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,128}$")


def route_label(path: str) -> str:
    parts = []
    for item in path.split("/"):
        if not item:
            continue
        parts.append(":id" if _UUID_SEGMENT.match(item) else item)
    return "/" + "/".join(parts)


def client_ip(scope: Scope, trust_proxy_headers: bool) -> str:
    if trust_proxy_headers:
        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        forwarded = headers.get(b"x-forwarded-for", b"").decode("latin-1").split(",", 1)[0].strip()
        if forwarded:
            return forwarded
    client = scope.get("client")
    return str(client[0]) if client else "unknown"


def request_id(scope: Scope) -> str:
    headers = {key.lower(): value for key, value in scope.get("headers", [])}
    incoming = headers.get(b"x-request-id", b"").decode("latin-1").strip()
    return incoming if _REQUEST_ID.match(incoming) else str(uuid.uuid4())


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.requests: dict[tuple[str, str, int], int] = defaultdict(int)
        self.duration_sum: dict[tuple[str, str], float] = defaultdict(float)
        self.duration_count: dict[tuple[str, str], int] = defaultdict(int)
        self.rate_limited: dict[str, int] = defaultdict(int)
        self.body_rejected = 0

    def observe(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        label = route_label(path)
        with self._lock:
            self.requests[(method, label, status_code)] += 1
            self.duration_sum[(method, label)] += duration_seconds
            self.duration_count[(method, label)] += 1

    def observe_rate_limit(self, bucket: str) -> None:
        with self._lock:
            self.rate_limited[bucket] += 1

    def observe_body_rejection(self) -> None:
        with self._lock:
            self.body_rejected += 1

    def render(self) -> str:
        with self._lock:
            lines = [
                "# HELP alo186_http_requests_total HTTP istek sayısı.",
                "# TYPE alo186_http_requests_total counter",
            ]
            for (method, path, status), value in sorted(self.requests.items()):
                lines.append(
                    f'alo186_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {value}'
                )
            lines.extend(
                [
                    "# HELP alo186_http_request_duration_seconds_sum HTTP istek süre toplamı.",
                    "# TYPE alo186_http_request_duration_seconds_sum counter",
                ]
            )
            for (method, path), value in sorted(self.duration_sum.items()):
                lines.append(
                    f'alo186_http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {value:.6f}'
                )
            lines.extend(
                [
                    "# HELP alo186_http_request_duration_seconds_count HTTP istek süre gözlem sayısı.",
                    "# TYPE alo186_http_request_duration_seconds_count counter",
                ]
            )
            for (method, path), value in sorted(self.duration_count.items()):
                lines.append(
                    f'alo186_http_request_duration_seconds_count{{method="{method}",path="{path}"}} {value}'
                )
            lines.extend(
                [
                    "# HELP alo186_rate_limited_total Rate limit ile reddedilen istek sayısı.",
                    "# TYPE alo186_rate_limited_total counter",
                ]
            )
            for bucket, value in sorted(self.rate_limited.items()):
                lines.append(f'alo186_rate_limited_total{{bucket="{bucket}"}} {value}')
            lines.extend(
                [
                    "# HELP alo186_request_body_rejected_total Boyut nedeniyle reddedilen gövde sayısı.",
                    "# TYPE alo186_request_body_rejected_total counter",
                    f"alo186_request_body_rejected_total {self.body_rejected}",
                ]
            )
            return "\n".join(lines) + "\n"


metrics = MetricsRegistry()


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        self.app = app
        self.settings = settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        req_id = request_id(scope)
        status_code = 500
        response_started = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"x-request-id", req_id.encode("ascii")),
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"referrer-policy", b"no-referrer"),
                        (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                        (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'; base-uri 'none'"),
                    ]
                )
                if self.settings.is_production:
                    headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                if scope.get("path", "").startswith("/api/v1/auth/"):
                    headers.append((b"cache-control", b"no-store"))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            if not response_started:
                status_code = 500
            raise
        finally:
            duration = time.perf_counter() - started
            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "")
            metrics.observe(method, path, status_code, duration)
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "request_id": req_id,
                        "method": method,
                        "path": route_label(path),
                        "status": status_code,
                        "duration_ms": round(duration * 1000, 2),
                        "client_ip": client_ip(scope, self.settings.trust_proxy_headers),
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            )


class RequestBodyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    metrics.observe_body_rejection()
                    await JSONResponse(
                        {"detail": "İstek gövdesi izin verilen boyutu aşıyor."},
                        status_code=413,
                    )(scope, receive, send)
                    return
            except ValueError:
                pass

        consumed = 0
        rejected = False

        async def limited_receive() -> Message:
            nonlocal consumed, rejected
            message = await receive()
            if message["type"] == "http.request":
                consumed += len(message.get("body", b""))
                if consumed > self.max_bytes:
                    rejected = True
                    raise _BodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            if rejected:
                metrics.observe_body_rejection()
                await JSONResponse(
                    {"detail": "İstek gövdesi izin verilen boyutu aşıyor."},
                    status_code=413,
                )(scope, receive, send)


class _BodyTooLarge(Exception):
    pass


@dataclass
class _Window:
    events: Deque[float]


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._windows: dict[str, _Window] = {}

    def check(self, key: str, limit: int, now: float | None = None) -> tuple[bool, int]:
        current = now if now is not None else time.monotonic()
        threshold = current - 60.0
        with self._lock:
            window = self._windows.setdefault(key, _Window(events=deque()))
            while window.events and window.events[0] <= threshold:
                window.events.popleft()
            if len(window.events) >= limit:
                retry_after = max(1, int(60.0 - (current - window.events[0])))
                return False, retry_after
            window.events.append(current)
            if len(self._windows) > 10_000:
                self._windows = {
                    item_key: item_value
                    for item_key, item_value in self._windows.items()
                    if item_value.events and item_value.events[-1] > threshold
                }
            return True, 0


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        self.app = app
        self.settings = settings
        self.limiter = SlidingWindowLimiter()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") == "OPTIONS":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return
        auth_bucket = path in {"/api/v1/auth/register", "/api/v1/auth/login"}
        bucket = "auth" if auth_bucket else "api"
        limit = (
            self.settings.auth_rate_limit_per_minute
            if auth_bucket
            else self.settings.api_rate_limit_per_minute
        )
        ip = client_ip(scope, self.settings.trust_proxy_headers)
        allowed, retry_after = self.limiter.check(f"{bucket}:{ip}", limit)
        if not allowed:
            metrics.observe_rate_limit(bucket)
            response = JSONResponse(
                {"detail": "Çok fazla istek gönderildi. Lütfen daha sonra tekrar deneyin."},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
