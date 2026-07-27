#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import smtplib
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def http_check(base_url: str, path: str, timeout: float) -> dict:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    started = time.perf_counter()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ALO186-Production-Synthetic/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            return {
                "name": f"http:{path}",
                "ok": response.status == 200,
                "status": response.status,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "final_url": response.geturl(),
                "body_preview": body[:300],
            }
    except urllib.error.HTTPError as exc:
        return {
            "name": f"http:{path}",
            "ok": False,
            "status": exc.code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover - ağ koşuluna bağlı
        return {
            "name": f"http:{path}",
            "ok": False,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": f"{type(exc).__name__}: {exc}",
        }


def dns_check(host: str) -> dict:
    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
        return {"name": "dns", "ok": bool(addresses), "host": host, "addresses": addresses}
    except Exception as exc:  # pragma: no cover - ağ koşuluna bağlı
        return {"name": "dns", "ok": False, "host": host, "error": f"{type(exc).__name__}: {exc}"}


def tls_check(host: str, port: int, timeout: float, min_days: int) -> dict:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=timeout) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert()
        expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        remaining = (expires - datetime.now(timezone.utc)).total_seconds() / 86400
        return {
            "name": "tls",
            "ok": remaining >= min_days,
            "host": host,
            "expires_at": expires.isoformat(),
            "days_remaining": round(remaining, 1),
            "issuer": dict(item[0] for item in cert.get("issuer", [])),
        }
    except Exception as exc:  # pragma: no cover - ağ koşuluna bağlı
        return {"name": "tls", "ok": False, "host": host, "error": f"{type(exc).__name__}: {exc}"}


def smtp_check(host: str | None, port: int, timeout: float) -> dict:
    if not host:
        return {"name": "smtp", "ok": True, "skipped": True, "reason": "SMTP host tanımlı değil"}
    try:
        with smtplib.SMTP(host, port, timeout=timeout) as client:
            code, _ = client.ehlo()
            if code >= 400:
                raise RuntimeError(f"EHLO başarısız: {code}")
            client.starttls(context=ssl.create_default_context())
            code, _ = client.ehlo()
        return {"name": "smtp", "ok": code < 400, "host": host, "port": port, "starttls": True}
    except Exception as exc:  # pragma: no cover - ağ koşuluna bağlı
        return {"name": "smtp", "ok": False, "host": host, "port": port, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="ALO186 API DNS/TLS/health/SMTP sentetik kontrolü")
    parser.add_argument("--base-url", default="https://api.alo186.com")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--min-tls-days", type=int, default=21)
    parser.add_argument("--smtp-host")
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--output")
    args = parser.parse_args()

    parsed = urllib.parse.urlparse(args.base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise SystemExit("--base-url geçerli bir HTTPS URL olmalıdır.")

    checks = [
        dns_check(parsed.hostname),
        tls_check(parsed.hostname, parsed.port or 443, args.timeout, args.min_tls_days),
        http_check(args.base_url, "/health/live", args.timeout),
        http_check(args.base_url, "/health/ready", args.timeout),
        smtp_check(args.smtp_host, args.smtp_port, args.timeout),
    ]
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
