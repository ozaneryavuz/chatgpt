from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "client_ip_hash",
            "user_id",
            "organization_id",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging() -> None:
    root = logging.getLogger()
    if any(isinstance(handler.formatter, JsonFormatter) for handler in root.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def request_id(value: str | None) -> str:
    if value and 8 <= len(value) <= 80 and all(ch.isalnum() or ch in "-_." for ch in value):
        return value
    return str(uuid.uuid4())


class RequestMetrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._started_at = time.monotonic()
        self._request_count: dict[tuple[str, str, int], int] = defaultdict(int)
        self._duration_sum: dict[tuple[str, str], float] = defaultdict(float)
        self._in_flight = 0
        self._gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}

    def enter(self) -> None:
        with self._lock:
            self._in_flight += 1

    def observe(self, *, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        safe_path = path if len(path) <= 160 else path[:160]
        with self._lock:
            self._request_count[(method, safe_path, int(status_code))] += 1
            self._duration_sum[(method, safe_path)] += max(0.0, duration_seconds)
            self._in_flight = max(0, self._in_flight - 1)

    def set_gauge(self, name: str, value: float, *, labels: dict[str, str] | None = None) -> None:
        if not name.startswith("alo186_") or not all(ch.isalnum() or ch in "_:" for ch in name):
            raise ValueError("Prometheus gauge adı alo186_ ile başlamalı ve güvenli karakterlerden oluşmalıdır.")
        label_tuple = tuple(sorted((str(key), str(item)) for key, item in (labels or {}).items()))
        with self._lock:
            self._gauges[(name, label_tuple)] = float(value)

    def render_prometheus(self) -> str:
        with self._lock:
            lines = [
                "# HELP alo186_uptime_seconds API process uptime in seconds.",
                "# TYPE alo186_uptime_seconds gauge",
                f"alo186_uptime_seconds {time.monotonic() - self._started_at:.3f}",
                "# HELP alo186_http_requests_in_flight Requests currently being processed.",
                "# TYPE alo186_http_requests_in_flight gauge",
                f"alo186_http_requests_in_flight {self._in_flight}",
                "# HELP alo186_http_requests_total Total HTTP requests.",
                "# TYPE alo186_http_requests_total counter",
            ]
            for (method, path, status_code), count in sorted(self._request_count.items()):
                lines.append(
                    f'alo186_http_requests_total{{method="{_escape(method)}",path="{_escape(path)}",status="{status_code}"}} {count}'
                )
            lines.extend(
                [
                    "# HELP alo186_http_request_duration_seconds_sum Cumulative request duration.",
                    "# TYPE alo186_http_request_duration_seconds_sum counter",
                ]
            )
            for (method, path), duration in sorted(self._duration_sum.items()):
                lines.append(
                    f'alo186_http_request_duration_seconds_sum{{method="{_escape(method)}",path="{_escape(path)}"}} {duration:.6f}'
                )
            emitted_types: set[str] = set()
            for (name, labels), value in sorted(self._gauges.items()):
                if name not in emitted_types:
                    lines.append(f"# HELP {name} ALO186 application gauge.")
                    lines.append(f"# TYPE {name} gauge")
                    emitted_types.add(name)
                label_text = ""
                if labels:
                    label_text = "{" + ",".join(f'{key}="{_escape(item)}"' for key, item in labels) + "}"
                lines.append(f"{name}{label_text} {value:.6f}")
            return "\n".join(lines) + "\n"


def _escape(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


metrics = RequestMetrics()
