#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    latency_ms: float | None = None


def dns_check(host: str) -> Check:
    started = dt.datetime.now(dt.timezone.utc)
    try:
        addresses = sorted({row[4][0] for row in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
        latency = (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
        return Check("dns", bool(addresses), ", ".join(addresses), latency)
    except OSError as exc:
        return Check("dns", False, str(exc))


def tls_check(host: str, minimum_days: int) -> Check:
    context = ssl.create_default_context()
    started = dt.datetime.now(dt.timezone.utc)
    try:
        with socket.create_connection((host, 443), timeout=15) as raw:
            with context.wrap_socket(raw, server_hostname=host) as secure:
                cert = secure.getpeercert()
                expires = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
                    tzinfo=dt.timezone.utc
                )
                remaining = expires - dt.datetime.now(dt.timezone.utc)
                sans = {value for kind, value in cert.get("subjectAltName", []) if kind == "DNS"}
                latency = (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
                ok = remaining.days >= minimum_days and host in sans
                return Check(
                    "tls",
                    ok,
                    f"expires={expires.isoformat()} remaining_days={remaining.days} san_match={host in sans}",
                    latency,
                )
    except (OSError, ssl.SSLError, KeyError, ValueError) as exc:
        return Check("tls", False, str(exc))


def http_check(base_url: str, path: str, expected_status: int = 200) -> Check:
    url = base_url.rstrip("/") + path
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ALO186-Production-Probe/1.0", "Accept": "application/json"},
    )
    started = dt.datetime.now(dt.timezone.utc)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read(128_000)
            latency = (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
            headers = {key.lower(): value for key, value in response.headers.items()}
            security = all(
                key in headers
                for key in ("x-content-type-options", "x-frame-options", "referrer-policy", "x-request-id")
            )
            parsed = None
            try:
                parsed = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass
            status_ok = response.status == expected_status
            body_ok = isinstance(parsed, dict) and parsed.get("status") in {"ok", "ready"}
            return Check(
                f"http:{path}",
                status_ok and body_ok and security,
                f"status={response.status} body_status={parsed.get('status') if isinstance(parsed, dict) else None} security_headers={security}",
                latency,
            )
    except urllib.error.HTTPError as exc:
        return Check(f"http:{path}", False, f"HTTP {exc.code}: {exc.reason}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return Check(f"http:{path}", False, str(exc))


def dig_txt(name: str) -> list[str]:
    try:
        process = subprocess.run(
            ["dig", "+short", "TXT", name],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip().replace('"', "") for line in process.stdout.splitlines() if line.strip()]


def email_dns_checks(domain: str) -> list[Check]:
    spf = [value for value in dig_txt(domain) if "v=spf1" in value.lower()]
    dmarc = dig_txt(f"_dmarc.{domain}")
    return [
        Check("email-dns:spf", len(spf) == 1, f"spf_records={len(spf)}"),
        Check(
            "email-dns:dmarc",
            any("v=DMARC1" in value.upper() for value in dmarc),
            "present" if dmarc else "missing",
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 API DNS, TLS, health ve e-posta DNS probe")
    parser.add_argument("--base-url", default="https://api.alo186.com")
    parser.add_argument("--minimum-tls-days", type=int, default=21)
    parser.add_argument("--email-domain", default="alo186.com")
    parser.add_argument("--check-email-dns", action="store_true")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()

    parsed = urlparse(args.base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise SystemExit("--base-url HTTPS olmalıdır.")

    checks = [
        dns_check(parsed.hostname),
        tls_check(parsed.hostname, args.minimum_tls_days),
        http_check(args.base_url, "/health/live"),
        http_check(args.base_url, "/health/ready"),
    ]
    if args.check_email_dns:
        checks.extend(email_dns_checks(args.email_domain))

    report = {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "base_url": args.base_url,
        "ok": all(check.ok for check in checks),
        "checks": [asdict(check) for check in checks],
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json_out:
        target = Path(args.json_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
